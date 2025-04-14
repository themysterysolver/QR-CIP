import numpy as np
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import io
from base64 import b64encode

def sha256_to_float(seed_string):
    hash_digest = hashlib.sha256(seed_string.encode()).hexdigest()
    int_value = int(hash_digest[:16], 16)
    return (int_value % (10**10)) / (10**10)

def lss_permutation(seed_string, n, r=3.9, s=3.0):
    x = sha256_to_float(seed_string)
    sequence = [(x := (r * x * (1 - x) + s * np.sin(np.pi * x)) % 1, i) for i in range(n)]
    permuted_indices = [i for _, i in sorted(sequence, reverse=True)]
    return np.array(permuted_indices)

def encrypt_aes(data, key):
    cipher = AES.new(key, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(data, AES.block_size))
    return cipher.iv + ct_bytes

def generate_shares(encrypted_data, n):
    shares = [np.random.randint(0, 256, size=len(encrypted_data), dtype=np.uint8) for _ in range(n-1)]
    last_share = np.frombuffer(encrypted_data, dtype=np.uint8).copy()
    for share in shares:
        last_share ^= share
    shares.append(last_share)
    return shares

def process_and_generate_shares(seed_string, qr_string, n_shares):
    # Generate AES key from seed
    aes_key = hashlib.sha256(seed_string.encode()).digest()
    
    # Generate QR code and encrypt it
    encrypted_qr = encrypt_aes(qr_string.encode(), aes_key)
    
    # Generate shares for the encrypted data
    shares = generate_shares(encrypted_qr, n_shares)
    
    return shares, encrypted_qr  # Return both shares and encrypted data
