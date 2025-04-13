## ABOUT!
- The code generates a QR code from user input and crops/resizes it for processing.
- It divides the QR into blocks, scrambles them using a permutation derived from a chaotic map and a SHA-256-based seed.
- The scrambled QR is AES encrypted, then split into multiple shares using XOR-based secret sharing.
- These shares can be recombined to reconstruct and decrypt the scrambled image.
- If the user provides the correct password again, the QR is descrambled and compared with the original using PSNR, NCORR, and SSIM metrics.
---
