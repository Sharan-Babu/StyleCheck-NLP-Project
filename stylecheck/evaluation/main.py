import pandas as pd
from transformers import T5ForConditionalGeneration, T5Tokenizer
import torch
from nltk.translate.gleu_score import sentence_gleu
import re
from models.stylecheck_eval import StyleCheckEvaluator
import json
from datetime import datetime
import numpy as np
import os
import textstat

class GrammarEvaluator:
    def __init__(self):
        print("Initializing evaluation system...")
        
        # Initialize T5
        print("Loading T5 model...")
        self.t5_tokenizer = T5Tokenizer.from_pretrained('t5-base')
        self.t5_model = T5ForConditionalGeneration.from_pretrained('t5-base')
        
        # Initialize StyleCheck
        print("Initializing StyleCheck...")
        self.stylecheck = StyleCheckEvaluator()
        
        # Load test data
        print("Loading test data...")
        self.test_data = self.load_test_data()
        
        print("Initialization complete!")
    
    def load_test_data(self):
        """Load test sentences from CSV"""
        df = pd.read_csv('evaluation/data/test_sentences.csv')
        return df
    
    def get_t5_correction(self, text):
        """Get correction from T5 model"""
        try:
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.t5_model.to(device)
            
            input_text = f"grammar: {text}"
            input_ids = self.t5_tokenizer.encode(input_text, return_tensors="pt", max_length=512, truncation=True)
            input_ids = input_ids.to(device)
            
            outputs = self.t5_model.generate(
                input_ids=input_ids,
                max_length=512,
                num_beams=4,
                early_stopping=True
            )
            
            corrected = self.t5_tokenizer.decode(outputs[0], skip_special_tokens=True)
            return corrected
            
        except Exception as e:
            print(f"Error in T5 correction: {str(e)}")
            return text
    
    def get_stylecheck_correction(self, text):
        """Get correction from StyleCheck"""
        return self.stylecheck.get_correction(text)
    
    def calculate_gleu(self, reference, candidate):
        """Calculate GLEU score between reference and candidate sentence"""
        reference_tokens = reference.lower().split()
        candidate_tokens = candidate.lower().split()
        return sentence_gleu([reference_tokens], candidate_tokens)
    
    def calculate_readability_metrics(self, text):
        """Calculate various readability metrics"""
        metrics = {
            'flesch_kincaid_grade': textstat.flesch_kincaid_grade(text),
            'flesch_reading_ease': textstat.flesch_reading_ease(text),
            'gunning_fog': textstat.gunning_fog(text),
            'smog_index': textstat.smog_index(text),
            'automated_readability_index': textstat.automated_readability_index(text),
            'coleman_liau_index': textstat.coleman_liau_index(text),
            'linsear_write_formula': textstat.linsear_write_formula(text),
            'dale_chall_readability_score': textstat.dale_chall_readability_score(text)
        }
        return metrics
    
    def evaluate_corrections(self):
        """Run evaluation on test cases"""
        results_file = 'evaluation/results/evaluation_progress.json'
        detailed_results_file = 'evaluation/results/detailed_results.json'
        
        # Try to load existing results
        try:
            with open(results_file, 'r') as f:
                results = json.load(f)
            with open(detailed_results_file, 'r') as f:
                detailed_results = json.load(f)
            print("\nLoaded existing results")
        except FileNotFoundError:
            # Initialize metrics for both models
            metrics = {
                'flesch_kincaid_grade': 0,
                'flesch_reading_ease': 0,
                'gunning_fog': 0,
                'smog_index': 0,
                'automated_readability_index': 0,
                'coleman_liau_index': 0,
                'linsear_write_formula': 0,
                'dale_chall_readability_score': 0
            }
            
            results = {
                'overall': {
                    't5': {'gleu': 0, 'readability_metrics': metrics.copy()},
                    'stylecheck': {'gleu': 0, 'readability_metrics': metrics.copy()}
                },
                'by_category': {},
                'processed_indices': []
            }
            detailed_results = {
                'test_cases': []
            }
            print("\nStarting new evaluation")
        
        total_cases = len(self.test_data)
        print(f"\nEvaluating {total_cases} test cases...")
        
        try:
            for idx, row in self.test_data.iterrows():
                # Skip if we've already processed this index
                if idx in results.get('processed_indices', []):
                    print(f"\rSkipping already processed case: {idx + 1}/{total_cases}", end='', flush=True)
                    continue
                
                category = row['category']
                original = row['original']
                ground_truth = row['ground_truth']
                
                # Get corrections
                t5_correction = self.get_t5_correction(original)
                stylecheck_correction = self.get_stylecheck_correction(original)
                
                # Calculate metrics
                t5_gleu = self.calculate_gleu(ground_truth, t5_correction)
                t5_readability = self.calculate_readability_metrics(t5_correction)
                stylecheck_gleu = self.calculate_gleu(ground_truth, stylecheck_correction)
                stylecheck_readability = self.calculate_readability_metrics(stylecheck_correction)
                
                # Store detailed results for this test case
                test_case_results = {
                    'index': idx,
                    'category': category,
                    'original': {
                        'text': original,
                        'readability_metrics': self.calculate_readability_metrics(original)
                    },
                    'ground_truth': {
                        'text': ground_truth,
                        'readability_metrics': self.calculate_readability_metrics(ground_truth)
                    },
                    't5': {
                        'correction': t5_correction,
                        'gleu': t5_gleu,
                        'readability_metrics': t5_readability
                    },
                    'stylecheck': {
                        'correction': stylecheck_correction,
                        'gleu': stylecheck_gleu,
                        'readability_metrics': stylecheck_readability
                    }
                }
                detailed_results['test_cases'].append(test_case_results)
                
                # Update overall results
                results['overall']['t5']['gleu'] += t5_gleu
                results['overall']['stylecheck']['gleu'] += stylecheck_gleu
                
                # Initialize readability metrics in overall results if not present
                if 'readability_metrics' not in results['overall']['t5']:
                    results['overall']['t5']['readability_metrics'] = {k: 0 for k in t5_readability.keys()}
                if 'readability_metrics' not in results['overall']['stylecheck']:
                    results['overall']['stylecheck']['readability_metrics'] = {k: 0 for k in stylecheck_readability.keys()}
                
                # Update overall readability metrics
                for metric in t5_readability:
                    results['overall']['t5']['readability_metrics'][metric] += t5_readability[metric]
                    results['overall']['stylecheck']['readability_metrics'][metric] += stylecheck_readability[metric]
                
                # Update category results
                if category not in results['by_category']:
                    results['by_category'][category] = {
                        't5': {'gleu': 0, 'readability_metrics': {k: 0 for k in t5_readability.keys()}, 'count': 0},
                        'stylecheck': {'gleu': 0, 'readability_metrics': {k: 0 for k in stylecheck_readability.keys()}, 'count': 0}
                    }
                
                # Update category metrics
                results['by_category'][category]['t5']['gleu'] += t5_gleu
                results['by_category'][category]['stylecheck']['gleu'] += stylecheck_gleu
                
                for metric in t5_readability:
                    results['by_category'][category]['t5']['readability_metrics'][metric] += t5_readability[metric]
                    results['by_category'][category]['stylecheck']['readability_metrics'][metric] += stylecheck_readability[metric]
                
                results['by_category'][category]['t5']['count'] += 1
                results['by_category'][category]['stylecheck']['count'] += 1
                
                # Mark this index as processed
                if 'processed_indices' not in results:
                    results['processed_indices'] = []
                results['processed_indices'].append(idx)
                
                # Save progress after each test case
                os.makedirs('evaluation/results', exist_ok=True)
                with open(results_file, 'w') as f:
                    json.dump(results, f, indent=2)
                with open(detailed_results_file, 'w') as f:
                    json.dump(detailed_results, f, indent=2)
                
                print(f"\rProcessing: {idx + 1}/{total_cases}", end='', flush=True)
                
        except KeyboardInterrupt:
            print("\n\nEvaluation interrupted. Progress has been saved.")
            return self.print_results(results)
        
        print("\n\nResults:")
        return self.print_results(results)
    
    def print_results(self, results):
        """Print evaluation results"""
        # Count total processed cases
        total_cases = len(results.get('processed_indices', []))
        if total_cases == 0:
            print("No results to display")
            return results
        
        # Calculate averages for overall results
        results['overall']['t5']['gleu'] /= total_cases
        results['overall']['stylecheck']['gleu'] /= total_cases
        
        # Calculate averages for readability metrics
        for model in ['t5', 'stylecheck']:
            for metric in results['overall'][model]['readability_metrics']:
                results['overall'][model]['readability_metrics'][metric] /= total_cases
        
        # Print overall results
        print("\nOverall Results:")
        print(f"T5 Model - GLEU: {results['overall']['t5']['gleu']:.3f}")
        print("T5 Model - Readability Metrics:")
        for metric, value in results['overall']['t5']['readability_metrics'].items():
            print(f"  {metric}: {value:.3f}")
        
        print(f"\nStyleCheck - GLEU: {results['overall']['stylecheck']['gleu']:.3f}")
        print("StyleCheck - Readability Metrics:")
        for metric, value in results['overall']['stylecheck']['readability_metrics'].items():
            print(f"  {metric}: {value:.3f}")
        
        # Calculate and print category results
        print("\nResults by Category:")
        for category in results['by_category']:
            count = results['by_category'][category]['t5']['count']
            if count > 0:
                t5_gleu = results['by_category'][category]['t5']['gleu'] / count
                stylecheck_gleu = results['by_category'][category]['stylecheck']['gleu'] / count
                
                print(f"\n{category}:")
                print(f"T5 Model - GLEU: {t5_gleu:.3f}")
                print("T5 Model - Readability Metrics:")
                for metric in results['by_category'][category]['t5']['readability_metrics']:
                    value = results['by_category'][category]['t5']['readability_metrics'][metric] / count
                    print(f"  {metric}: {value:.3f}")
                
                print(f"\nStyleCheck - GLEU: {stylecheck_gleu:.3f}")
                print("StyleCheck - Readability Metrics:")
                for metric in results['by_category'][category]['stylecheck']['readability_metrics']:
                    value = results['by_category'][category]['stylecheck']['readability_metrics'][metric] / count
                    print(f"  {metric}: {value:.3f}")
        
        return results

if __name__ == "__main__":
    evaluator = GrammarEvaluator()
    results = evaluator.evaluate_corrections()
    evaluator.print_results(results)
