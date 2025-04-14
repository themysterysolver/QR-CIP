import os
import requests

PINATA_API_KEY = os.getenv("PINATA_API_KEY")
PINATA_SECRET_API_KEY = os.getenv("PINATA_SECRET_API_KEY")

def upload_image_to_ipfs(image_path):
    url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
    headers = {
        "pinata_api_key": PINATA_API_KEY,
        "pinata_secret_api_key": PINATA_SECRET_API_KEY
    }
    
    with open(image_path, "rb") as f:
        files = {
            "file": (os.path.basename(image_path), f)
        }
        response = requests.post(url, files=files, headers=headers)

    if response.status_code == 200:
        ipfs_hash = response.json()["IpfsHash"]
        print(f"✅ Uploaded {image_path} to IPFS: {ipfs_hash}")
        return ipfs_hash
    else:
        raise Exception(f"❌ Failed to upload to IPFS: {response.text}")
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    print("🚀 Uploading QR shares to IPFS...")
    for i in range(1, 5):
        image_path = f"images/share_{i}.png"
        try:
            ipfs_hash = upload_image_to_ipfs(image_path)
            print(f"🔗 Share {i} IPFS Hash: {ipfs_hash}")
        except Exception as e:
            print(e)
