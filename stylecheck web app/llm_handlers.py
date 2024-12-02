# Import necessary libraries
import os
from mistralai import Mistral
import anthropic
import google.generativeai as genai
from openai import OpenAI
import re
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# regex to extract the corrected sentence
def extract_correction(text):
    """Extract the corrected sentence from within double curly braces."""
    match = re.search(r'{{(.+?)}}', text)
    if match:
        return match.group(1).strip()
    return None

# 3 LLM handlers
def get_mistral_correction(sentence):
    """Get correction from Mistral AI"""
    try:
        client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))
        chat_response = client.chat.complete(
            model="mistral-large-latest",
            messages=[
                {
                    "role": "system",
                    "content": """Given a sentence, your task is to help correct it's grammar and style. First, think about how to correct it and then return only one final corrected sentence within double curly braces.

Example Input: She don't likes pizza no more.
Your output: Reasoning followed by {{She doesn't like pizza anymore.}}"""
                },
                {
                    "role": "user",
                    "content": f"Sentence: {sentence}"
                }
            ]
        )
        response_text = chat_response.choices[0].message.content
        print(f"Mistral Response: {response_text}")
        return extract_correction(response_text)
    except Exception as e:
        print(f"Mistral AI returned Error: {str(e)}")
        return None


def get_anthropic_correction(sentence):
    """Get correction from Anthropic Claude"""
    try:
        client = anthropic.Anthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY"),
        )

        message = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=2808,
            temperature=0.1,
            system="Given a sentence, your task is to help correct it's grammar and style. First, think about how to correct it and then return only one final corrected sentence within double curly braces.\n\nExample Input: She don't likes pizza no more.\nYour output: Reasoning followed by {{She doesn't like pizza anymore.}}",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"Sentence: {sentence}"
                        }
                    ]
                }
            ]
        )
        response_text = message.content[0].text
        print(f"Anthropic Response: {response_text}")
        return extract_correction(response_text)
    except Exception as e:
        print(f"Anthropic returned Error: {str(e)}")
        return None


def get_gemini_correction(sentence):
    """Get correction from Gemini"""
    try:
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

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
            system_instruction="Given a sentence, your task is to help correct it's grammar and style. First, think about how to correct it and then return only one final corrected sentence within double curly braces.\n\nExample Input: She don't likes pizza no more.\nYour output: Reasoning followed by {{She doesn't like pizza anymore.}}",
        )

        chat_session = model.start_chat(history=[])
        response = chat_session.send_message(f"Sentence: {sentence}")
        response_text = response.text
        print(f"Gemini Response: {response_text}")
        return extract_correction(response_text)

    except Exception as e:
        print(f"Gemini returned Error: {str(e)}")
        return None


# OpenAI LLM call
def get_openai_final_corrections(original_text, corrections):
    """Get final corrections from OpenAI"""
    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Format the corrections for OpenAI input
        corrections_str = str(corrections)
        
        response = client.chat.completions.create(
            model="gpt-4o-mini", 
            messages=[
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "text",
                            "text": "Review and correct grammar or style issues found in an English sentence, considering reasoning and corrections proposed by multiple language experts. Return a final response in JSON format, with details for each specific correction.\n\n# Output Format\nThe output should be a JSON array where each element contains a structured JSON object with the following fields:\n- `\"original\"`: The incorrect word or phrase.\n- `\"corrected\"`: The corrected version of the word or phrase.\n- `\"explanation\"`: The reasoning behind the correction based on the experts' analysis.\n\nFor the entire sentence, include additional fields summarizing the final correction:\n- `\"original_phrase\"`: The original input sentence.\n- `\"corrected_phrase\"`: The corrected version of the entire sentence with all corrections applied.\n- `\"overall_explanation\"`: A summary of the reasoning behind the final corrected phrase.\n\n# Example\n**Input**: \"She don't like the dogs.\"\n\n**Experts' Responses**:\n1. Expert 1: Corrected it to \"She doesn't like the dogs.\" - Incorrect auxiliary verb usage.\n2. Expert 2: Suggested \"She does not like dogs.\" - Grammar problem and improved style.\n3. Expert 3: Changed it to \"She doesn't enjoy dogs.\" - Auxiliary verb and rephrased slightly for stylistic effect.\n\nOutput (JSON):\n```json\n[\n  {\n    \"original\": \"don't\",\n    \"corrected\": \"doesn't\",\n    \"explanation\": \"The auxiliary verb 'don't' is incorrect for third-person singular; it should be 'doesn't'.\"\n  },\n  {\n    \"original\": \"the dogs\",\n    \"corrected\": \"dogs\",\n    \"explanation\": \"The determiner 'the' was removed to generalize the statement per Expert 2's suggestion.\"\n  },\n  {\n    \"original_phrase\": \"She don't like the dogs.\",\n    \"corrected_phrase\": \"She doesn't like dogs.\",\n    \"overall_explanation\": \"The auxiliary verb was corrected, and the determiner was removed for generalization, balancing grammatical correctness and style based on the experts' feedback.\"\n  }\n]\n```"
                        }
                    ]
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"Sentence: {original_text}\n\nReceived corrections from Experts: {corrections_str}"
                        }
                    ]
                }
            ],
            response_format={"type": "json_object"},
            temperature=0.1,
            max_tokens=2048,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        
        response_text = response.choices[0].message.content
        print(f"OpenAI Response: {response_text}")
        return json.loads(response_text)
    except Exception as e:
        print(f"OpenAI returned Error: {str(e)}")
        return None


def get_all_corrections(sentence):
    """Get corrections from all LLMs and final analysis from OpenAI"""
    corrections = []
    
    # Get corrections from each LLM
    mistral_correction = get_mistral_correction(sentence)
    if mistral_correction:
        corrections.append(("Mistral", mistral_correction))
    
    anthropic_correction = get_anthropic_correction(sentence)
    if anthropic_correction:
        corrections.append(("Anthropic", anthropic_correction))
    
    gemini_correction = get_gemini_correction(sentence)
    if gemini_correction:
        corrections.append(("Gemini", gemini_correction))
    
    # Get final analysis from OpenAI
    if corrections:
        final_corrections = get_openai_final_corrections(sentence, corrections)
        if final_corrections:
            return final_corrections
    
    return None
