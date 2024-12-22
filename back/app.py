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
from typing import Optional, Dict, Set
import json
import os
from threading import Lock
import threading

# IPFS API configuration
IPFS_API_BASE_URL = 'http://127.0.0.1:5001/api/v0'

# Generate encryption key - in production, this should be managed securely
encryption_key = Fernet.generate_key()
fernet = Fernet(encryption_key)

# Cache for tracking pinned hashes
class PinningCache:
    def __init__(self, cache_file: str = 'pinned_hashes.json'):
        self.cache_file = cache_file
        self.pinned_hashes: Set[str] = set()
        self.lock = Lock()
        self._load_cache()
        
        # Start background pin verification thread
        self.verify_thread = threading.Thread(target=self._verify_pins_periodically, daemon=True)
        self.verify_thread.start()
    
    def _load_cache(self):
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    self.pinned_hashes = set(json.load(f))
        except Exception as e:
            print(f"Error loading pin cache: {e}")
            self.pinned_hashes = set()
    
    def _save_cache(self):
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(list(self.pinned_hashes), f)
        except Exception as e:
            print(f"Error saving pin cache: {e}")
    
    def add(self, hash_value: str):
        with self.lock:
            self.pinned_hashes.add(hash_value)
            self._save_cache()
    
    def remove(self, hash_value: str):
        with self.lock:
            self.pinned_hashes.discard(hash_value)
            self._save_cache()
    
    def is_pinned(self, hash_value: str) -> bool:
        return hash_value in self.pinned_hashes
    
    def _verify_pins_periodically(self):
        while True:
            self._verify_all_pins()
            time.sleep(3600)  # Verify pins every hour
    
    def _verify_all_pins(self):
        with self.lock:
            hashes_to_remove = set()
            for hash_value in self.pinned_hashes:
                try:
                    response = requests.post(f'{IPFS_API_BASE_URL}/pin/ls?arg={hash_value}')
                    if response.status_code != 200:
                        print(f"Hash {hash_value} is no longer pinned, re-pinning...")
                        pin_response = requests.post(f'{IPFS_API_BASE_URL}/pin/add?arg={hash_value}')
                        if pin_response.status_code != 200:
                            hashes_to_remove.add(hash_value)
                except Exception as e:
                    print(f"Error verifying pin for {hash_value}: {e}")
            
            # Remove any hashes that couldn't be re-pinned
            for hash_value in hashes_to_remove:
                self.pinned_hashes.discard(hash_value)
            if hashes_to_remove:
                self._save_cache()

# Initialize the pinning cache
pinning_cache = PinningCache()

def ipfs_add_bytes(content: bytes, retries: int = 3, retry_delay: float = 1.0) -> str:
    """
    Add content to IPFS with automatic pinning and retry logic.
    
    Args:
        content: The bytes content to add to IPFS
        retries: Number of retry attempts
        retry_delay: Delay between retries in seconds
    
    Returns:
        str: IPFS hash of the added content
    """
    last_error = None
    
    for attempt in range(retries):
        try:
            # Add the file to IPFS
            files = {'file': content}
            response = requests.post(f'{IPFS_API_BASE_URL}/add', files=files)
            if response.status_code != 200:
                raise Exception(f"Failed to add to IPFS: {response.text}")
            
            ipfs_hash = response.json()['Hash']
            
            # Pin the file and add to cache
            pin_response = requests.post(f'{IPFS_API_BASE_URL}/pin/add?arg={ipfs_hash}')
            if pin_response.status_code != 200:
                raise Exception(f"Failed to pin file: {pin_response.text}")
            
            pinning_cache.add(ipfs_hash)
            
            # Verify the content was stored correctly
            stored_content = ipfs_cat(ipfs_hash)
            if stored_content != content:
                raise Exception("Content verification failed")
            
            return ipfs_hash
            
        except Exception as e:
            last_error = e
            if attempt < retries - 1:
                time.sleep(retry_delay)
                continue
            raise Exception(f"Failed to add content to IPFS after {retries} attempts: {str(last_error)}")

def ipfs_cat(hash_value: str, retries: int = 3, retry_delay: float = 1.0) -> Optional[bytes]:
    """
    Retrieve content from IPFS with automatic re-pinning and retry logic.
    
    Args:
        hash_value: The IPFS hash to retrieve
        retries: Number of retry attempts
        retry_delay: Delay between retries in seconds
    
    Returns:
        bytes: The retrieved content
    """
    last_error = None
    
    for attempt in range(retries):
        try:
            # Check if hash is in our pinning cache
            if not pinning_cache.is_pinned(hash_value):
                # Try to pin the hash
                pin_response = requests.post(f'{IPFS_API_BASE_URL}/pin/add?arg={hash_value}')
                if pin_response.status_code == 200:
                    pinning_cache.add(hash_value)
            
            # Get the file content
            response = requests.post(f'{IPFS_API_BASE_URL}/cat?arg={hash_value}')
            if response.status_code == 200:
                return response.content
            
            # If we couldn't get the content, try to re-pin
            pin_response = requests.post(f'{IPFS_API_BASE_URL}/pin/add?arg={hash_value}')
            if pin_response.status_code != 200:
                raise Exception(f"Failed to re-pin file: {pin_response.text}")
            
        except Exception as e:
            last_error = e
            if attempt < retries - 1:
                time.sleep(retry_delay)
                continue
            raise Exception(f"Failed to retrieve content from IPFS after {retries} attempts: {str(last_error)}")

