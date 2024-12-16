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
contract_address = '0x973c5c85FADdd33FC29cdE75354accC49023568e'

# Create contract instance
patient_contract = w3.eth.contract(address=contract_address, abi=contract_abi)


# Load the ABI for the doctor contract
with open('contract_doctor_abi.json', 'r') as abi_file:
    doctor_contract_abi = json.load(abi_file)

# Contract address for the doctor contract (replace with actual address from Ganache)
doctor_contract_address = '0xd8b934580fcE35a11B58C6D73aDeE468a2833fa8'

# Create contract instance for the doctor contract
doctor_contract = w3.eth.contract(address=doctor_contract_address, abi=doctor_contract_abi)

# Get the account from Ganache (the first account in the list, for example)
account_address = w3.eth.accounts[0]

# Initialize Flask app
app = Flask(__name__)

CORS(app)  # Enable CORS for all routes


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

    # Required fields for doctor registration
    required_fields = ['name', 'specialization', 'hospital_name', 'hh_number', 'password']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        # Call the `register_doctor` function from connect_doctor.py
        response = register_doctor(
            name=data['name'],
            specialization=data['specialization'],
            hospital_name=data['hospital_name'],
            hh_number=data['hh_number'],
            password=data['password'],
            private_key=private_key
        )

        # Process the response from `register_doctor`
        if response['status'] == 'success':
            # Serialize the receipt for the response
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
            # Handle errors
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
        # Example of a state-modifying function, using .send_transaction() instead of .call()
        nonce = w3.eth.get_transaction_count(account_address)

        transaction = doctor_contract.functions.validateDoctorLogin(
            data['hh_number'],  # Health number
            data['password']    # Password
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

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
