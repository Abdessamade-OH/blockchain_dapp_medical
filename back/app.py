from flask import Flask, request, jsonify
from web3 import Web3
import json
import os
from dotenv import load_dotenv
from flask_cors import CORS
from connect_doctor import register_doctor
import ipfshttpclient
from cryptography.fernet import Fernet
import base64
from datetime import datetime
import hashlib
import requests
import time
import json
import os
from threading import Lock
import threading
from typing import Optional, Dict, Set, List, Tuple
import base64


# IPFS API configuration
IPFS_API_BASE_URL = 'http://127.0.0.1:5001/api/v0'

# Generate encryption key - in production, this should be managed securely
encryption_key = Fernet.generate_key()
fernet = Fernet(encryption_key)

# Pinata configuration
PINATA_API_KEY = "1d4e98ae316ec67e0147"  # Replace with your actual Pinata API key
PINATA_SECRET_API_KEY = "eee12cb52ec621fd5ca6c4db72b297018aa448d26427d1b4b0d6c0e1b41ec1f9"  # Replace with your actual Pinata secret key
PINATA_BASE_URL = "https://api.pinata.cloud"

class PinataIPFSManager:
    def __init__(self):
        self.headers = {
            'pinata_api_key': PINATA_API_KEY,
            'pinata_secret_api_key': PINATA_SECRET_API_KEY
        }
        
    def pin_to_ipfs(self, content: bytes) -> str:
        """
        Pin content to IPFS using Pinata.
        Returns the IPFS hash (CID) of the pinned content.
        """
        try:
            url = f"{PINATA_BASE_URL}/pinning/pinFileToIPFS"
            files = {
                'file': content
            }
            
            response = requests.post(
                url,
                files=files,
                headers=self.headers
            )
            
            if response.status_code != 200:
                raise Exception(f"Failed to pin to Pinata: {response.text}")
                
            return response.json()['IpfsHash']
            
        except Exception as e:
            raise Exception(f"Pinata pinning error: {str(e)}")
    
    def unpin_from_ipfs(self, ipfs_hash: str) -> bool:
        """
        Unpin content from IPFS using Pinata.
        Returns True if successful, False otherwise.
        """
        try:
            url = f"{PINATA_BASE_URL}/pinning/unpin/{ipfs_hash}"
            response = requests.delete(url, headers=self.headers)
            
            return response.status_code == 200
            
        except Exception as e:
            print(f"Pinata unpinning error: {str(e)}")
            return False
    
    def get_pin_list(self, filters: Optional[Dict] = None) -> List[Dict]:
        """
        Get list of pinned files from Pinata.
        Optional filters can be provided to narrow down results.
        """
        try:
            url = f"{PINATA_BASE_URL}/data/pinList"
            if filters:
                url += "?" + "&".join([f"{k}={v}" for k, v in filters.items()])
                
            response = requests.get(url, headers=self.headers)
            
            if response.status_code != 200:
                raise Exception(f"Failed to get pin list: {response.text}")
                
            return response.json()['rows']
            
        except Exception as e:
            print(f"Error getting pin list: {str(e)}")
            return []

# Initialize Pinata manager
pinata_manager = PinataIPFSManager()

# Update the RecordManager class to improve record processing
class RecordManager:
    def __init__(self, doctor_contract, fernet):
        self.doctor_contract = doctor_contract
        self.fernet = fernet
        self._cache = {}  # Add a cache to store processed records
        self._cache_lock = Lock()  # Add thread safety for cache operations
        
    def clear_cache(self):
        """Clear the cache of processed records"""
        with self._cache_lock:
            self._cache.clear()
            
    def process_record(self, record, include_patient=False):
        """Process a single record and decrypt its metadata"""
        try:
            # Check cache first
            record_hash = record[2]  # recordHash
            with self._cache_lock:
                if record_hash in self._cache:
                    return self._cache[record_hash]
            
            encrypted_metadata = base64.b64decode(record[4])  # record[4] is encryptedData
            decrypted_metadata = self.fernet.decrypt(encrypted_metadata)
            metadata = json.loads(decrypted_metadata.decode())
            
            processed_record = {
                "record_hash": record_hash,
                "notes": record[3],        # notes
                "timestamp": record[5],    # timestamp
                "filename": metadata.get("filename"),
                "content_type": metadata.get("content_type"),
                "ipfs_hash": metadata.get("ipfs_hash"),
                "version_history": metadata.get("version_history", [])
            }
            
            if include_patient:
                processed_record["patient_hh_number"] = record[0]
            
            # Cache the processed record
            with self._cache_lock:
                self._cache[record_hash] = processed_record
                
            return processed_record
        except Exception as e:
            print(f"Error processing record: {e}")
            return None
            
    def get_version_history(self, records, record_hash):
        """Get the complete version history of a record"""
        history = []
        current_hash = record_hash
        
        while current_hash:
            found = False
            for record in records:
                if record[2] == current_hash:  # record[2] is recordHash
                    try:
                        metadata = json.loads(self.fernet.decrypt(base64.b64decode(record[4])).decode())
                        history.append({
                            "file_hash": current_hash,
                            "ipfs_hash": metadata.get("ipfs_hash"),
                            "timestamp": record[5]
                        })
                        current_hash = metadata.get("previous_version")
                        found = True
                        break
                    except Exception as e:
                        print(f"Error processing version history: {e}")
                        current_hash = None
            if not found:
                break
                
        return history

    def get_latest_records(self, records):
        """Get only the latest version of each record with improved error handling"""
        processed_records = {}
        
        try:
            # Sort records by timestamp (newest first)
            sorted_records = sorted(records, key=lambda x: x[5], reverse=True)
            
            # Track processed file hashes to avoid duplicates
            processed_hashes = set()
            
            for record in sorted_records:
                try:
                    if record[2] in processed_hashes:  # Skip if we've already processed this hash
                        continue
                        
                    processed = self.process_record(record)
                    if processed:
                        metadata = json.loads(self.fernet.decrypt(base64.b64decode(record[4])).decode())
                        previous_version = metadata.get("previous_version")
                        
                        # Add current hash to processed set
                        processed_hashes.add(record[2])
                        
                        if previous_version:
                            processed_hashes.add(previous_version)  # Also mark previous version as processed
                            
                        # Update or add the record
                        processed_records[record[2]] = processed
                        
                        # Update version history
                        processed_records[record[2]]["version_history"] = self.get_version_history(records, record[2])
                        
                except Exception as e:
                    print(f"Error processing individual record: {e}")
                    continue
                    
            return list(processed_records.values())
            
        except Exception as e:
            print(f"Error in get_latest_records: {e}")
            return list(processed_records.values())  # Return what we have even if there was an error
    
