# StyleCheck

An AI-powered grammar and style correction tool for ESL (English as Second Language) learners. StyleCheck leverages multiple Language Models to provide comprehensive feedback on writing.

## Features
- Real-time grammar and style corrections
- Detailed explanations for each correction
- Multi-LLM architecture for enhanced accuracy
- Clean and modern web interface

## Setup
1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file with your API keys:
```
ANTHROPIC_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here
MISTRAL_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
```

3. Run the application:
```bash
python app.py
```

## Architecture
- Frontend: HTML, CSS, JavaScript
- Backend: Flask (Python)
- LLM Integration: Mistral, Anthropic Claude, Google Gemini, OpenAI GPT-4o
- Processing: Multi-stage correction pipeline with consensus-based final output
