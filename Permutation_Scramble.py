import numpy as np
import matplotlib.pyplot as plt
import cv2
import qrcode

def lss_permutation(seed, n, r=3.9, s=3.0):
    """
    Generate a valid and chaotic permutation sequence using LSS.
    :param seed: Initial seed value (x0) for the LSS algorithm.
    :param n: Length of the permutation sequence.
    :param r: Control parameter for the logistic map (default: 3.9).
    :param s: Control parameter for the sine map (default: 3.0).
    :return: A list of permuted indices.
    """
    x = seed  # Initial seed
    sequence = [(x := (r * x * (1 - x) + s * np.sin(np.pi * x)) % 1, i) for i in range(n)]

    # Generate permutation indices
    permuted_indices = [i for _, i in sorted(sequence, reverse=True)]
    
    return np.array(permuted_indices)

def crop_qr_border(img):
    """
    Crop the white border around the QR code.
    :param img: Input image.
    :return: Cropped image.
    """
    # Convert to grayscale and threshold to binary
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)

    # Find contours and get the largest one (QR code)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return img  # If no contours found, return the original image

    cnt = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(cnt)

    # Add a small margin to ensure the border is fully removed
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
    return blocks[permutation.tolist()]  # Ensure proper indexing

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

def display_qr(img, title="QR Code"):
    """
    Display image.
    :param img: Input image.
    :param title: Title of the displayed image.
    """
    plt.imshow(cv2.cvtColor(img.astype(np.uint8), cv2.COLOR_BGR2RGB))
    plt.title(title)
    plt.axis("off")
    plt.show()

if __name__ == "__main__":
    # Ask the user for a string input
    user_input = input("Enter a string to generate a QR code: ")

    # Initialisation
    seed = 0.85  # Change seed for more randomization
    n = 16  # Number of blocks (4x4 grid)
    permutation = lss_permutation(seed, n)  # Generate permutation sequence using LSS
    print("Permutation Sequence:", permutation)

    # Generate QR Code
    qr = qrcode.make(user_input)  # Use the user's input to generate the QR code
    qr.save("qr.png")

    # Load and preprocess the QR code image
    img = cv2.imread("qr.png")

    # Crop the white border
    img = crop_qr_border(img)
    img = cv2.resize(img, (400, 400))  # Ensure the image is 400x400

    # Divide the QR code into 4x4 blocks
    divided_blocks = divide_qr(img)

    # Display the original QR code
    print("Original QR Code:")
    display_qr(rebuild_matrix(divided_blocks), "Original QR Code")

    # Scramble the blocks
    scrambled_blocks = scramble_qr(divided_blocks, permutation)
    print("Scrambled QR Code:")
    display_qr(rebuild_matrix(scrambled_blocks), "Scrambled QR Code")

    # Descramble the blocks
    descrambled_blocks = descramble_qr(scrambled_blocks, permutation)
    print("Descrambled QR Code:")
    display_qr(rebuild_matrix(descrambled_blocks), "Descrambled QR Code")