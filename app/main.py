# app.py
from flask import Flask, request, jsonify, render_template
import boto3
import json
import os

app = Flask(__name__)

CHAT_PASSWORD = os.getenv('CHAT_PASSWORD')
# Initialize Bedrock client
bedrock = boto3.client(
    service_name='bedrock-runtime',
    region_name='us-east-1',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)

def validate_password(password):
    return password == CHAT_PASSWORD

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        password = data.get('password', '')
        if not validate_password(password):
            return jsonify({'error': 'Invalid password'}), 401
        message = data.get('message', '')

        body = json.dumps({
            "inputText": message,
            "textGenerationConfig": {
                "maxTokenCount": 500,
                "temperature": 0.7,
                "topP": 0.9,
            }
        })

        response = bedrock.invoke_model(
            modelId='amazon.titan-text-express-v1',
            body=body
        )

        response_body = json.loads(response.get('body').read())
        return jsonify({'response': response_body.get('results')[0].get('outputText', '')})
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)