# Import necessary libraries
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from llm_handlers import get_all_corrections

# Initialize Flask app and routes
app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/check', methods=['POST'])
def check_text():
    text = request.json.get('text', '').strip()
    
    if not text:
        return jsonify({
            "error": "Please provide some text to check."
        }), 400
    
    # Get corrections from all LLMs and final analysis from OpenAI
    corrections_data = get_all_corrections(text)
    
    if not corrections_data:
        return jsonify({
            "error": "Failed to get corrections from LLMs."
        }), 500
    
    return jsonify(corrections_data)

if __name__ == '__main__':
    app.run(debug=True)
