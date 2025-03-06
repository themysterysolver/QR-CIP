import numpy as np
import matplotlib.pyplot as plt
import cv2
import qrcode
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from PIL import Image

# Define PSNR and NCORR functions
def psnr(original, reconstructed):
    mse = np.mean((original - reconstructed) ** 2)
    if mse == 0:
        return float('inf')
    max_pixel = 255.0
    return 20 * np.log10(max_pixel / np.sqrt(mse))

def normxcorr2D(original, reconstructed):
    corr = np.corrcoef(original.flatten(), reconstructed.flatten())
    return corr[0, 1]

# Permutation Scrambling Functions
def sha256_to_float(seed_string):
    """Convert SHA-256 hash of a string into a floating-point number."""
    hash_digest = hashlib.sha256(seed_string.encode()).hexdigest()
    int_value = int(hash_digest[:16], 16)  # Take first 16 hex characters
    return (int_value % (10**10)) / (10**10)  # Normalize to range (0,1)

def lss_permutation(seed_string, n, r=3.9, s=3.0):
    """
    Generate a valid and chaotic permutation sequence using LSS.
    :param seed_string: String input to generate SHA-256 hash seed.
    :param n: Length of the permutation sequence.
    :param r: Control parameter for the logistic map (default: 3.9).
    :param s: Control parameter for the sine map (default: 3.0).
    :return: A list of permuted indices.
    """
    x = sha256_to_float(seed_string)  # Convert hash to seed value
    sequence = [(x := (r * x * (1 - x) + s * np.sin(np.pi * x)) % 1, i) for i in range(n)]
    permuted_indices = [i for _, i in sorted(sequence, reverse=True)]
    return np.array(permuted_indices)

