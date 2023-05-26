from flask import Flask, request, Response
import json
import requests
import os
from dotenv import load_dotenv
import binascii
import jwt

from ecdsa import SigningKey, SECP256k1
load_dotenv()

app=Flask(__name__)

@app.route("/upload-image-to-deso", methods=["POST"])
def upload_image_to_deso():
    try:
        if 'file' not in request.files:
            return Response(
                response=json.dumps({"message": "No file part"}),
                status=500,
                mimetype='application/json'
            )
        file = request.files['file']
        if file.filename == '':
            return Response(
                response=json.dumps({"message": "No selected file"}),
                status=500,
                mimetype='application/json'
            )

        file.save('uploads/' + file.filename)
        file_path = 'uploads/' + file.filename

        tempFile = open(file_path, "rb")
        imageFileList = [
            ('file', ('screenshot.jpg', tempFile, 'image/png'))]
        jwt_ = getDeSoJWT(os.getenv('EVENTER_SEED_HEX'))
        endpointURL = "https://node.deso.org/api/v0/upload-image"
        payload = {
            "UserPublicKeyBase58Check": os.getenv('EVENTER_PUBLIC_KEY'),
            "JWT": jwt_,
        }

        response = requests.post(
            endpointURL, data=payload, files=imageFileList)

        # close the file
        file.close()
        tempFile.close()

        # delete the file saved in uploads folder
        if os.path.exists(file_path):
            os.remove(file_path)
        else:
            print("File not found.")
        return response.json()

    except Exception as e:
        return Response(
            response=json.dumps(
                {"message": "Error uploading Image", "exception": e.args}),
            status=500,
            mimetype='application/json'
        )
    
@app.route("/scrapbook", methods=["POST","GET"])
def getDeSoJWT(seedHex):
    # returns JWT token of user that helps in public key validation in backend
    private_key = bytes(seedHex, "utf-8")
    private_key = binascii.unhexlify(private_key)
    key = SigningKey.from_string(private_key, curve=SECP256k1)
    key = key.to_pem()
    encoded_jwt = jwt.encode({}, key, algorithm="ES256")
    return encoded_jwt