def check_ipfs_node() -> bool:
    """
    Check if the IPFS node is running and accessible.
    
    Returns:
        bool: True if the node is running and accessible, False otherwise
    """
    try:
        response = requests.post(f'{IPFS_API_BASE_URL}/id')
        return response.status_code == 200
    except:
        return False

def get_pinned_hashes() -> Set[str]:
    """
    Get the set of currently pinned hashes.
    
    Returns:
        Set[str]: Set of pinned IPFS hashes
    """
    return set(pinning_cache.pinned_hashes)


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
        # Check if IPFS node is running
        if not check_ipfs_node():
            return jsonify({"error": "IPFS node is not running"}), 500

        # Validate input
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
        
        # IPFS storage with verification
        max_ipfs_retries = 3
        ipfs_hash = None
        
        for attempt in range(max_ipfs_retries):
            try:
                ipfs_hash = ipfs_add_bytes(encrypted_content)
                # Verify IPFS storage
                stored_content = ipfs_cat(ipfs_hash)
                if stored_content == encrypted_content:
                    break
            except Exception as e:
                if attempt == max_ipfs_retries - 1:
                    raise Exception(f"Failed to store file in IPFS after {max_ipfs_retries} attempts")
                continue

        # Create metadata
        metadata = {
            "filename": file.filename,
            "content_type": file.content_type,
            "timestamp": datetime.now().isoformat(),
            "ipfs_hash": ipfs_hash,
            "file_hash": file_hash
        }
        encrypted_metadata = fernet.encrypt(json.dumps(metadata).encode())

        # Blockchain transaction with retry mechanism
        max_blockchain_retries = 3
        tx_hash = None
        tx_receipt = None
        
        account = w3.eth.account.from_key(private_key)
        account_address = account.address

        for attempt in range(max_blockchain_retries):
            try:
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
                    'nonce': nonce + attempt,
                })

                signed_txn = w3.eth.account.sign_transaction(transaction, private_key)
                tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
                tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

                # Verify record creation
                if verify_medical_record_creation(doctor_contract, patient_hh_number, file_hash):
                    break
                else:
                    raise Exception("Record creation verification failed")
                    
            except Exception as e:
                if attempt == max_blockchain_retries - 1:
                    # If IPFS upload succeeded but blockchain failed, try to unpin the file
                    if ipfs_hash:
                        try:
                            requests.post(f'{IPFS_API_BASE_URL}/pin/rm?arg={ipfs_hash}')
                        except:
                            pass
                    raise Exception(f"Failed to create medical record after {max_blockchain_retries} attempts: {str(e)}")
                continue

        if tx_receipt.status == 1:
            # Create audit log for record creation
            audit_details = json.dumps({
                "action": "Created medical record",
                "patient": patient_hh_number,
                "file_hash": file_hash
            })
            create_audit_log(doctor_hh_number, 0, audit_details)  # 0 for CREATE action

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

        if not ipfs_hash or not patient_hh_number:
            return jsonify({"error": "Missing required parameters"}), 400

        # If doctor_hh_number is provided, check doctor's access
        if doctor_hh_number:
            has_access = doctor_contract.functions.checkPatientAccess(
                patient_hh_number,
                doctor_hh_number
            ).call()

            if not has_access:
                return jsonify({"error": "Doctor does not have access to this patient's records"}), 403

        # Get encrypted content from IPFS
        encrypted_content = ipfs_cat(ipfs_hash)
        
        # Decrypt the content
        decrypted_content = fernet.decrypt(encrypted_content)

        # If doctor is accessing the record, create audit log
        if doctor_hh_number:
            audit_details = json.dumps({
                "action": "Viewed medical record",
                "patient": patient_hh_number,
                "ipfs_hash": ipfs_hash
            })
            create_audit_log(doctor_hh_number, 2, audit_details)  # 2 for VIEW action

        return decrypted_content, 200, {
            'Content-Type': 'application/octet-stream',
            'Content-Disposition': f'attachment; filename=medical_record_{ipfs_hash}'
        }

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Add this new route to your Flask backend (paste.txt)
@app.route('/get_patient_own_records', methods=['GET'])
def get_patient_own_records():
    try:
        patient_hh_number = request.args.get('patient_hh_number')

        if not patient_hh_number:
            return jsonify({"error": "Missing patient_hh_number parameter"}), 400

        # Get medical records directly without doctor authentication
        records = doctor_contract.functions.getPatientAllMedicalRecords(
            patient_hh_number
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

@app.route('/get_doctor_patient_records', methods=['GET'])
def get_doctor_patient_records():
    try:
        doctor_hh_number = request.args.get('doctor_hh_number')

        if not doctor_hh_number:
            return jsonify({"error": "Missing doctor_hh_number parameter"}), 400

        # Get all patients that granted access to the doctor
        patients = doctor_contract.functions.getDoctorPatients(doctor_hh_number).call()
        
        all_records = []
        
        # Get records for each patient
        for patient_hh_number in patients:
            # Check if doctor still has access
            has_access = doctor_contract.functions.checkPatientAccess(
                patient_hh_number,
                doctor_hh_number
            ).call()
            
            if has_access:
                # Get patient records
                records = doctor_contract.functions.getPatientMedicalRecords(
                    patient_hh_number,
                    doctor_hh_number
                ).call()
                
                # Process and decrypt records
                for record in records:
                    try:
                        # Decrypt the metadata
                        encrypted_metadata = base64.b64decode(record[4])  # record[4] is encryptedData
                        decrypted_metadata = fernet.decrypt(encrypted_metadata)
                        metadata = json.loads(decrypted_metadata.decode())

                        processed_record = {
                            "patient_hh_number": patient_hh_number,
                            "record_hash": record[2],  # recordHash
                            "notes": record[3],        # notes
                            "timestamp": record[5],     # timestamp
                            "filename": metadata.get("filename"),
                            "content_type": metadata.get("content_type"),
                            "ipfs_hash": metadata.get("ipfs_hash")
                        }
                        all_records.append(processed_record)
                    except Exception as e:
                        print(f"Error processing record: {e}")
                        continue

        return jsonify({
            "status": "success",
            "records": all_records
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/update_medical_record', methods=['PUT'])
def update_medical_record():
    try:
        # Check if IPFS node is running
        if not check_ipfs_node():
            return jsonify({"error": "IPFS node is not running. Please start your IPFS daemon."}), 500

        # Check if required fields are present
        if 'file' not in request.files or \
           not request.form.get('patient_hh_number') or \
           not request.form.get('doctor_hh_number') or \
           not request.form.get('old_file_hash'):
            return jsonify({"error": "Missing required fields"}), 400

        patient_hh_number = request.form.get('patient_hh_number')
        doctor_hh_number = request.form.get('doctor_hh_number')
        old_file_hash = request.form.get('old_file_hash')
        notes = request.form.get('notes', '')
        file = request.files['file']

        # Check if doctor has access
        has_access = doctor_contract.functions.checkPatientAccess(
            patient_hh_number,
            doctor_hh_number
        ).call()

        if not has_access:
            return jsonify({"error": "Doctor does not have access to this patient's records"}), 403

        # Read and encrypt the new file
        file_content = file.read()
        
        # Generate a new file hash
        new_file_hash = hashlib.sha256(file_content).hexdigest()
        
        # Encrypt the file content
        encrypted_content = fernet.encrypt(file_content)
        
        # Save encrypted file to IPFS
        new_ipfs_hash = ipfs_add_bytes(encrypted_content)

        # Create encrypted metadata
        metadata = {
            "filename": file.filename,
            "content_type": file.content_type,
            "timestamp": datetime.now().isoformat(),
            "ipfs_hash": new_ipfs_hash,
            "file_hash": new_file_hash
        }
        encrypted_metadata = fernet.encrypt(json.dumps(metadata).encode())

        # Get the account from the private key
        account = w3.eth.account.from_key(private_key)
        account_address = account.address

        # Get the current nonce
        nonce = w3.eth.get_transaction_count(account_address)

        # Update medical record on blockchain with retry mechanism
        max_retries = 3
        for attempt in range(max_retries):
            try:
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
                    'nonce': nonce + attempt,
                })

                signed_txn = w3.eth.account.sign_transaction(transaction, private_key)
                tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
                tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
                
                if tx_receipt.status == 1:  # Transaction successful
                    break
            except Exception as e:
                if attempt == max_retries - 1:  # Last attempt
                    raise e
                continue

        if tx_receipt.status == 1:
            # Create audit log for record update
            audit_details = json.dumps({
                "action": "Updated medical record",
                "patient": patient_hh_number,
                "old_file_hash": old_file_hash,
                "new_file_hash": new_file_hash
            })
            create_audit_log(doctor_hh_number, 1, audit_details)  # 1 for UPDATE action

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

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
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