# Load environment variables from .env file
load_dotenv()

# Get the private key from the .env file (never sent from the frontend)
private_key = os.getenv("PRIVATE_KEY")

# Set up Web3 connection (Ganache instance)
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))  # Ganache HTTP RPC URL

# Check if connected to Ganache
if not w3.is_connected():
    print("Failed to connect to the Ethereum network.")
    exit()

# Load the ABI from the JSON file
with open('contract_patient_abi.json', 'r') as abi_file:
    contract_abi = json.load(abi_file)

# Contract address (replace with your actual contract address from Ganache)
contract_address = '0xA297EAe3F22c6Cb634CCb888D54E838399D3DCE5'

# Create contract instance
patient_contract = w3.eth.contract(address=contract_address, abi=contract_abi)


# Load the ABI for the doctor contract
with open('contract_doctor_abi.json', 'r') as abi_file:
    doctor_contract_abi = json.load(abi_file)

# Contract address for the doctor contract (replace with actual address from Ganache)
doctor_contract_address = '0x2538074e1567Dc526e1a30ec8EBBc87377c5EDD2'

# Create contract instance for the doctor contract
doctor_contract = w3.eth.contract(address=doctor_contract_address, abi=doctor_contract_abi)


# Load the ABI for the audit contract (add at the start of your Flask app)
with open('contract_audit_abi.json', 'r') as abi_file:
    audit_contract_abi = json.load(abi_file)

# Contract address for the audit contract (replace with actual address)
audit_contract_address = '0x4fd60f571c6dB1B88901739CE44fFD5c1441C064'  # Replace with actual address

# Create contract instance for the audit contract
audit_contract = w3.eth.contract(address=audit_contract_address, abi=audit_contract_abi)

# Get the account from Ganache (the first account in the list, for example)
account_address = w3.eth.accounts[6]

# Initialize Flask app
app = Flask(__name__)

CORS(app)  # Enable CORS for all routes


# Route to fetch patient details by hh_number
@app.route('/get_patient_details', methods=['GET'])
def get_patient_details():
    hh_number = request.args.get('hh_number')

    if not hh_number:
        return jsonify({"error": "Missing hh_number parameter"}), 400

    try:
        # Call the smart contract function to fetch patient details
        patient_details = patient_contract.functions.getPatientDetails(hh_number).call()

        # Structure the response
        patient_data = {
            "walletAddress": patient_details[0],
            "name": patient_details[1],
            "dateOfBirth": patient_details[2],
            "gender": patient_details[3],
            "bloodGroup": patient_details[4],
            "homeAddress": patient_details[5],
            "email": patient_details[6],
            "hhNumber": patient_details[7]
        }

        return jsonify({"status": "success", "patient_data": patient_data})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to fetch doctor details by hh_number
@app.route('/get_doctor_details', methods=['GET'])
def get_doctor_details():
    hh_number = request.args.get('hh_number')

    if not hh_number:
        return jsonify({"error": "Missing hh_number parameter"}), 400

    try:
        # First check if the doctor is registered
        is_registered = doctor_contract.functions.isDoctorRegistered(hh_number).call()
        
        if not is_registered:
            return jsonify({
                "status": "error",
                "error": "Doctor not registered"
            }), 404

        # If registered, proceed to get details
        doctor_details = doctor_contract.functions.getDoctorDetails(hh_number).call()

        # Structure the response to match the actual contract return values
        doctor_data = {
            "walletAddress": doctor_details[0],
            "name": doctor_details[1],
            "specialization": doctor_details[2],
            "hospitalName": doctor_details[3],  
            "hhNumber": doctor_details[4]
        }

        return jsonify({
            "status": "success",
            "doctor_data": doctor_data
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "error": f"Failed to fetch doctor details: {str(e)}"
        }), 500

