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
cred = credentials.Certificate(json.loads(os.getenv("FIREBASE_ADMIN_KEY")))

try:
    firebase_admin_key = os.environ.get("FIREBASE_ADMIN_KEY")
    cred = credentials.Certificate(json.loads(firebase_admin_key))
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
    print("Error loading Firebase Admin key:", e)
if __name__ == '__main__':
    app.run(debug=True)