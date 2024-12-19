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

# IPFS API configuration
IPFS_API_BASE_URL = 'http://127.0.0.1:5001/api/v0'

# Generate encryption key - in production, this should be managed securely
encryption_key = Fernet.generate_key()
fernet = Fernet(encryption_key)

# Function to add content to IPFS
def ipfs_add_bytes(content):
    try:
        files = {
            'file': content
        }
        response = requests.post(f'{IPFS_API_BASE_URL}/add', files=files)
        if response.status_code == 200:
            return response.json()['Hash']
        else:
            raise Exception(f"Failed to add to IPFS: {response.text}")
    except Exception as e:
        raise Exception(f"IPFS add error: {str(e)}")

# Function to get content from IPFS
def ipfs_cat(hash_value):
    try:
        response = requests.post(f'{IPFS_API_BASE_URL}/cat?arg={hash_value}')
        if response.status_code == 200:
            return response.content
        else:
            raise Exception(f"Failed to get from IPFS: {response.text}")
    except Exception as e:
        raise Exception(f"IPFS cat error: {str(e)}")


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
contract_address = '0x77BEB626ff16CfdFB8641FCe31612eCc1ccA1F4E'

# Create contract instance
patient_contract = w3.eth.contract(address=contract_address, abi=contract_abi)


# Load the ABI for the doctor contract
with open('contract_doctor_abi.json', 'r') as abi_file:
    doctor_contract_abi = json.load(abi_file)

# Contract address for the doctor contract (replace with actual address from Ganache)
doctor_contract_address = '0xE29244A44e40693e6F9b63629B640F608D3dB38d'

# Create contract instance for the doctor contract
doctor_contract = w3.eth.contract(address=doctor_contract_address, abi=doctor_contract_abi)

# Get the account from Ganache (the first account in the list, for example)
account_address = w3.eth.accounts[0]

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

        return jsonify({
            "status": "success",
            "message": "Access granted successfully",
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

        return jsonify({
            "status": "success",
            "message": "Access revoked successfully",
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
    
# Update the create_medical_record route
@app.route('/create_medical_record', methods=['POST'])
def create_medical_record():
    try:
        # Check if required fields are present
        if 'file' not in request.files or not request.form.get('patient_hh_number') or not request.form.get('doctor_hh_number'):
            return jsonify({"error": "Missing required fields"}), 400

        patient_hh_number = request.form.get('patient_hh_number')
        doctor_hh_number = request.form.get('doctor_hh_number')
        notes = request.form.get('notes', '')
        file = request.files['file']

        # First check if doctor has access
        has_access = doctor_contract.functions.checkPatientAccess(
            patient_hh_number,
            doctor_hh_number
        ).call()

        if not has_access:
            return jsonify({"error": "Doctor does not have access to this patient's records"}), 403

        # Read and encrypt the file
        file_content = file.read()
        
        # Generate a unique file hash
        file_hash = hashlib.sha256(file_content).hexdigest()
        
        # Encrypt the file content
        encrypted_content = fernet.encrypt(file_content)
        
        # Save encrypted file to IPFS using the new function
        ipfs_hash = ipfs_add_bytes(encrypted_content)

        # Create encrypted metadata
        metadata = {
            "filename": file.filename,
            "content_type": file.content_type,
            "timestamp": datetime.now().isoformat(),
            "ipfs_hash": ipfs_hash,
            "file_hash": file_hash
        }
        encrypted_metadata = fernet.encrypt(json.dumps(metadata).encode())
        
        # Get the account from the private key
        account = w3.eth.account.from_key(private_key)
        account_address = account.address

        # Get the current nonce
        nonce = w3.eth.get_transaction_count(account_address)

        # Create medical record on blockchain
        transaction = doctor_contract.functions.createMedicalRecord(
            patient_hh_number,
            doctor_hh_number,
            file_hash,  # record hash
            notes,      # notes
            base64.b64encode(encrypted_metadata).decode()  # encrypted metadata
        ).build_transaction({
            'from': account_address,
            'gas': 2000000,
            'gasPrice': w3.to_wei('20', 'gwei'),
            'nonce': nonce,
        })

        # Sign and send the transaction
        signed_txn = w3.eth.account.sign_transaction(transaction, private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

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

        if not all([ipfs_hash, patient_hh_number, doctor_hh_number]):
            return jsonify({"error": "Missing required parameters"}), 400

        # Check if doctor has access
        has_access = doctor_contract.functions.checkPatientAccess(
            patient_hh_number,
            doctor_hh_number
        ).call()

        if not has_access:
            return jsonify({"error": "Doctor does not have access to this patient's records"}), 403

        # Get encrypted content from IPFS using the new function
        encrypted_content = ipfs_cat(ipfs_hash)
        
        # Decrypt the content
        decrypted_content = fernet.decrypt(encrypted_content)

        return decrypted_content, 200, {
            'Content-Type': 'application/octet-stream',
            'Content-Disposition': f'attachment; filename=medical_record_{ipfs_hash}'
        }

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
