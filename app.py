import os
import json
import firebase_admin
from flask import Flask, jsonify, render_template
from firebase_admin import credentials, storage, initialize_app
from flask_cors import CORS


app = Flask(__name__)
CORS(app, origins=["*"])
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Initialize Firebase Admin SDK


try:
    credential = {
        "type": "service_account",
        "project_id": "analytixnexa",
        "private_key_id": os.environ.get("PRIVATE_KEY_ID"),
        "private_key": os.environ.get("PRIVATE_KEY").replace(r'\n', '\n'),  # CHANGE HERE
        "client_email": os.environ.get("CLIENT_EMAIL"),
        "client_id": os.environ.get("CLIENT_ID"),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": os.environ.get("AUTH_PROVIDER_X509_CERT_URL"),
        "client_x509_cert_url": os.environ.get("CLIENT_X509_CERT_URL")
    }
    cred = credentials.Certificate(credential)
    # cred = credentials.Certificate("./key.json")
        
    # firebase_admin.initialize_app(cred)

    firebase_admin.initialize_app(cred, {"storageBucket": "analytixnexa.appspot.com"})

    def list_files(bucket_name):
        """Lists all files in the specified Firestore Storage bucket."""
        bucket = storage.bucket(bucket_name)
        blobs = bucket.list_blobs()

        file_names = [blob.name for blob in blobs]
        return file_names


    @app.route('/')
    def home():
        return render_template('home.html')
        


    @app.route('/api/list_files', methods=['GET'])
    def api_list_files():
        try:
            # Replace 'your-firebase-storage-bucket-url' with your actual Firestore Storage bucket URL
            bucket_name = "analytixnexa.appspot.com"
            
            
            # List all file names in the Firestore Storage bucket
            file_names = list_files(bucket_name)
            
            if len(file_names) == 0:
                response = jsonify({"message":"No files"})
                
                return response,200

            response = jsonify({"file_names": file_names})
            
            # Return the list of file names as JSON response
            return response, 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
except Exception as e:
    @app.route('/')
    def home():
        return render_template('error.html')
    @app.route('/bad')
    def bad():
        credential = {
        "type": "service_account",
        "project_id": "analytixnexa",
        "private_key_id": os.environ.get("PRIVATE_KEY_ID").strip("'"),
        "private_key": os.environ.get("PRIVATE_KEY").replace('\n', '\n').strip("'"),  # CHANGE HERE
        "client_email": os.environ.get("CLIENT_EMAIL").strip("'"),
        "client_id": os.environ.get("CLIENT_ID").strip("'"),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": os.environ.get("AUTH_PROVIDER_X509_CERT_URL").strip("'"),
        "client_x509_cert_url": os.environ.get("CLIENT_X509_CERT_URL").strip("'")
        }
        return credential
    
    print("Error loading Firebase Admin key:", e)
if __name__ == '__main__':
    app.run(debug=True)