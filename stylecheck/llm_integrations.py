import os
from mistralai import Mistral
import anthropic
import google.generativeai as genai
from openai import OpenAI
from dotenv import load_dotenv
import re
import json

# Load environment variables
load_dotenv()

def extract_correction(response_text):
    """Extract the corrected sentence from within double curly braces."""
    match = re.search(r'\{\{(.*?)\}\}', response_text)
    if match:
        return match.group(1).strip()
    return None

def get_mistral_correction(text):
    """Get correction from Mistral AI."""
    try:
        client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))
        chat_response = client.chat.complete(
            model="mistral-large-latest",
            messages=[
                {
                    "role": "system",
                    "content": """Given a sentence, your task is to help correct it's grammar and style. First, think about how to correct it and then return the final corrected sentence within double curly braces.

Example Input: She don't likes pizza no more.
Your output: Reasoning followed by {{She doesn't like pizza anymore.}}"""
                },
                {
                    "role": "user",
                    "content": f"Sentence: {text}"
                }
            ]
        )
        response_text = chat_response.choices[0].message.content
        print(f"Mistral Response: {response_text}")
        return extract_correction(response_text)
    except Exception as e:
        print(f"Error with Mistral AI: {str(e)}")
        return None

def get_anthropic_correction(text):
    """Get correction from Anthropic's Claude."""
    try:
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        message = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=2808,
            temperature=0.1,
            system="Given a sentence, your task is to help correct it's grammar and style. First, think about how to correct it and then return the final corrected sentence within double curly braces.\n\nExample Input: She don't likes pizza no more.\nYour output: Reasoning followed by {{She doesn't like pizza anymore.}}",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"Sentence: {text}"
                        }
                    ]
                }
            ]
        )
        response_text = message.content[0].text
        print(f"Anthropic Response: {response_text}")
        return extract_correction(response_text)
    except Exception as e:
        print(f"Error with Anthropic: {str(e)}")
        return None

def get_gemini_correction(text):
    """Get correction from Google's Gemini."""
    try:
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        
        generation_config = {
            "temperature": 0.1,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
            "response_mime_type": "text/plain",
        }

        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config=generation_config,
            system_instruction="Given a sentence, your task is to help correct it's grammar and style. First, think about how to correct it and then return the final corrected sentence within double curly braces.\n\nExample Input: She don't likes pizza no more.\nYour output: Reasoning followed by {{She doesn't like pizza anymore.}}",
        )

        chat_session = model.start_chat(history=[])
        response = chat_session.send_message(f"Sentence: {text}")
        response_text = response.text
        print(f"Gemini Response: {response_text}")
        return extract_correction(response_text)
    except Exception as e:
        print(f"Error with Gemini: {str(e)}")
        return None

def get_final_correction(text, llm_corrections):
    """Get final correction from OpenAI, considering all LLM responses."""
    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Format the corrections for OpenAI input
        corrections_str = str([(name, corr) for name, corr in llm_corrections])
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Review and correct grammar or style issues found in an English sentence, considering reasoning and corrections proposed by multiple language experts. Return a final response in JSON format, with details for each specific correction.\n\n# Output Format\nThe output should be a JSON array where each element contains a structured JSON object with the following fields:\n- `\"original\"`: The incorrect word or phrase.\n- `\"corrected\"`: The corrected version of the word or phrase.\n- `\"explanation\"`: The reasoning behind the correction based on the experts' analysis.\n\nFor the entire sentence, include additional fields summarizing the final correction:\n- `\"original_phrase\"`: The original input sentence.\n- `\"corrected_phrase\"`: The corrected version of the entire sentence with all corrections applied.\n- `\"overall_explanation\"`: A summary of the reasoning behind the final corrected phrase.\n"
                },
                {
                    "role": "user",
                    "content": f"Sentence: {text}\n\nReceived corrections from Experts: {corrections_str}"
                }
            ],
            response_format={"type": "json_object"},
            temperature=0.1,
            max_tokens=2048,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        
        final_response = json.loads(response.choices[0].message.content)
        print(f"OpenAI Final Response: {json.dumps(final_response, indent=2)}")
        return final_response
    except Exception as e:
        print(f"Error with OpenAI: {str(e)}")
        return None

def get_all_corrections(text):
    """Get corrections from all LLMs."""
    corrections = []
    
    # Get corrections from each LLM
    mistral_correction = get_mistral_correction(text)
    if mistral_correction:
        corrections.append(("Mistral", mistral_correction))
    
    anthropic_correction = get_anthropic_correction(text)
    if anthropic_correction:
        corrections.append(("Anthropic", anthropic_correction))
    
    gemini_correction = get_gemini_correction(text)
    if gemini_correction:
        corrections.append(("Gemini", gemini_correction))
    
    # If we have corrections, get final analysis from OpenAI
    if corrections:
        return get_final_correction(text, corrections)
    
    return None
