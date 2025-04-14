## SECURING IT IN BLOCKCHAIN
---
##### DIR STRUCTURE
```
secure_qr_blockchain/
│
├── .env                      # API keys and wallet info
├── requirements.txt          # Dependencies
├── README.md
│
├── images/                   # Stores QR and its split/reconstructed images
│   ├── qr.png
│   ├── share_1.png
│   ├── ...
│   ├── received_share_1.png
│   └── reconstructed_qr.png
│
├── src/                      # Python source code
│   ├── __init__.py
│   ├── generate_and_split_qr.py
│   ├── upload_to_ipfs.py
│   ├── send_qr.py
│   ├── receive_qr.py
│   ├── reconstruct_and_decode.py
│   └── main.py               # <--- Run this to do it all

```
----
# Secure QR Blockchain

This project demonstrates the process of generating, storing, and retrieving a QR code using blockchain and IPFS. The QR code is split into multiple parts, uploaded to IPFS, and its hashes are stored on the blockchain. Later, the QR code is reconstructed and decoded from the parts.

## File Functions

### `generate_and_split_qr.py`

- **`generate_qr(text)`**: Generates a QR code for the given text and saves it as an image.
- **`split_image_into_4(qr_path)`**: Splits the generated QR image into 4 shares (images).

### `upload_to_ipfs.py`

- **`upload_image_to_ipfs(image_path)`**: Uploads an image (share) to IPFS and returns the IPFS hash for that image.

### `send_qr.py`

- **`send_ipfs_hashes(hashes)`**: Sends the list of IPFS hashes to the blockchain (likely Ethereum).

### `receive_qr.py`

- **`get_latest_ipfs_hashes()`**: Retrieves the latest IPFS hashes from the blockchain.
- **`download_from_ipfs(hash, save_path)`**: Downloads an image from IPFS using the provided hash and saves it to the given path.

### `reconstruct_and_decode.py`

- **`reconstruct_image(parts)`**: Reconstructs the original QR image from the 4 shares (split parts).
- **`decode_qr(image_path)`**: Decodes the QR code from the reconstructed image to extract the original text.

### `main.py`

- **`main()`**: Orchestrates the entire flow:
  1. Generates a QR code, splits it into shares.
  2. Uploads the shares to IPFS.
  3. Sends the hashes to the blockchain.
  4. Waits for confirmation, retrieves the hashes from the blockchain, and downloads the shares.
  5. Reconstructs the QR code and decodes it to get back the original text.

## Overview

This structure allows you to generate, store, and retrieve a QR code across a decentralized network (IPFS), while ensuring the QR is safely reconstructed from shares distributed across multiple locations.

---