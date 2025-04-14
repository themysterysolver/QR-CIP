from web3 import Web3
import os
from dotenv import load_dotenv

load_dotenv()

INFURA_API_KEY = os.getenv("INFURA_API_KEY")
RECEIVER = os.getenv("RECEIVER_ADDRESS")

w3 = Web3(Web3.HTTPProvider(f"https://sepolia.infura.io/v3/{INFURA_API_KEY}"))

def get_latest_hashes():
    latest_block = w3.eth.block_number
    block = w3.eth.get_block(latest_block, full_transactions=True)
    for tx in block.transactions:
        if tx['to'] and tx['to'].lower() == RECEIVER.lower():
            data = tx['input']
            decoded = bytes.fromhex(data[2:]).decode("utf-8")
            hashes = decoded.split("|")
            return hashes
    return []
