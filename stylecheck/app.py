from flask import Flask, render_template, request, jsonify
from llm_integrations import get_all_corrections
import traceback

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/check', methods=['POST'])
def check_text():
    try:
        text = request.json.get('text', '')
        print(f"\nReceived text for correction: {text}")
        if not text:
            print("Error: Empty text received")
            return jsonify({"error": "No text provided"}), 400
        
        # Get corrections from all LLMs and final OpenAI analysis
        correction_result = get_all_corrections(text)
        print("\nFinal correction result:", correction_result)
        
        if not correction_result:
            print("Error: No correction result returned")
            return jsonify({"error": "Failed to get corrections"}), 500
            
        # Extract corrections and add IDs
        corrections = correction_result.get("corrections", [])
        if not corrections:
            print("Error: No corrections in result")
            return jsonify({"error": "No corrections available"}), 400
            
        for i, correction in enumerate(corrections, 1):
            correction["id"] = i
        
        response_data = {
            "corrections": corrections,
            "corrected_text": correction_result.get("corrected_phrase", ""),
            "overall_explanation": correction_result.get("overall_explanation", "")
        }
        print("\nSending response:", response_data)
        return jsonify(response_data)
        
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"Error in check_text: {str(e)}")
        print(f"Traceback: {error_trace}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
