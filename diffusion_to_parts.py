import numpy as np
from PIL import Image
import qrcode
import matplotlib.pyplot as plt

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

def generate_qr(data):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    return img.convert('L')  # Convert to grayscale

def encrypt(input_image, share_size):
    image = np.asarray(input_image)
    (row, column) = image.shape
    shares = np.random.randint(0, 256, size=(row, column, share_size), dtype=np.uint8)
    shares[:, :, -1] = image.copy()
    for i in range(share_size - 1):
        shares[:, :, -1] = shares[:, :, -1] ^ shares[:, :, i]
    return shares, image

def decrypt(shares):
    (row, column, share_size) = shares.shape
    shares_image = shares.copy()
    for i in range(share_size - 1):
        shares_image[:, :, -1] = shares_image[:, :, -1] ^ shares_image[:, :, i]
    final_output = shares_image[:, :, share_size - 1]
    output_image = Image.fromarray(final_output.astype(np.uint8))
    return output_image, final_output

def display_images(qr_image, shares, reconstructed_image):
    # Display the generated QR code
    plt.figure(figsize=(5, 5))
    plt.imshow(qr_image, cmap='gray')
    plt.title("Generated QR Code")
    plt.axis('off')
    plt.show()

    # Display the shares
    fig, axes = plt.subplots(1, len(shares), figsize=(15, 5))
    for i, share in enumerate(shares):
        axes[i].imshow(share, cmap='gray')
        axes[i].set_title(f'Share {i + 1}')
        axes[i].axis('off')
    plt.show()

    # Display the reconstructed image
    plt.figure(figsize=(5, 5))
    plt.imshow(reconstructed_image, cmap='gray')
    plt.title("Superimposed Output")
    plt.axis('off')
    plt.show()

if __name__ == "__main__":
    # Generate QR code from the string "me"
    qr_data = "me"
    qr_image = generate_qr(qr_data)
    print(f"QR code generated for the string '{qr_data}'.")

    try:
        share_size = int(input("Input the number of shares images you want to create for encrypting (min is 2, max is 8): "))
        if share_size < 2 or share_size > 8:
            raise ValueError
    except ValueError:
        print("Input is not a valid integer!")
        exit(0)

    # Convert QR image to grayscale numpy array
    input_image = np.asarray(qr_image)

    # Encrypt the QR code
    shares, input_matrix = encrypt(input_image, share_size)

    # Decrypt the shares to reconstruct the QR code
    output_image, output_matrix = decrypt(shares)

    # Display the images
    display_images(input_image, [shares[:, :, i] for i in range(share_size)], output_matrix)

    # Evaluation metrics
    print("Evaluation metrics:")
    print(f"PSNR value is {psnr(input_matrix, output_matrix)} dB")
    print(f"Mean NCORR value is {normxcorr2D(input_matrix, output_matrix)}")