@app.route('/register', methods=['POST'])
def register_patient():
    data = request.get_json()
    
    # Validate the required fields
    required_fields = ['name', 'dob', 'gender', 'blood_group', 'address', 'email', 'hh_number', 'password']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        # Get the current nonce
        nonce = w3.eth.get_transaction_count(account_address)

        # Prepare the transaction
        transaction = patient_contract.functions.registerPatient(
            data['name'],        # name
            data['dob'],         # date of birth
            data['gender'],      # gender
            data['blood_group'], # blood group
            data['address'],     # home address
            data['email'],       # email
            data['hh_number'],   # hhNumber
            data['password']     # password
        ).build_transaction({
            'from': account_address,
            'gas': 2000000,
            'gasPrice': w3.to_wei('20', 'gwei'),
            'nonce': nonce,
        })

        # Sign the transaction using the private key from .env file
        signed_txn = w3.eth.account.sign_transaction(transaction, private_key)

        # Send the signed transaction
        tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)

        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        return jsonify({
            "status": "success",
            "transaction_hash": tx_hash.hex(),  # Convert HexBytes to string
            "transaction_receipt": {
                "blockHash": tx_receipt.blockHash.hex(),
                "blockNumber": tx_receipt.blockNumber,
                "contractAddress": tx_receipt.contractAddress,
                "cumulativeGasUsed": tx_receipt.cumulativeGasUsed,
                "gasUsed": tx_receipt.gasUsed,
                "status": tx_receipt.status,
                "transactionIndex": tx_receipt.transactionIndex
            }
        })


    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/login', methods=['POST'])
