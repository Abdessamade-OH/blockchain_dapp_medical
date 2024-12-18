from flask import Flask, request, jsonify
from web3 import Web3
import json
import os
from dotenv import load_dotenv
from flask_cors import CORS
from connect_doctor import register_doctor


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
doctor_contract_address = '0x38cD50DC3959b0dDBDcc997923D22F0A08F087c3'

# Create contract instance for the doctor contract
doctor_contract = w3.eth.contract(address=doctor_contract_address, abi=doctor_contract_abi)

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

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
