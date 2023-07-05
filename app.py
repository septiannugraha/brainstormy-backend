import os
from flask import request, jsonify, Response, Flask
from elevenlabs import clone, generate, play, set_api_key
import anthropic
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000", "http://example.com"])

set_api_key(os.getenv("XI_API_KEY"))

@app.route('/chat', methods=['POST'])
def generate_chat_response():
    data = request.get_json()  # Get the JSON data from request
    messages = data.get('messages', [])
    prompts = ""
    for message in messages:
        if message['role'] == 'human':
            prompts += f"{anthropic.HUMAN_PROMPT} {message['content']}"
        elif message['role'] == 'assistant':
            prompts += f"{anthropic.AI_PROMPT} {message['content']}"

    prompt = (f"{anthropic.HUMAN_PROMPT} You are my brainstorming partner. I need your help to collaboratively brainstorm some ideas and provide some suggestions according to your best ability. Please try to keep the response concise, as I'll ask follow up questions afterwards"
        f"{anthropic.AI_PROMPT} Understood, I will assist you in brainstorming some ideas together. "
        f"{prompts}")

    c = anthropic.Anthropic(api_key=os.getenv("CLAUDE_KEY"))
    resp = c.completions.create(
        prompt=f"{prompt} {anthropic.AI_PROMPT}",
        stop_sequences=[anthropic.HUMAN_PROMPT],
        model="claude-v1.3-100k",
        max_tokens_to_sample=900,
    )

    print(resp)

    return jsonify({"status": "success", "result": resp.completion})

@app.route('/talk', methods=['POST'])
def generate_speech():
    data = request.get_json()
    message = data.get('message', 'No message provided')

    audio = generate(
        text=message,
        voice="Bella",
        model='eleven_monolingual_v1'
    )

    return Response(audio, mimetype='audio/mpeg')

@app.route('/')
def hello_world():
    return 'Hello, World!'

if __name__ == '__main__':
    app.run(debug=True)
