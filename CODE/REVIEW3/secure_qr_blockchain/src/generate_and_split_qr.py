import qrcode
from PIL import Image
import os

def generate_qr(text: str, output_dir: str = "images/qr.png") -> str:
    """
    Generates a QR code from the provided text and saves it as an image.
    
    Args:
    - text (str): The text to be encoded in the QR code.
    - output_dir (str): The directory to save the generated QR code image.
    
    Returns:
    - str: The path where the QR code image is saved.
    """
    # Create a QR code object
    qr = qrcode.QRCode(
        version=1,  # QR code version (size of the grid)
        error_correction=qrcode.constants.ERROR_CORRECT_L,  # Error correction level
        box_size=10,  # Size of each box in the QR code grid
        border=4,  # Border size (in boxes)
    )
    
    # Add the data to the QR code
    qr.add_data(text)
    qr.make(fit=True)
    
    # Create the QR code image
    qr_image = qr.make_image(fill='black', back_color='white')
    
    # Save the QR code image
    qr_image.save(output_dir)
    
    print(f"QR code generated and saved to {output_dir}")
    return output_dir


def split_image_into_4(qr_path: str, output_dir: str = "images/") -> list:
    """
    Splits the QR code image into 4 shares.
    
    Args:
    - qr_path (str): Path to the QR code image.
    - output_dir (str): Directory to save the split images (shares).
    
    Returns:
    - list: A list of file paths to the split share images.
    """
    # Open the QR image using PIL
    qr_image = Image.open(qr_path)
    
    # Get the dimensions of the QR image
    width, height = qr_image.size
    
    # Calculate the dimensions of each share (each is a quarter of the original image)
    half_width = width // 2
    half_height = height // 2
    
    # Split the image into 4 quadrants
    shares = [
        qr_image.crop((0, 0, half_width, half_height)),  # Top-left
        qr_image.crop((half_width, 0, width, half_height)),  # Top-right
        qr_image.crop((0, half_height, half_width, height)),  # Bottom-left
        qr_image.crop((half_width, half_height, width, height))  # Bottom-right
    ]
    
    # Save the shares as separate images
    share_paths = []
    for i, share in enumerate(shares):
        share_path = os.path.join(output_dir, f"share_{i+1}.png")
        share.save(share_path)
        share_paths.append(share_path)
        print(f"Share {i+1} saved to {share_path}")
    
    return share_paths


# Example usage
if __name__ == "__main__":
    text = "hi"
    
    # Step 1: Generate the QR code
    qr_path = generate_qr(text)
    
    # Step 2: Split the QR code into 4 shares
    split_paths = split_image_into_4(qr_path)
    print("Generated and split the QR code into shares:", split_paths)
