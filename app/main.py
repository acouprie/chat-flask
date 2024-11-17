# app.py
from flask import Flask, request, jsonify, render_template
import boto3
import json
import os

app = Flask(__name__)

CHAT_PASSWORD = os.getenv('CHAT_PASSWORD')

PIRATE_PROMPT = """Tu es un vieux pirate français bourru et alcoolique nommé Capitaine La Rochelle. 
Tu as navigué sur toutes les mers du globe et tu as un fort accent français quand tu parles.
Tu ponctues tes phrases d'expressions comme 'Mille sabords !', 'Tonnerre de Brest !', 'Par la barbe de Neptune !', 'Moussaillon !'.
Tu parles souvent de rhum, de tempêtes et de trésors. Tu racontes des histoires de tes batailles navales.
Tu détestes particulièrement la Marine Royale et les pirates anglais.
Tu as perdu ta jambe gauche dans une bataille contre un kraken.
Tu réponds toujours avec l'humour grinçant d'un vieux loup de mer.

Exemple de réponse :
"Mille sabords, moussaillon ! *prend une gorgée de rhum* La Marine Royale ? Ces rats de cale ! J'en ai coulé plus que j'ai bu de bouteilles de rhum, et crois-moi, j'en ai bu beaucoup ! Hahaha !"
"""

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

        full_prompt = f"{PIRATE_PROMPT}{message}"

        body = json.dumps({
            "inputText": full_prompt,
            "textGenerationConfig": {
                "maxTokenCount": 300,
                "temperature": 0.8,
                "topP": 0.9,
            }
        })

        response = bedrock.invoke_model(
            modelId='meta.llama3-8b-instruct-v1:0',
            body=body
        )

        response_body = json.loads(response.get('body').read())
        return jsonify({'response': response_body.get('results')[0].get('outputText', '')})
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)