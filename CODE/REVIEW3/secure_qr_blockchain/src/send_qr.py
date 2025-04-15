import os
import json
import requests
from web3 import Web3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Constants from .env file
PINATA_API_KEY = os.getenv("PINATA_API_KEY")
PINATA_SECRET_API_KEY = os.getenv("PINATA_SECRET_API_KEY")
ALCHEMY_API_URL = os.getenv("ALCHEMY_API_URL")
SENDER_ADDRESS = os.getenv("SENDER_ADDRESS")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
RECEIVER_ADDRESS = os.getenv("RECEIVER_ADDRESS")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")
CONTRACT_ABI = json.loads(os.getenv("CONTRACT_ABI"))  # Parse the ABI from .env

# Web3 Setup
w3 = Web3(Web3.HTTPProvider(ALCHEMY_API_URL))

# Verify connection to Ethereum node
if not w3.is_connected():
    raise Exception("Failed to connect to the Ethereum network.")

# Load contract
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)

def send_transaction(ipfs_hash):
    """
    Send the IPFS hash to the blockchain through a transaction.
    """
    # Prepare transaction data
    tx_data = contract.functions.sendQRData(ipfs_hash).buildTransaction({
        'from': SENDER_ADDRESS,
        'gas': 2000000,
        'gasPrice': w3.toWei('20', 'gwei'),
        'nonce': w3.eth.getTransactionCount(SENDER_ADDRESS),
    })

    # Sign the transaction
    signed_tx = w3.eth.account.signTransaction(tx_data, PRIVATE_KEY)

    # Send the transaction
    tx_hash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
    print(f"Transaction sent with hash: {tx_hash.hex()}")
    return tx_hash.hex()

def upload_image_to_ipfs(image_path):
    """
    Upload an image to IPFS using Pinata.
    """
    url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
    headers = {
        "pinata_api_key": PINATA_API_KEY,
        "pinata_secret_api_key": PINATA_SECRET_API_KEY
    }
    
    with open(image_path, "rb") as f:
        files = {"file": (os.path.basename(image_path), f)}
        response = requests.post(url, files=files, headers=headers)
    
    if response.status_code == 200:
        ipfs_hash = response.json()["IpfsHash"]
        print(f"✅ Uploaded {image_path} to IPFS: {ipfs_hash}")
        return ipfs_hash
    else:
        raise Exception(f"❌ Failed to upload to IPFS: {response.text}")

def main():
    # Example IPFS upload and transaction
    print("🚀 Uploading QR share to IPFS...")
    for i in range(1, 5):
        image_path = f"images/share_{i}.png"
        try:
            ipfs_hash = upload_image_to_ipfs(image_path)
            print(f"🔗 Share {i} IPFS Hash: {ipfs_hash}")
            # Send the IPFS hash to the blockchain
            tx_hash = send_transaction(ipfs_hash)
            print(f"Transaction successful! Hash: {tx_hash}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
