import os
import requests
from web3 import Web3
from upload_to_ipfs import upload_image_to_ipfs  # Assuming upload_to_ipfs.py has the IPFS uploading function

# Alchemy API URL and your MetaMask details
ALCHEMY_API_URL = os.getenv("ALCHEMY_API_URL")  # Example: 'https://eth-sepolia.g.alchemy.com/v2/your-api-key'
SENDER_ADDRESS = os.getenv("SENDER_ADDRESS")  # Your MetaMask address
PRIVATE_KEY = os.getenv("PRIVATE_KEY")  # Your MetaMask private key
CONTRACT_ADDRESS = 'YOUR_DEPLOYED_CONTRACT_ADDRESS'  # Replace with your deployed contract address
CONTRACT_ABI = 'YOUR_CONTRACT_ABI'  # Replace with your contract ABI, either in JSON or a Python dictionary format

# Initialize Web3
web3 = Web3(Web3.HTTPProvider(ALCHEMY_API_URL))

# Your contract
contract = web3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)

# Function to send IPFS hashes to the blockchain
def send_ipfs_hashes(hashes):
    # Set up the sender address
    account = SENDER_ADDRESS

    # Loop through each IPFS hash and send it to the smart contract
    for i, hash in enumerate(hashes):
        # Prepare the transaction data
        tx = contract.functions.storeIPFSHash(i, hash).buildTransaction({
            'gas': 500000,
            'gasPrice': web3.toWei('20', 'gwei'),
            'nonce': web3.eth.getTransactionCount(account),
        })

        # Sign the transaction with your private key
        signed_tx = web3.eth.account.signTransaction(tx, PRIVATE_KEY)

        # Send the transaction
        tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)
        print(f"Transaction sent! Hash: {tx_hash.hex()}")

        # Optionally, you can wait for the receipt to ensure the transaction is mined
        receipt = web3.eth.waitForTransactionReceipt(tx_hash)
        print(f"Transaction receipt: {receipt}")

# Main function for generating, uploading QR codes, and sending IPFS hashes to Ethereum
def main():
    # Example: Generate and split QR
    qr_paths = ['path_to_qr_share1.png', 'path_to_qr_share2.png', 'path_to_qr_share3.png', 'path_to_qr_share4.png']
    hashes = []

    # Upload the QR images to IPFS and collect the IPFS hashes
    for qr_path in qr_paths:
        ipfs_hash = upload_image_to_ipfs(qr_path)  # upload_to_ipfs.py should handle this function
        hashes.append(ipfs_hash)

    # Now, send the hashes to the Ethereum blockchain
    send_ipfs_hashes(hashes)

# Run the main function
if __name__ == "__main__":
    main()
