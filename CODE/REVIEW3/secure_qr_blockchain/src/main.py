from generate_and_split_qr import generate_qr, split_image_into_4
from upload_to_ipfs import upload_image_to_ipfs
from send_qr import send_ipfs_hashes
from receive_qr import get_latest_ipfs_hashes, download_from_ipfs
from reconstruct_and_decode import reconstruct_image, decode_qr
import time

def main():
    # Step 1: Generate and split QR
    print("✅ Generating and splitting QR...")
    qr_path = generate_qr("🔐 Secure QR Data via Blockchain")
    shares = split_image_into_4(qr_path)

    # Step 2: Upload to IPFS
    print("🌀 Uploading shares to IPFS...")
    hashes = [upload_image_to_ipfs(share) for share in shares]

    # Step 3: Send hashes to blockchain
    print("⛓️  Sending hashes via Ethereum...")
    send_ipfs_hashes(hashes)

    # Wait for blockchain to confirm
    print("⏳ Waiting for blockchain confirmation...")
    time.sleep(30)  # Give time for TX to be mined (adjust if needed)

    # Step 4: Read from blockchain and download from IPFS
    print("📥 Reading transaction and downloading shares...")
    received_hashes = get_latest_ipfs_hashes()
    for i, h in enumerate(received_hashes):
        download_from_ipfs(h, f"received_share_{i+1}.png")

    # Step 5: Reconstruct and decode
    print("🧩 Reconstructing and decoding QR...")
    parts = [f"images/received_share_{i+1}.png" for i in range(4)]
    reconstruct_image(parts)
    decode_qr("images/reconstructed_qr.png")

if __name__ == "__main__":
    main()
