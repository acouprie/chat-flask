from flask import Flask, request, jsonify, render_template
import boto3
import json
import os

app = Flask(__name__)

CHAT_PASSWORD = os.getenv('CHAT_PASSWORD')

BASE_PIRATE_PROMPT = """Tu es un vieux pirate français bourru et alcoolique nommé Capitaine La Rochelle.
Tu as navigué sur toutes les mers du globe et tu as un fort accent français quand tu parles.
Tu ponctues tes phrases d'expressions comme 'Mille sabords !', 'Tonnerre de Brest !', 'Par la barbe de Neptune !', 'Moussaillon !'.
Tu parles souvent de rhum, de tempêtes et de trésors. Tu racontes des histoires de tes batailles navales.
Tu détestes particulièrement la Marine Royale et les pirates anglais.
Tu as perdu ta jambe gauche dans une bataille contre un kraken.
Tu réponds toujours avec l'humour grinçant d'un vieux loup de mer."""

MODEL_CONFIGS = {
    'titan': {
        'id': 'amazon.titan-text-express-v1',
        'prompt_template': lambda message: [
            {
                "role": "system",
                "content": BASE_PIRATE_PROMPT
            },
            {
                "role": "user",
                "content": message
            }
        ],
        'make_body': lambda prompt: {
            "inputText": json.dumps(prompt),
            "textGenerationConfig": {
                "maxTokenCount": 300,
                "temperature": 0.8,
                "topP": 0.9,
                "stopSequences": ["User:"]
            }
        },
        'get_response': lambda response_body: response_body.get('results')[0].get('outputText', '')
    },
    'llama': {
        'id': 'meta.llama3-8b-instruct-v1:0',
        'prompt_template': lambda message: f"[INST]{BASE_PIRATE_PROMPT}\n\n{message}[/INST]",
        'make_body': lambda prompt: {
            "prompt": prompt,
            "temperature": 0.8,
            "top_p": 0.9,
            "max_gen_len": 300
        },
        'get_response': lambda response_body: response_body.get('generation', '').strip().replace(BASE_PIRATE_PROMPT, '').strip()
    }
}

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
        model_key = data.get('model', 'titan')

        if model_key not in MODEL_CONFIGS:
            return jsonify({'error': 'Invalid model selection'}), 400

        model_config = MODEL_CONFIGS[model_key]
        prompt = model_config['prompt_template'](message)
        body = model_config['make_body'](prompt)

        response = bedrock.invoke_model(
            modelId=model_config['id'],
            body=json.dumps(body)
        )

        response_body = json.loads(response.get('body').read())
        response_text = model_config['get_response'](response_body)

        response_text = response_text.strip()
        if "[INST]" in response_text:
            response_text = response_text.split("[INST]")[-1]
        if "[/INST]" in response_text:
            response_text = response_text.split("[/INST]")[-1]
        
        return jsonify({'response': response_text})
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)