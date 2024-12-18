import json
from web3 import Web3

# Set up Web3 connection (Ganache instance)
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))  # Ganache HTTP RPC URL

# Load the ABI from the JSON file
with open('contract_patient_abi.json', 'r') as abi_file:
    contract_abi = json.load(abi_file)

# Contract address (replace with your actual contract address from Ganache)
contract_address = '0x51E64eab866e1287490ceFeA9111a8207796C776'

# Create contract instance
patient_contract = w3.eth.contract(address=contract_address, abi=contract_abi)

def register_patient(name, dob, gender, blood_group, address, email, hh_number, password, private_key):
    # Get the account from Ganache (the first account in the list, for example)
    account_address = w3.eth.accounts[6]

    # Set up a transaction to call the `registerPatient` function
    nonce = w3.eth.get_transaction_count(account_address)

    try:
        # Prepare the transaction
        transaction = patient_contract.functions.registerPatient(
            name, dob, gender, blood_group, address, email, hh_number, password
        ).build_transaction({
            'from': account_address,
            'gas': 2000000,
            'gasPrice': w3.to_wei('20', 'gwei'),
            'nonce': nonce,
        })

        # Sign the transaction using the private key
        signed_txn = w3.eth.account.sign_transaction(transaction, private_key)

        # Send the signed transaction
        tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)

        # Wait for the transaction receipt
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        return {"status": "success", "receipt": tx_receipt}

    except Exception as e:
        return {"status": "error", "message": str(e)}
