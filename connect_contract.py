import os
from dotenv import load_dotenv
from web3 import Web3
import json

# Load environment variables from .env file
load_dotenv()

# Get the private key from the .env file
private_key = os.getenv("PRIVATE_KEY")

# Set up Web3 connection (Ganache instance)
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))  # Ganache HTTP RPC URL

# Check if connected to Ganache
if w3.is_connected():
    print("Connected to Ethereum network.")
else:
    print("Failed to connect to the Ethereum network.")

# Load the ABI from the JSON file
with open('contract_abi.json', 'r') as abi_file:
    contract_abi = json.load(abi_file)

# Contract address (replace with your actual contract address from Ganache)
contract_address = '0x973c5c85FADdd33FC29cdE75354accC49023568e'

# Create contract instance
patient_contract = w3.eth.contract(address=contract_address, abi=contract_abi)

# Get the account from Ganache (the first account in the list, for example)
account_address = w3.eth.accounts[0]

# Set up a transaction to call the `registerPatient` function
try:
    # Get the current nonce
    nonce = w3.eth.get_transaction_count(account_address)

    # Prepare the transaction
    transaction = patient_contract.functions.registerPatient(
        'John Doe',          # name
        '01-01-1990',        # date of birth
        'Male',              # gender
        'O+',                # blood group
        '123 Main St',       # home address
        'john.doe4@email.com', # email
        '12348',             # hhNumber
        'password123'        # password
    ).build_transaction({
        'from': account_address,
        'gas': 2000000,
        'gasPrice': w3.to_wei('20', 'gwei'),
        'nonce': nonce,
    })
    print("Transaction built successfully.")
except Exception as e:
    print(f"Error building transaction: {e}")
    exit()

# Sign the transaction using the private key from .env file
try:
    # Sign the transaction
    signed_txn = w3.eth.account.sign_transaction(transaction, private_key)
    
    # Send the signed transaction - note the change to raw_transaction
    tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
    print(f"Transaction hash: {tx_hash.hex()}")
    
    # Wait for the transaction receipt
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print("Transaction successful!")
    print(f"Transaction receipt: {tx_receipt}")

except Exception as e:
    print(f"Error sending transaction: {e}")
