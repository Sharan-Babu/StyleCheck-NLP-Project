import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from llm_integrations import get_all_corrections

class StyleCheckEvaluator:
    def __init__(self):
        pass
    
    def get_correction(self, text):
        """Get correction from StyleCheck system"""
        try:
            # Get corrections from all LLMs
            correction_result = get_all_corrections(text)
            
            if correction_result and "corrected_phrase" in correction_result:
                return correction_result["corrected_phrase"]
            
            return text  # Return original text if correction fails
            
        except Exception as e:
            print(f"Error getting StyleCheck correction: {str(e)}")
            return text  # Return original text on error
    
    def get_detailed_analysis(self, text):
        """Get detailed analysis including corrections and explanations"""
        try:
            correction_result = get_all_corrections(text)
            
            if correction_result:
                return {
                    "corrected_text": correction_result.get("corrected_phrase", text),
                    "corrections": correction_result.get("corrections", []),
                    "overall_explanation": correction_result.get("overall_explanation", "")
                }
            
            return {
                "corrected_text": text,
                "corrections": [],
                "overall_explanation": "No corrections available"
            }
            
        except Exception as e:
            print(f"Error getting detailed analysis: {str(e)}")
            return {
                "corrected_text": text,
                "corrections": [],
                "overall_explanation": f"Error: {str(e)}"
            }
