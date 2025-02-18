from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import base64
import time
import os

BLOCK_SIZE = 128

def pad(data):
    padder = padding.PKCS7(BLOCK_SIZE).padder()
    padded_data = padder.update(data) + padder.finalize()
    return padded_data

def unpad(padded_data):
    unpadder = padding.PKCS7(BLOCK_SIZE).unpadder()
    data = unpadder.update(padded_data) + unpadder.finalize()
    return data

def AESencrypt(plaintext,key,iv):
    # pick an instance of AES in OFB mode
    aes = Cipher(algorithms.AES(key),modes.OFB(iv)).encryptor()
    return aes.update(pad(plaintext, BLOCK_SIZE)) + aes.finalize()

# decrypt and unpad ciphertext
def AESdecrypt(ciphertext, key, iv):
    # pick an instance of AES in OFB mode
    aes = Cipher(algorithms.AES(key), modes.OFB(iv)).decryptor()
    return unpad(aes.update(ciphertext) + aes.finalize(), BLOCK_SIZE)


def modifycookie(encryptedCookie_b64):
    encryptedCookie = base64.b64decode(encryptedCookie_b64)

    # Perpare the orginal values & modified values
    UUserName = b"anonymous"
    AUserName = b"admin,"
    uTimestamp = b"1706745660"
    currentTimestamp = str(int(time.time())).encode('utf-8')
    print("Current Timestamp:", currentTimestamp)

    # Get the position of the username & timestamp
    userNamePosition = 5
    timestampPosition = userNamePosition + len(UUserName) + 8

    # XOR the two usernames to get the XOR mask
    xorMask = bytes(a ^ b for a, b in zip(UUserName, AUserName))

    # XOR the current timestamp with the timestamp in the encrypted cookie to get the XOR mask
    xorMaskTimestamp = bytes(a ^ b for a, b in zip(uTimestamp, currentTimestamp))
    
    # Modify the encrypted cookie (use for loop to XOR the mask with the encrypted cookie byte by byte)
    modifiedEncryptedCookie = bytearray(encryptedCookie)
    for i in range(len(xorMask)):
        modifiedEncryptedCookie[userNamePosition + i] ^= xorMask[i]

    for i in range(len(xorMaskTimestamp)):
        modifiedEncryptedCookie[timestampPosition + i] ^= xorMaskTimestamp[i]
    
    return base64.b64encode(bytes(modifiedEncryptedCookie)).decode()

def main():
    # Generate a random key & IV
    key = os.urandom(32)
    iv = os.urandom(16)
    plaintextCookie = b"user=anonymous,tmstmp=1706745660"
    encryptedCookie = AESencrypt( plaintextCookie,key, iv)
    base64EncodedCookie = base64.b64encode(encryptedCookie).decode()
    print("Original Cookie (base64):", base64EncodedCookie)

    # Modify the encrypted cookie
    modifiedCookieB64 = modifycookie(base64EncodedCookie)
    print("Modified Cookie (base64):", modifiedCookieB64)
    modifiedCookiePlaintext = AESdecrypt(key, base64.b64decode(modifiedCookieB64), iv)
    print("Decrypted Modified Cookie:", modifiedCookiePlaintext)

main()