def login_patient():
    data = request.get_json()
    
    # Validate the required fields
    required_fields = ['hh_number', 'password']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        # Call the smart contract function to validate the login
        is_valid = patient_contract.functions.validatePatientLogin(
            data['hh_number'],  # Health number
            data['password']    # Password
        ).call()

        if is_valid:
            return jsonify({"status": "success", "message": "Login successful"})
        else:
            return jsonify({"status": "failure", "message": "Invalid credentials"}), 401

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/register_doctor', methods=['POST'])
def register_doctor_endpoint():
    data = request.get_json()

    required_fields = ['name', 'specialization', 'hospital_name', 'hh_number', 'password']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        response = register_doctor(
            name=data['name'],
            specialization=data['specialization'],
            hospital_name=data['hospital_name'],
            hh_number=data['hh_number'],
            password=data['password'],
            private_key=private_key  # Make sure this matches the private key of the account you want to use
        )

        if response['status'] == 'success':
            tx_receipt = response['receipt']
            serialized_receipt = {
                "blockHash": tx_receipt.blockHash.hex(),
                "blockNumber": tx_receipt.blockNumber,
                "contractAddress": tx_receipt.contractAddress,
                "cumulativeGasUsed": tx_receipt.cumulativeGasUsed,
                "gasUsed": tx_receipt.gasUsed,
                "status": tx_receipt.status,
                "transactionIndex": tx_receipt.transactionIndex
            }
            return jsonify({"status": "success", "transaction_receipt": serialized_receipt})
        else:
            return jsonify({"error": response['message']}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/login_doctor', methods=['POST'])
def login_doctor():
    data = request.get_json()

    # Validate the required fields
    required_fields = ['hh_number', 'password']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        # Get the address associated with the private key
        account = w3.eth.account.from_key(private_key)
        account_address = account.address

        # Get the current nonce for the account
        nonce = w3.eth.get_transaction_count(account_address)

        transaction = doctor_contract.functions.validateDoctorLogin(
            data['hh_number'],  # Health number
            data['password']    # Password
        ).build_transaction({
            'from': account_address,  # Using the address derived from private key
            'gas': 2000000,
            'gasPrice': w3.to_wei('20', 'gwei'),
            'nonce': nonce,
        })

        # Sign the transaction
        signed_txn = w3.eth.account.sign_transaction(transaction, private_key)

        # Send the signed transaction
        tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        return jsonify({
            "status": "success",
            "transaction_hash": tx_hash.hex(),
            "transaction_receipt": {
                "blockHash": tx_receipt.blockHash.hex(),
                "blockNumber": tx_receipt.blockNumber,
                "contractAddress": tx_receipt.contractAddress,
                "cumulativeGasUsed": tx_receipt.cumulativeGasUsed,
                "gasUsed": tx_receipt.gasUsed,
                "status": tx_receipt.status,
                "transactionIndex": tx_receipt.transactionIndex
            }
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/grant_doctor_access', methods=['POST'])
def grant_doctor_access():
    data = request.get_json()
    
    # Validate the required fields
    required_fields = ['patient_hh_number', 'doctor_hh_number']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        # First verify if the doctor exists
        is_doctor_registered = doctor_contract.functions.isDoctorRegistered(data['doctor_hh_number']).call()
        if not is_doctor_registered:
            return jsonify({"error": "Doctor not registered"}), 404

        # Get the account from the private key
        account = w3.eth.account.from_key(private_key)
        account_address = account.address

        # Get the current nonce
        nonce = w3.eth.get_transaction_count(account_address)

        # Prepare the transaction
        transaction = doctor_contract.functions.grantPatientAccess(
            data['patient_hh_number'],
            data['doctor_hh_number']
        ).build_transaction({
            'from': account_address,
            'gas': 2000000,
            'gasPrice': w3.to_wei('20', 'gwei'),
            'nonce': nonce,
        })

        # Sign the transaction
        signed_txn = w3.eth.account.sign_transaction(transaction, private_key)

        # Send the signed transaction
        tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        if tx_receipt.status == 1:
            # Create audit log for access grant
            audit_details = json.dumps({
                "action": "Granted access",
                "doctor": data['doctor_hh_number'],
                "patient": data['patient_hh_number']
            })
            create_audit_log(data['doctor_hh_number'], 3, audit_details)  # 3 for GRANT_ACCESS action

        return jsonify({
            "status": "success",
            "message": "Access granted successfully",
            "transaction_hash": tx_hash.hex(),
            "transaction_receipt": {
                "blockHash": tx_receipt.blockHash.hex(),
                "blockNumber": tx_receipt.blockNumber,
                "status": tx_receipt.status
            }
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/revoke_doctor_access', methods=['POST'])
def revoke_doctor_access():
    data = request.get_json()
    
    # Validate the required fields
    required_fields = ['patient_hh_number', 'doctor_hh_number']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        # First verify if the doctor exists
        is_doctor_registered = doctor_contract.functions.isDoctorRegistered(data['doctor_hh_number']).call()
        if not is_doctor_registered:
            return jsonify({"error": "Doctor not registered"}), 404

        # Get the account from the private key
        account = w3.eth.account.from_key(private_key)
        account_address = account.address

        # Get the current nonce
        nonce = w3.eth.get_transaction_count(account_address)

        # Prepare the transaction
        transaction = doctor_contract.functions.revokePatientAccess(
            data['patient_hh_number'],
            data['doctor_hh_number']
        ).build_transaction({
            'from': account_address,
            'gas': 2000000,
            'gasPrice': w3.to_wei('20', 'gwei'),
            'nonce': nonce,
        })

        # Sign the transaction
        signed_txn = w3.eth.account.sign_transaction(transaction, private_key)

        # Send the signed transaction
        tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        if tx_receipt.status == 1:
            # Create audit log for access revocation
            audit_details = json.dumps({
                "action": "Revoked access",
                "doctor": data['doctor_hh_number'],
                "patient": data['patient_hh_number']
            })
            create_audit_log(data['doctor_hh_number'], 4, audit_details)  # 4 for REVOKE_ACCESS action

        return jsonify({
            "status": "success",
            "message": "Access revoked successfully",
            "transaction_hash": tx_hash.hex(),
            "transaction_receipt": {
                "blockHash": tx_receipt.blockHash.hex(),
                "blockNumber": tx_receipt.blockNumber,
                "status": tx_receipt.status
            }
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/check_doctor_access', methods=['GET'])
def check_doctor_access():
    patient_hh_number = request.args.get('patient_hh_number')
    doctor_hh_number = request.args.get('doctor_hh_number')

    if not patient_hh_number or not doctor_hh_number:
        return jsonify({"error": "Missing required parameters"}), 400

    try:
        # Call the smart contract function to check access
        has_access = doctor_contract.functions.checkPatientAccess(
            patient_hh_number,
            doctor_hh_number
        ).call()

        return jsonify({
            "status": "success",
            "has_access": has_access
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/get_patient_doctors', methods=['GET'])
def get_patient_doctors():
    patient_hh_number = request.args.get('patient_hh_number')
    
    if not patient_hh_number:
        return jsonify({"error": "Missing patient_hh_number parameter"}), 400
        
    try:
        # Get all doctor HH numbers with access
        doctor_hh_numbers = doctor_contract.functions.getDoctorsWithAccess(patient_hh_number).call()
        
        # Get details for each doctor
        doctors_details = []
        for hh_number in doctor_hh_numbers:
            doctor_details = doctor_contract.functions.getDoctorDetails(hh_number).call()
            doctors_details.append({
                "walletAddress": doctor_details[0],
                "name": doctor_details[1],
                "specialization": doctor_details[2],
                "hospitalName": doctor_details[3],
                "hhNumber": doctor_details[4]
            })
        
        return jsonify({
            "status": "success",
            "patient_hh_number": patient_hh_number,
            "doctors": doctors_details
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/updatePatientInfo', methods=['POST'])
def update_patient_info():
    data = request.json
    hh_number = data.get('hhNumber')
    home_address = data.get('homeAddress')
    email = data.get('email')

    if not hh_number or not home_address or not email:
        return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400

    try:
        # Get the account from the private key
        account = w3.eth.account.from_key(private_key)
        account_address = account.address

        # Get the current nonce
        nonce = w3.eth.get_transaction_count(account_address)

        # Prepare the transaction with the sender's address
        transaction = patient_contract.functions.updatePatientInfo(
            hh_number,
            home_address,
            email
        ).build_transaction({
            'from': account_address,  # Explicitly set the sender
            'gas': 2000000,
            'gasPrice': w3.to_wei('20', 'gwei'),
            'nonce': nonce,
        })

        # Sign the transaction
        signed_txn = w3.eth.account.sign_transaction(transaction, private_key)

        # Send the signed transaction
        tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)

        # Wait for transaction receipt
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        return jsonify({'status': 'success', 'transactionHash': tx_hash.hex()}), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/updateDoctorInfo', methods=['POST'])
def update_doctor_info():
    data = request.json
    hh_number = data.get('hhNumber')
    specialization = data.get('specialization')
    hospital_name = data.get('hospitalName')

    if not hh_number or not specialization or not hospital_name:
        return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400

    try:
        # Get the account from the private key
        account = w3.eth.account.from_key(private_key)
        account_address = account.address

        # Get the current nonce
        nonce = w3.eth.get_transaction_count(account_address)

        # Prepare the transaction with the sender's address
        transaction = doctor_contract.functions.updateDoctorInfo(
            hh_number,
            specialization,
            hospital_name
        ).build_transaction({
            'from': account_address,  # Explicitly set the sender
            'gas': 2000000,
            'gasPrice': w3.to_wei('20', 'gwei'),
            'nonce': nonce,
        })

        # Sign the transaction
        signed_txn = w3.eth.account.sign_transaction(transaction, private_key)

        # Send the signed transaction
        tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)

        # Wait for transaction receipt
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        return jsonify({'status': 'success', 'transactionHash': tx_hash.hex()}), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
    
# Add these helper functions to check transaction status and record existence
def verify_medical_record_creation(doctor_contract, patient_hh_number, record_hash):
    """Verify if a medical record was successfully created"""
    try:
        # Get all patient records
        records = doctor_contract.functions.getPatientAllMedicalRecords(
            patient_hh_number
        ).call()
        
        # Check if the record exists
        for record in records:
            if record[2] == record_hash:  # record[2] is recordHash
                return True
        return False
    except Exception as e:
        print(f"Verification error: {str(e)}")
        return False

# Modify the create_medical_record route
@app.route('/create_medical_record', methods=['POST'])
def create_medical_record():
    try:
        if 'file' not in request.files or \
           not request.form.get('patient_hh_number') or \
           not request.form.get('doctor_hh_number'):
            return jsonify({"error": "Missing required fields"}), 400

        patient_hh_number = request.form.get('patient_hh_number')
        doctor_hh_number = request.form.get('doctor_hh_number')
        notes = request.form.get('notes', '')
        file = request.files['file']

        # Check doctor access
        has_access = doctor_contract.functions.checkPatientAccess(
            patient_hh_number,
            doctor_hh_number
        ).call()

        if not has_access:
            return jsonify({"error": "Doctor does not have access"}), 403

        # Process file
        file_content = file.read()
        file_hash = hashlib.sha256(file_content).hexdigest()
        encrypted_content = fernet.encrypt(file_content)
        
        # Pin to IPFS using Pinata
        ipfs_hash = pinata_manager.pin_to_ipfs(encrypted_content)

        # Create metadata
        metadata = {
            "filename": file.filename,
            "content_type": file.content_type,
            "timestamp": datetime.now().isoformat(),
            "ipfs_hash": ipfs_hash,
            "file_hash": file_hash
        }
        encrypted_metadata = fernet.encrypt(json.dumps(metadata).encode())

        # Blockchain transaction
        account = w3.eth.account.from_key(private_key)
        account_address = account.address
        nonce = w3.eth.get_transaction_count(account_address)

        transaction = doctor_contract.functions.createMedicalRecord(
            patient_hh_number,
            doctor_hh_number,
            file_hash,
            notes,
            base64.b64encode(encrypted_metadata).decode()
        ).build_transaction({
            'from': account_address,
            'gas': 2000000,
            'gasPrice': w3.to_wei('20', 'gwei'),
            'nonce': nonce,
        })

        signed_txn = w3.eth.account.sign_transaction(transaction, private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        if tx_receipt.status == 1:
            # Create audit log
            audit_details = json.dumps({
                "action": "Created medical record",
                "patient": patient_hh_number,
                "file_hash": file_hash,
                "ipfs_hash": ipfs_hash
            })
            create_audit_log(doctor_hh_number, 0, audit_details)

        return jsonify({
            "status": "success",
            "message": "Medical record created successfully",
            "data": {
                "ipfs_hash": ipfs_hash,
                "file_hash": file_hash,
                "transaction_hash": tx_hash.hex(),
                "block_number": tx_receipt.blockNumber
            }
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_medical_records', methods=['GET'])
def get_medical_records():
    try:
        patient_hh_number = request.args.get('patient_hh_number')
        doctor_hh_number = request.args.get('doctor_hh_number')

        if not patient_hh_number or not doctor_hh_number:
            return jsonify({"error": "Missing required parameters"}), 400

        # Check if doctor has access
        has_access = doctor_contract.functions.checkPatientAccess(
            patient_hh_number,
            doctor_hh_number
        ).call()

        if not has_access:
            return jsonify({"error": "Doctor does not have access to this patient's records"}), 403

        # Get medical records from blockchain
        records = doctor_contract.functions.getPatientMedicalRecords(
            patient_hh_number,
            doctor_hh_number
        ).call()

        # Process and decrypt records
        processed_records = []
        for record in records:
            try:
                # Decrypt the metadata
                encrypted_metadata = base64.b64decode(record[4])  # record[4] is encryptedData
                decrypted_metadata = fernet.decrypt(encrypted_metadata)
                metadata = json.loads(decrypted_metadata.decode())

                processed_record = {
                    "record_hash": record[2],  # recordHash
                    "notes": record[3],        # notes
                    "timestamp": record[5],     # timestamp
                    "filename": metadata.get("filename"),
                    "content_type": metadata.get("content_type"),
                    "ipfs_hash": metadata.get("ipfs_hash")
                }
                processed_records.append(processed_record)
            except Exception as e:
                print(f"Error processing record: {e}")
                continue

        return jsonify({
            "status": "success",
            "records": processed_records
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Update the get_medical_record_file route
@app.route('/get_medical_record_file', methods=['GET'])
def get_medical_record_file():
    try:
        ipfs_hash = request.args.get('ipfs_hash')
        patient_hh_number = request.args.get('patient_hh_number')
        doctor_hh_number = request.args.get('doctor_hh_number')
        content_type = request.args.get('content_type', 'application/octet-stream')

        if not ipfs_hash or not patient_hh_number:
            return jsonify({"error": "Missing required parameters"}), 400

        # If doctor_hh_number is provided, it's a doctor viewing the record
        if doctor_hh_number:
            # Verify doctor's access
            has_access = doctor_contract.functions.checkPatientAccess(
                patient_hh_number,
                doctor_hh_number
            ).call()

            if not has_access:
                return jsonify({"error": "Doctor does not have access to this patient's records"}), 403

        # Get file content from Pinata/IPFS
        try:
            # Construct the IPFS gateway URL
            ipfs_url = f"https://gateway.pinata.cloud/ipfs/{ipfs_hash}"
            
            # Fetch the encrypted content
            response = requests.get(ipfs_url)
            if response.status_code != 200:
                return jsonify({"error": "Failed to fetch file from IPFS"}), 500
                
            encrypted_content = response.content
            
            # Decrypt the content
            decrypted_content = fernet.decrypt(encrypted_content)

            # Create appropriate audit logs based on who is viewing
            if doctor_hh_number:
                # Doctor viewing - create logs for both doctor and patient audit trails
                doctor_audit_details = json.dumps({
                    "action": "Viewed medical record",
                    "patient": patient_hh_number,
                    "ipfs_hash": ipfs_hash
                })
                create_audit_log(doctor_hh_number, 2, doctor_audit_details)  # 2 for VIEW action

            else:
                # Patient viewing - find all doctors who have access to this record
                records = doctor_contract.functions.getPatientAllMedicalRecords(patient_hh_number).call()
                record_doctors = set()
                
                # Find the doctor(s) associated with this record
                for record in records:
                    try:
                        encrypted_metadata = base64.b64decode(record[4])
                        decrypted_metadata = fernet.decrypt(encrypted_metadata)
                        metadata = json.loads(decrypted_metadata.decode())
                        
                        if metadata.get('ipfs_hash') == ipfs_hash:
                            record_doctor = record[1]  # doctor_hh_number from record
                            record_doctors.add(record_doctor)
                    except Exception as e:
                        print(f"Error processing record metadata: {e}")
                        continue

                # Create audit logs for each associated doctor
                for record_doctor in record_doctors:
                    patient_audit_details = json.dumps({
                        "action": "Patient viewed medical record",
                        "patient": patient_hh_number,
                        "ipfs_hash": ipfs_hash
                    })
                    create_audit_log(record_doctor, 2, patient_audit_details)  # 2 for VIEW action

            return decrypted_content, 200, {
                'Content-Type': content_type,
                'Content-Disposition': f'attachment; filename=medical_record_{ipfs_hash}'
            }

        except Exception as e:
            return jsonify({"error": f"Failed to retrieve or decrypt file: {str(e)}"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Update the get_patient_own_records endpoint for better error handling and persistence
@app.route('/get_patient_own_records', methods=['GET'])
def get_patient_own_records():
    try:
        patient_hh_number = request.args.get('patient_hh_number')

        if not patient_hh_number:
            return jsonify({"error": "Missing patient_hh_number parameter"}), 400

        # Get all medical records with retry logic
        max_retries = 3
        retry_delay = 1  # seconds
        
        for attempt in range(max_retries):
            try:
                records = doctor_contract.functions.getPatientAllMedicalRecords(
                    patient_hh_number
                ).call()
                break
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                time.sleep(retry_delay)
                continue

        # Use RecordManager to process records
        record_manager = RecordManager(doctor_contract, fernet)
        processed_records = record_manager.get_latest_records(records)

        # Verify IPFS availability for each record
        for record in processed_records:
            try:
                ipfs_hash = record.get('ipfs_hash')
                if ipfs_hash:
                    # Check if the file is still pinned in Pinata
                    pin_list = pinata_manager.get_pin_list({'ipfs_pin_hash': ipfs_hash})
                    if not pin_list:
                        # If not found in Pinata, try to re-pin it
                        print(f"Re-pinning file with hash: {ipfs_hash}")
                        # Add re-pinning logic here if needed
            except Exception as e:
                print(f"Error verifying IPFS record {ipfs_hash}: {e}")

        # Sort records by timestamp (newest first)
        processed_records.sort(key=lambda x: x['timestamp'], reverse=True)

        return jsonify({
            "status": "success",
            "records": processed_records
        })

    except Exception as e:
        print(f"Error in get_patient_own_records: {e}")
        return jsonify({"error": str(e)}), 500

# Update the get_doctor_patient_records endpoint for better persistence
@app.route('/get_doctor_patient_records', methods=['GET'])
def get_doctor_patient_records():
    try:
        doctor_hh_number = request.args.get('doctor_hh_number')

        if not doctor_hh_number:
            return jsonify({"error": "Missing doctor_hh_number parameter"}), 400

        # Get all patients with retry logic
        max_retries = 3
        retry_delay = 1  # seconds
        
        for attempt in range(max_retries):
            try:
                patients = doctor_contract.functions.getDoctorPatients(doctor_hh_number).call()
                break
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                time.sleep(retry_delay)
                continue

        record_manager = RecordManager(doctor_contract, fernet)
        all_records = []

        for patient_hh_number in patients:
            try:
                has_access = doctor_contract.functions.checkPatientAccess(
                    patient_hh_number,
                    doctor_hh_number
                ).call()
                
                if has_access:
                    # Get records with retry logic
                    for attempt in range(max_retries):
                        try:
                            records = doctor_contract.functions.getPatientMedicalRecords(
                                patient_hh_number,
                                doctor_hh_number
                            ).call()
                            break
                        except Exception as e:
                            if attempt == max_retries - 1:
                                raise e
                            time.sleep(retry_delay)
                            continue
                    
                    # Process records for this patient
                    patient_records = record_manager.get_latest_records(records)
                    
                    # Verify IPFS availability for each record
                    for record in patient_records:
                        try:
                            ipfs_hash = record.get('ipfs_hash')
                            if ipfs_hash:
                                # Check if the file is still pinned in Pinata
                                pin_list = pinata_manager.get_pin_list({'ipfs_pin_hash': ipfs_hash})
                                if not pin_list:
                                    # If not found in Pinata, try to re-pin it
                                    print(f"Re-pinning file with hash: {ipfs_hash}")
                                    # Add re-pinning logic here if needed
                        except Exception as e:
                            print(f"Error verifying IPFS record {ipfs_hash}: {e}")
                    
                    # Add patient_hh_number to each record
                    for record in patient_records:
                        record["patient_hh_number"] = patient_hh_number
                        all_records.extend([record])

            except Exception as e:
                print(f"Error processing patient {patient_hh_number}: {e}")
                continue

        # Sort all records by timestamp (newest first)
        all_records.sort(key=lambda x: x['timestamp'], reverse=True)

        return jsonify({
            "status": "success",
            "records": all_records
        })

    except Exception as e:
        print(f"Error in get_doctor_patient_records: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/update_medical_record', methods=['PUT'])
def update_medical_record():
    try:
        if 'file' not in request.files:
            return jsonify({"status": "error", "message": "No file provided"}), 400
            
        required_fields = ['patient_hh_number', 'doctor_hh_number', 'old_file_hash']
        for field in required_fields:
            if not request.form.get(field):
                return jsonify({"status": "error", "message": f"Missing required field: {field}"}), 400

        patient_hh_number = request.form.get('patient_hh_number')
        doctor_hh_number = request.form.get('doctor_hh_number')
        old_file_hash = request.form.get('old_file_hash')
        notes = request.form.get('notes', '')
        file = request.files['file']

        # Verify doctor access
        has_access = doctor_contract.functions.checkPatientAccess(
            patient_hh_number,
            doctor_hh_number
        ).call()

        if not has_access:
            return jsonify({
                "status": "error", 
                "message": "Doctor does not have access to update this record"
            }), 403

        # Get the old record's metadata
        records = doctor_contract.functions.getPatientAllMedicalRecords(patient_hh_number).call()
        old_ipfs_hash = None
        version_history = []
        
        for record in records:
            if record[2] == old_file_hash:  # record[2] is recordHash
                try:
                    encrypted_metadata = base64.b64decode(record[4])
                    decrypted_metadata = fernet.decrypt(encrypted_metadata)
                    old_metadata = json.loads(decrypted_metadata.decode())
                    old_ipfs_hash = old_metadata.get('ipfs_hash')
                    version_history = old_metadata.get('version_history', [])
                    break
                except Exception as e:
                    print(f"Error decoding old metadata: {str(e)}")

        # Add the current version to history before creating new version
        if old_ipfs_hash:
            version_history.append({
                "file_hash": old_file_hash,
                "ipfs_hash": old_ipfs_hash,
                "timestamp": datetime.now().isoformat()
            })

        # Process new file
        file_content = file.read()
        new_file_hash = hashlib.sha256(file_content).hexdigest()
        encrypted_content = fernet.encrypt(file_content)
        new_ipfs_hash = pinata_manager.pin_to_ipfs(encrypted_content)

        # Create metadata for new version
        metadata = {
            "filename": file.filename,
            "content_type": file.content_type,
            "timestamp": datetime.now().isoformat(),
            "ipfs_hash": new_ipfs_hash,
            "file_hash": new_file_hash,
            "previous_version": old_file_hash,
            "version_history": version_history
        }
        encrypted_metadata = fernet.encrypt(json.dumps(metadata).encode())

        # Update blockchain record
        account = w3.eth.account.from_key(private_key)
        account_address = account.address
        nonce = w3.eth.get_transaction_count(account_address)

        transaction = doctor_contract.functions.updateMedicalRecord(
            patient_hh_number,
            doctor_hh_number,
            old_file_hash,
            new_file_hash,
            notes,
            base64.b64encode(encrypted_metadata).decode()
        ).build_transaction({
            'from': account_address,
            'gas': 2000000,
            'gasPrice': w3.to_wei('20', 'gwei'),
            'nonce': nonce,
        })

        signed_txn = w3.eth.account.sign_transaction(transaction, private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        if tx_receipt.status == 1:
            # Unpin the old version after successful update
            if old_ipfs_hash:
                try:
                    pinata_manager.unpin_from_ipfs(old_ipfs_hash)
                except Exception as e:
                    print(f"Warning: Failed to unpin old file: {str(e)}")

            # Create audit log
            audit_details = json.dumps({
                "action": "Updated medical record",
                "patient": patient_hh_number,
                "old_file_hash": old_file_hash,
                "new_file_hash": new_file_hash,
                "new_ipfs_hash": new_ipfs_hash
            })
            create_audit_log(doctor_hh_number, 1, audit_details)

            return jsonify({
                "status": "success",
                "message": "Medical record updated successfully",
                "data": {
                    "old_file_hash": old_file_hash,
                    "new_file_hash": new_file_hash,
                    "new_ipfs_hash": new_ipfs_hash,
                    "transaction_hash": tx_hash.hex(),
                    "block_number": tx_receipt.blockNumber
                }
            })
        else:
            # If transaction failed, unpin the new file
            pinata_manager.unpin_from_ipfs(new_ipfs_hash)
            raise Exception("Transaction failed")

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Unexpected error: {str(e)}"
        }), 500
    
# Helper function to create audit logs
def create_audit_log(entity_id, action_type, details):
    """
    Create an audit log entry
    Parameters:
    - entity_id: Doctor or Patient HH number
    - action_type: Integer representing the action (0-4)
    - details: String containing additional information
    """
    try:
        # Get the account from the private key
        account = w3.eth.account.from_key(private_key)
        account_address = account.address

        # Get the current nonce
        nonce = w3.eth.get_transaction_count(account_address)

        # Prepare the transaction
        transaction = audit_contract.functions.logAudit(
            entity_id,
            action_type,
            details
        ).build_transaction({
            'from': account_address,
            'gas': 2000000,
            'gasPrice': w3.to_wei('20', 'gwei'),
            'nonce': nonce,
        })

        # Sign the transaction
        signed_txn = w3.eth.account.sign_transaction(transaction, private_key)

        # Send the signed transaction
        tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)

        # Wait for transaction receipt
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        return True
    except Exception as e:
        print(f"Error creating audit log: {str(e)}")
        return False

@app.route('/get_doctor_audit_logs', methods=['GET'])
def get_doctor_audit_logs():
    try:
        doctor_hh_number = request.args.get('doctor_hh_number')
        
        if not doctor_hh_number:
            return jsonify({"error": "Missing doctor_hh_number parameter"}), 400

        # Verify doctor exists
        is_registered = doctor_contract.functions.isDoctorRegistered(doctor_hh_number).call()
        if not is_registered:
            return jsonify({"error": "Doctor not registered"}), 404

        # Get audit logs for the doctor
        audit_logs = audit_contract.functions.getAuditLogsForEntity(doctor_hh_number).call()

        # Process audit logs
        processed_logs = []
        for log in audit_logs:
            # Convert action type from integer to string
            action_type_map = {
                0: "CREATE",
                1: "UPDATE",
                2: "VIEW",
                3: "GRANT_ACCESS",
                4: "REVOKE_ACCESS"
            }
            
            action_type = action_type_map.get(log[1], "UNKNOWN")  # log[1] is actionType

            processed_log = {
                "entityId": log[0],           # Doctor HH number
                "actionType": action_type,     # Converted action type
                "performer": log[2],          # Address that performed the action
                "timestamp": log[3],          # Timestamp of the action
                "details": log[4]             # Additional details
            }

            # Add human-readable timestamp
            processed_log["datetime"] = datetime.fromtimestamp(log[3]).strftime('%Y-%m-%d %H:%M:%S')
            
            processed_logs.append(processed_log)

        # Sort logs by timestamp in descending order (most recent first)
        processed_logs.sort(key=lambda x: x['timestamp'], reverse=True)

        return jsonify({
            "status": "success",
            "doctor_hh_number": doctor_hh_number,
            "audit_logs": processed_logs,
            "total_logs": len(processed_logs)
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

# New route to get patient audit logs
@app.route('/get_patient_audit_logs', methods=['GET'])
def get_patient_audit_logs():
    try:
        patient_hh_number = request.args.get('patient_hh_number')
        
        if not patient_hh_number:
            return jsonify({"error": "Missing patient_hh_number parameter"}), 400

        # Verify patient exists
        try:
            patient_details = patient_contract.functions.getPatientDetails(patient_hh_number).call()
            if not patient_details[0]:  # Check if wallet address is empty
                return jsonify({"error": "Patient not registered"}), 404
        except Exception as e:
            return jsonify({"error": "Patient not registered"}), 404

        # Get audit logs where the details JSON contains this patient's HH number
        all_audit_logs = []
        
        # Get doctors who have/had access to this patient
        doctors = doctor_contract.functions.getDoctorsWithAccess(patient_hh_number).call()
        
        # Collect audit logs for each doctor
        for doctor_hh_number in doctors:
            doctor_logs = audit_contract.functions.getAuditLogsForEntity(doctor_hh_number).call()
            
            # Filter logs to only include those related to this patient
            for log in doctor_logs:
                try:
                    details = json.loads(log[4])  # Parse the details JSON
                    # Check if this log is related to the patient
                    if ('patient' in details and details['patient'] == patient_hh_number) or \
                       ('patient_hh_number' in details and details['patient_hh_number'] == patient_hh_number):
                        
                        # Get doctor details for more context
                        doctor_details = doctor_contract.functions.getDoctorDetails(doctor_hh_number).call()
                        doctor_name = doctor_details[1]  # Get doctor's name
                        
                        # Convert action type from integer to string
                        action_type_map = {
                            0: "CREATE",
                            1: "UPDATE",
                            2: "VIEW",
                            3: "GRANT_ACCESS",
                            4: "REVOKE_ACCESS"
                        }
                        
                        action_type = action_type_map.get(log[1], "UNKNOWN")
                        
                        processed_log = {
                            "doctorId": doctor_hh_number,
                            "doctorName": doctor_name,
                            "actionType": action_type,
                            "performer": log[2],
                            "timestamp": log[3],
                            "details": log[4],
                            "datetime": datetime.fromtimestamp(log[3]).strftime('%Y-%m-%d %H:%M:%S')
                        }
                        
                        # Add additional context based on action type
                        if action_type == "CREATE":
                            processed_log["action_description"] = f"Dr. {doctor_name} created a new medical record"
                        elif action_type == "UPDATE":
                            processed_log["action_description"] = f"Dr. {doctor_name} updated a medical record"
                        elif action_type == "VIEW":
                            processed_log["action_description"] = f"Dr. {doctor_name} viewed a medical record"
                        elif action_type == "GRANT_ACCESS":
                            processed_log["action_description"] = f"Access granted to Dr. {doctor_name}"
                        elif action_type == "REVOKE_ACCESS":
                            processed_log["action_description"] = f"Access revoked from Dr. {doctor_name}"
                        
                        all_audit_logs.append(processed_log)
                except json.JSONDecodeError:
                    continue  # Skip logs with invalid JSON details
                except Exception as e:
                    print(f"Error processing log: {str(e)}")
                    continue

        # Sort logs by timestamp in descending order (most recent first)
        all_audit_logs.sort(key=lambda x: x['timestamp'], reverse=True)

        return jsonify({
            "status": "success",
            "patient_hh_number": patient_hh_number,
            "audit_logs": all_audit_logs,
            "total_logs": len(all_audit_logs)
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500
    
# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
