from flask import Flask, request, jsonify, send_file, render_template
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import os

# Constants
ENCRYPTION_KEY = b'0123456789abcdef0123456789abcdef'  # 32 bytes key for AES-256
UPLOAD_FOLDER = 'encrypted_files'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Flask App
app = Flask(__name__)

# Encryption Function
def encrypt_file(data):
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(ENCRYPTION_KEY), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(data) + padder.finalize()

    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
    return iv, encrypted_data

# Decryption Function
def decrypt_file(encrypted_data, iv):
    cipher = Cipher(algorithms.AES(ENCRYPTION_KEY), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()

    decrypted_padded_data = decryptor.update(encrypted_data) + decryptor.finalize()

    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    data = unpadder.update(decrypted_padded_data) + unpadder.finalize()
    return data

# Home route to render the HTML
@app.route('/')
def home():
    return render_template('index.html')

# Route to Upload and Encrypt File
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        print("No file part in the request")
        return jsonify({'message': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        print("No file selected")
        return jsonify({'message': 'No selected file'}), 400

    if file:
        file_data = file.read()
        iv, encrypted_data = encrypt_file(file_data)
        file_path = os.path.join(UPLOAD_FOLDER, file.filename + '.enc')

        # Save encrypted data and iv
        with open(file_path, 'wb') as f:
            f.write(iv + encrypted_data)

        print(f"File {file.filename} uploaded and encrypted successfully.")
        return jsonify({'message': 'File uploaded and encrypted successfully!'}), 200

# Route to Decrypt and Download File
@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    try:
        file_path = os.path.join(UPLOAD_FOLDER, filename + '.enc')

        with open(file_path, 'rb') as f:
            encrypted_data = f.read()
            iv = encrypted_data[:16]
            actual_encrypted_data = encrypted_data[16:]

            decrypted_data = decrypt_file(actual_encrypted_data, iv)

            # Save the decrypted data temporarily for download
            temp_path = os.path.join(UPLOAD_FOLDER, 'temp_' + filename)
            with open(temp_path, 'wb') as temp_file:
                temp_file.write(decrypted_data)

            return send_file(temp_path, as_attachment=True, download_name=filename)

    except FileNotFoundError:
        print(f"File {filename} not found for download.")
        return jsonify({'message': 'File not found'}), 404

    finally:
        # Clean up the temporary file after sending 
        if os.path.exists(temp_path):
            os.remove(temp_path)

# Run the Flask App
if __name__ == '__main__':
    app.run(debug=True);
