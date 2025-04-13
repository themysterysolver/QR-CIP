# ✅ YOUR MVP — IN SIMPLE STEPS

## 🧾 1. Sign In / Sign Up Page
User provides:

- 📱 **Phone number**
- 👤 **Username**
- 🔒 **Password** (set during sign-up)

🔹 Store in **database** (with proper hashing for password)

---

## 🔐 2. Login Page
- Use **username + password** to log in

---

## 🧭 3. Dashboard
Once logged in, user lands here. Contains:

### 📤 SEND TO SECTION (for Sender role):
Uploads & Sends shares via blockchain

- **Send To**: 📱 *Phone number input*
- **Upload options**:
  - 📄 **Document** → converted to **QR**
  - 📝 **Text** → converted to **video**
  - 🔑 **Key** → stored in DB (not sent yet)
- **Encrypt & store metadata**
- **Split QR (or encrypted output) into shares**
- **Use blockchain** (or simulated ledger) to record/send shares to receiver’s phone number

### 📥 RECEIVE QUEUE (for Receiver role):
Inbox to see received shares & fetch key

- Shows shares tied to receiver’s phone number
- Shows **Fetch Key** button  
  When clicked:
  - Triggers **admin to send secret key (OTP)** to phone
  - User enters key to **decrypt and show the final QR**
  - Final QR is displayed (merged from shares + key)

---

## 🛠️ TECHNOLOGIES TO USE

| Layer         | Tools                                                                 |
|---------------|-----------------------------------------------------------------------|
| **Frontend**  | HTML, CSS, JavaScript (can use Bootstrap for speed)                  |
| **Backend**   | Python (Flask or FastAPI)                                             |
| **Database**  | SQLite or PostgreSQL                                                  |
| **Auth**      | Flask-Login / JWT                                                     |
| **OTP**       | Twilio API (or dummy SMS logic)                                       |
| **Blockchain**| Simulate with smart contract on Ganache / local Ethereum / Web3.py    |
| **QR/Encrypt**| `qrcode`, `pycryptodome`, `opencv-python`                             |
| **Secret Sharing** | `secretsharing` or Shamir’s algorithm libraries                 |

---

## 🎬 How It Works Together

```mermaid
flowchart TD
    A[Sign In Page] --> B[Create Account in DB]
    C[Login Page] --> D[Validate & Redirect to Dashboard]
    D --> E1[Send To Section]
    E1 --> F1[Upload File / Text / Key]
    F1 --> G1[Encrypt & Split Shares]
    G1 --> H1[Store in Blockchain w/ Receiver’s Phone]
    D --> E2[Receive Queue]
    E2 --> F2[Load Shares from Blockchain]
    F2 --> G2[Request Key → Admin Approves]
    G2 --> H2[User Enters OTP to Unlock Final QR]
