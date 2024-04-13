import os
import json
import firebase_admin
from flask import Flask, jsonify, render_template, request
from firebase_admin import credentials, storage, initialize_app
from flask_cors import CORS
from dotenv import load_dotenv
import pandas as pd
from io import StringIO

load_dotenv()
app = Flask(__name__)
CORS(app, origins=["*"])
app.config['TEMPLATES_AUTO_RELOAD'] = True

def product_preference_analysis(dataset):
    # Example: Count the occurrences of each product
    product_counts = dataset['product'].value_counts()

    # Convert to list of dictionaries
    result_list = [{'product': product, 'count': count} for product, count in product_counts.items()]

    return result_list

def sales_analysis(dataset):
    # Example: Calculate total sales and average sale
    total_sales = dataset['sale'].sum()
    average_sale = dataset['sale'].mean()
    return total_sales,average_sale

def customer_behavior_analysis(dataset):
    # Example: Analyze customer behavior by counting the number of unique customers
    unique_customers = dataset['customer'].nunique()
    return unique_customers

def temporal_analysis(dataset):
    # Example: Analyze temporal patterns by calculating monthly sales and unit price for each product
    dataset['date'] = pd.to_datetime(dataset['date'])
    dataset['month_year'] = dataset['date'].dt.to_period('M')
    
    result = []

    for period, group in dataset.groupby('month_year'):
        monthly_sales_unit_price = group.groupby('product').agg({'sale': 'sum', 'unit_price': 'mean'}).reset_index()
        
        monthly_data = []
        for _, row in monthly_sales_unit_price.iterrows():
            monthly_data.append({'product': row['product'], 'sale': row['sale'], 'unit_price': row['unit_price']})
        
        result.append({'month': str(period), 'monthly_sale': monthly_data})

    return result

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
        "client_x509_cert_url": os.environ.get("AUTH_PROVIDER_X509_CERT_URL")
    }
    cred = credentials.Certificate(credential)
   
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
        
    @app.route('/api/receive_string', methods=['POST'])
    def receive_string():
        data = request.json  # Assuming data is sent in JSON format
        if 'my_string' in data:
            received_string = data['my_string']
            file_path = received_string
            # Process the received string as needed
            # result = {'message': f'Success! Received string: {received_string}'}
            try:
                bucket_name = "analytixnexa.appspot.com" 
                bucket = storage.bucket(bucket_name)
                blob = bucket.blob(file_path)
                if blob.exists():
                    content = blob.download_as_text()

                    # Convert content to DataFrame
                    df = pd.read_csv(StringIO(content))
                    
                    response = jsonify({
                        "product_preference_analysis": {
                            "product_count": product_preference_analysis(df)
                        },
                        "sale_analysis": {
                            "total_sale": int(sales_analysis(df)[0]),
                            "average_sale": int(sales_analysis(df)[1])
                        },
                        "customer_behavior_analysis": {
                            "unique_customer": customer_behavior_analysis(df)
                        },
                        "temporal_analysis": {
                            "temporal_analysis": temporal_analysis(df)
                        }
                        
                    })
                    # response = jsonify({"message": f"File '{file_path}' exists in Firebase Storage"})
                    return response, 200
                else:
                    response = jsonify({"message": f"File '{file_path}' does not exist in Firebase Storage"})
                    return response, 404  # Not Found
            except Exception as e:
                return jsonify({"error": str(e)}), 500  # Internal Server Error
        else:
            return jsonify({'error': 'Missing or invalid data'}), 400
except Exception as e:
    @app.route('/')
    def home():
        return render_template('home.html')
    
    print("Error loading Firebase Admin key:", e)
if __name__ == '__main__':
    app.run(debug=True)