def crop_qr_border(img):
    """
    Crop the white border around the QR code.
    :param img: Input image.
    :return: Cropped image.
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return img  # If no contours found, return the original image
    cnt = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(cnt)
    margin = 5
    x = max(0, x - margin)
    y = max(0, y - margin)
    w = min(img.shape[1] - x, w + 2 * margin)
    h = min(img.shape[0] - y, h + 2 * margin)
    return img[y:y+h, x:x+w]

def divide_qr(img):
    """
    Divide image into 4x4 grid of 16 blocks.
    :param img: Input image (QR code).
    :return: A list of 16 smaller blocks.
    """
    if img.shape[0] % 4 != 0 or img.shape[1] % 4 != 0:
        img = cv2.resize(img, (400, 400))  # Resize to ensure divisibility by 4
    block_size = img.shape[0] // 4
    return np.array([
        img[i * block_size:(i + 1) * block_size, j * block_size:(j + 1) * block_size]
        for i in range(4) for j in range(4)
    ])

def scramble_qr(blocks, permutation):
    """
    Scramble QR code blocks.
    :param blocks: List of divided blocks.
    :param permutation: Permutation sequence.
    :return: Scrambled blocks.
    """
    return blocks[permutation.tolist()]

def descramble_qr(blocks, permutation):
    """
    Reverse scrambling using inverse permutation.
    :param blocks: Scrambled blocks.
    :param permutation: Permutation sequence.
    :return: Descrambled blocks.
    """
    inverse_perm = np.argsort(permutation)
    return blocks[inverse_perm.tolist()]

def rebuild_matrix(blocks):
    """
    Reconstruct image from 4x4 blocks.
    :param blocks: List of blocks.
    :return: Reconstructed image.
    """
    return np.vstack([np.hstack(blocks[i * 4:(i + 1) * 4]) for i in range(4)])

# AES Encryption Functions
def encrypt_aes(data, key):
    """Encrypt data using AES-256 in CBC mode."""
    cipher = AES.new(key, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(data, AES.block_size))
    return cipher.iv + ct_bytes

def decrypt_aes(encrypted_data, key):
    """Decrypt data using AES-256 in CBC mode."""
    iv = encrypted_data[:AES.block_size]
    ct = encrypted_data[AES.block_size:]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(ct), AES.block_size)

# Share-Based Diffusion Functions
def generate_shares(encrypted_data, n, k):
    """
    Generate n shares using XOR-based diffusion.
    :param encrypted_data: Encrypted data (1D byte array).
    :param n: Total number of shares.
    :param k: Minimum number of shares required for reconstruction.
    :return: List of shares.
    """
    shares = [np.random.randint(0, 256, size=len(encrypted_data), dtype=np.uint8) for _ in range(n-1)]
    last_share = np.frombuffer(encrypted_data, dtype=np.uint8).copy()
    for share in shares:
        last_share ^= share
    shares.append(last_share)
    return shares

def reconstruct_image(shares):
    """
    Reconstruct the encrypted data from shares.
    :param shares: List of shares.
    :return: Reconstructed encrypted data (1D byte array).
    """
    return np.bitwise_xor.reduce(shares).tobytes()

# Display Functions
def display_images(qr_image, shares, reconstructed_image, title_prefix=""):
    """
    Display the QR code, shares, and reconstructed image.
    :param qr_image: QR code image.
    :param shares: List of shares.
    :param reconstructed_image: Reconstructed image.
    :param title_prefix: Prefix for the titles of the displayed images.
    """
    plt.figure(figsize=(5, 5))
    plt.imshow(qr_image, cmap='gray')
    plt.title(f"{title_prefix} QR Code")
    plt.axis('off')
    plt.show()

    fig, axes = plt.subplots(1, len(shares), figsize=(15, 5))
    for i, share in enumerate(shares):
        # Pad or truncate the share to fit a square matrix for visualization
        share_size = int(np.ceil(np.sqrt(len(share))))
        padded_size = share_size * share_size
        if len(share) < padded_size:
            # Pad with zeros
            share_padded = np.pad(share, (0, padded_size - len(share)), mode='constant')
        else:
            # Truncate
            share_padded = share[:padded_size]
        share_2d = share_padded.reshape((share_size, share_size))
        axes[i].imshow(share_2d, cmap='gray')
        axes[i].set_title(f'{title_prefix} Share {i + 1}')
        axes[i].axis('off')
    plt.show()

    plt.figure(figsize=(5, 5))
    plt.imshow(reconstructed_image, cmap='gray')
    plt.title(f"{title_prefix} Reconstructed Image")
    plt.axis('off')
    plt.show()

# Main Program
if __name__ == "__main__":
    # Ask the user for a SHA-256 input string
    sha256_input = input("Enter a string for SHA-256-based permutation: ")
    
    # Ask the user for a separate string to generate a QR code
    qr_input = input("Enter a string to generate a QR code: ")

    # Generate QR Code
    qr = qrcode.make(qr_input)
    qr.save("qr.png")

    # Load and preprocess the QR code image
    img = cv2.imread("qr.png")
    img = crop_qr_border(img)
    img = cv2.resize(img, (400, 400))  # Ensure the image is 400x400

    # Divide the QR code into 4x4 blocks
    divided_blocks = divide_qr(img)

    # Generate permutation sequence using SHA-256 input string
    n = 16
    permutation = lss_permutation(sha256_input, n)
    print("Permutation Sequence:", permutation)

    # Scramble the blocks
    scrambled_blocks = scramble_qr(divided_blocks, permutation)
    scrambled_qr = rebuild_matrix(scrambled_blocks)

    # Display the scrambled QR code
    print("Scrambled QR Code:")
    plt.imshow(scrambled_qr, cmap='gray')
    plt.title("Scrambled QR Code")
    plt.axis('off')
    plt.show()

    # Encrypt the scrambled QR code using AES
    aes_key = hashlib.sha256(sha256_input.encode()).digest()  # Derive AES key from SHA-256 input
    encrypted_qr = encrypt_aes(scrambled_qr.tobytes(), aes_key)

    # Display the AES-encrypted scrambled QR code
    print("AES-Encrypted Scrambled QR Code:")
    encrypted_qr_array = np.frombuffer(encrypted_qr, dtype=np.uint8)
    encrypted_qr_2d = encrypted_qr_array[:400*400].reshape((400, 400))  # Reshape to 2D for visualization
    plt.imshow(encrypted_qr_2d, cmap='gray')
    plt.title("AES-Encrypted Scrambled QR Code")
    plt.axis('off')
    plt.show()

    # Generate shares using XOR-based diffusion
    try:
        share_size = int(input("Input the number of shares images you want to create for encrypting (min is 2, max is 8): "))
        if share_size < 2 or share_size > 8:
            raise ValueError
    except ValueError:
        print("Input is not a valid integer!")
        exit(0)

    # Generate shares
    shares = generate_shares(encrypted_qr, share_size, share_size)

    # Display the shares
    print("Shares:")
    display_images(scrambled_qr, shares, scrambled_qr, "Scrambled")

    # Ask for the SHA-256 password again
    sha256_input_verify = input("Enter the SHA-256-based password again to reconstruct the QR code: ")

    # Verify the password
    if sha256_input_verify == sha256_input:
        print("Password verified. Reconstructing the QR code...")

        # Reconstruct the encrypted QR code from shares
        reconstructed_encrypted_qr = reconstruct_image(shares)

        # Decrypt the reconstructed QR code using AES
        decrypted_qr = decrypt_aes(reconstructed_encrypted_qr, aes_key)

        # Convert decrypted_qr back to numpy array
        decrypted_qr_array = np.frombuffer(decrypted_qr, dtype=np.uint8).reshape(scrambled_qr.shape)

        # Descramble the reconstructed QR code
        descrambled_blocks = descramble_qr(divide_qr(decrypted_qr_array), permutation)
        descrambled_qr = rebuild_matrix(descrambled_blocks)

        # Display the final descrambled QR code
        print("Descrambled QR Code:")
        plt.imshow(descrambled_qr, cmap='gray')
        plt.title("Descrambled QR Code")
        plt.axis('off')
        plt.show()

        # Evaluation metrics
        original_qr = np.asarray(Image.open("qr.png").convert('L'))  # Ensure grayscale
        descrambled_qr_resized = cv2.resize(descrambled_qr, (original_qr.shape[1], original_qr.shape[0]))

        # Convert descrambled_qr_resized to grayscale if it has 3 channels
        if len(descrambled_qr_resized.shape) == 3:
            descrambled_qr_resized = cv2.cvtColor(descrambled_qr_resized, cv2.COLOR_BGR2GRAY)

        print("Evaluation metrics:")
        print(f"PSNR value is {psnr(original_qr, descrambled_qr_resized)} dB")
        print(f"Mean NCORR value is {normxcorr2D(original_qr, descrambled_qr_resized)}")
    else:
        print("Incorrect password. Generating wrong output...")

        # Generate a random wrong output
        wrong_output = np.random.randint(0, 256, size=scrambled_qr.shape, dtype=np.uint8)
        plt.imshow(wrong_output, cmap='gray')
        plt.title("Wrong Output (Incorrect Password)")
        plt.axis('off')
        plt.show()
