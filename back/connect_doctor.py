import json
from web3 import Web3  # Correct import


# Set up Web3 connection (Ganache instance)
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))  # Ganache HTTP RPC URL

# Load the ABI from the JSON file
with open('contract_doctor_abi.json', 'r') as abi_file:
    doctor_contract_abi = json.load(abi_file)

# Contract address (replace with your actual contract address from Ganache)
doctor_contract_address = '0xd8b934580fcE35a11B58C6D73aDeE468a2833fa8'  # Replace with the actual address

# Create contract instance
doctor_contract = w3.eth.contract(address=doctor_contract_address, abi=doctor_contract_abi)

def register_doctor(name, specialization, hospital_name, hh_number, password, private_key):
    """
    Registers a doctor in the blockchain.
    """
    # Get the account from Ganache (the first account in the list, for example)
    account_address = w3.eth.accounts[0]

    # Set up a transaction to call the `registerDoctor` function
    nonce = w3.eth.get_transaction_count(account_address)
    try:
        transaction = doctor_contract.functions.registerDoctor(
            name, specialization, hospital_name, hh_number, password
        ).build_transaction({
            'from': account_address,
            'gas': 2000000,
            'gasPrice': w3.to_wei('20', 'gwei'),
            'nonce': nonce,
        })

        signed_txn = w3.eth.account.sign_transaction(transaction, private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)

        try:
            tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            
            # Check transaction status explicitly
            if tx_receipt['status'] == 0:
                return {
                    "status": "error", 
                    "message": "Transaction failed (likely due to a contract require statement)"
                }

            return {"status": "success", "receipt": tx_receipt}

        except Exception as receipt_error:
            return {
                "status": "error", 
                "message": f"Transaction receipt error: {str(receipt_error)}"
            }

    except Exception as e:
        # More detailed error logging
        return {
            "status": "error", 
            "message": f"Registration error: {str(e)}",
            "error_type": type(e).__name__
        }
    