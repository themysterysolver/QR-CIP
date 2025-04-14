from PIL import Image
import cv2
import numpy as np
import os

def reconstruct_image(parts):
    images = [Image.open(p) for p in parts]
    top = np.hstack((np.array(images[0]), np.array(images[1])))
    bottom = np.hstack((np.array(images[2]), np.array(images[3])))
    full = np.vstack((top, bottom))
    final = Image.fromarray(full)
    final.save("images/reconstructed_qr.png")
    print("Reconstructed QR saved.")

def decode_qr(image_path):
    img = cv2.imread(image_path)
    detector = cv2.QRCodeDetector()
    data, _, _ = detector.detectAndDecode(img)
    print("Decoded QR Data:", data)

if __name__ == "__main__":
    parts = [f"images/received_share_{i+1}.png" for i in range(4)]
    reconstruct_image(parts)
    decode_qr("images/reconstructed_qr.png")
