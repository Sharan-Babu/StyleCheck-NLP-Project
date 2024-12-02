import json
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import os

def load_results():
    """Load evaluation results from JSON files"""
    with open('evaluation/results/evaluation_progress.json', 'r') as f:
        summary_results = json.load(f)
    with open('evaluation/results/detailed_results.json', 'r') as f:
        detailed_results = json.load(f)
    return summary_results, detailed_results

def create_gleu_comparison(results, save_dir):
    """Create GLEU score comparison chart"""
    plt.figure(figsize=(10, 6))
    
    # Overall GLEU scores
    models = ['T5', 'StyleCheck']
    gleu_scores = [
        results['overall']['t5']['gleu'],
        results['overall']['stylecheck']['gleu']
    ]
    
    # Create bar plot
    plt.bar(models, gleu_scores)
    plt.title('GLEU Score Comparison')
    plt.ylabel('GLEU Score')
    plt.ylim(0, 1.0) 
    
    # Adding value labels on top of bars
    for i, v in enumerate(gleu_scores):
        plt.text(i, v + 0.01, f'{v:.3f}', ha='center')
    
    plt.savefig(os.path.join(save_dir, 'gleu_comparison.png'))
    plt.close()


def create_readability_comparison(results, save_dir):
    """Create readability metrics comparison chart"""
    metrics = list(results['overall']['t5']['readability_metrics'].keys())
    t5_scores = [results['overall']['t5']['readability_metrics'][m] for m in metrics]
    stylecheck_scores = [results['overall']['stylecheck']['readability_metrics'][m] for m in metrics]
    
    # Create DataFrame for plotting
    df = pd.DataFrame({
        'Metric': metrics + metrics,
        'Score': t5_scores + stylecheck_scores,
        'Model': ['T5']*len(metrics) + ['StyleCheck']*len(metrics)
    })
    
    # Create grouped bar plot
    plt.figure(figsize=(15, 8))
    sns.barplot(data=df, x='Metric', y='Score', hue='Model')
    plt.title('Readability Metrics Comparison')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    plt.savefig(os.path.join(save_dir, 'readability_comparison.png'))
    plt.close()

def create_category_performance(results, save_dir):
    """Create category-wise performance comparison chart"""
    categories = list(results['by_category'].keys())
    t5_scores = []
    stylecheck_scores = []
    
    for category in categories:
        count = results['by_category'][category]['t5']['count']
        t5_scores.append(results['by_category'][category]['t5']['gleu'] / count)
        stylecheck_scores.append(results['by_category'][category]['stylecheck']['gleu'] / count)
    
    # Create DataFrame for plotting
    df = pd.DataFrame({
        'Category': categories + categories,
        'GLEU Score': t5_scores + stylecheck_scores,
        'Model': ['T5']*len(categories) + ['StyleCheck']*len(categories)
    })
    
    # Create grouped bar plot
    plt.figure(figsize=(12, 6))
    sns.barplot(data=df, x='Category', y='GLEU Score', hue='Model')
    plt.title('Category-wise GLEU Score Comparison')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    plt.savefig(os.path.join(save_dir, 'category_performance.png'))
    plt.close()


def create_readability_distribution(detailed_results, save_dir):
    """Create readability score distribution plot"""
    # Extract readability scores for each test case
    metrics = list(detailed_results['test_cases'][0]['t5']['readability_metrics'].keys())
    
    for metric in metrics:
        t5_scores = [case['t5']['readability_metrics'][metric] for case in detailed_results['test_cases']]
        stylecheck_scores = [case['stylecheck']['readability_metrics'][metric] for case in detailed_results['test_cases']]
        
        plt.figure(figsize=(10, 6))
        plt.hist(t5_scores, alpha=0.5, label='T5', bins=20)
        plt.hist(stylecheck_scores, alpha=0.5, label='StyleCheck', bins=20)
        plt.title(f'{metric} Distribution')
        plt.xlabel('Score')
        plt.ylabel('Frequency')
        plt.legend()
        plt.tight_layout()
        
        plt.savefig(os.path.join(save_dir, f'readability_dist_{metric}.png'))
        plt.close()


def create_improvement_analysis(detailed_results, save_dir):
    """Create analysis of improvements made by each model"""
    # Calculate improvement in readability for each test case
    improvements_t5 = []
    improvements_stylecheck = []
    
    for case in detailed_results['test_cases']:
        original_flesch = case['original']['readability_metrics']['flesch_reading_ease']
        t5_flesch = case['t5']['readability_metrics']['flesch_reading_ease']
        stylecheck_flesch = case['stylecheck']['readability_metrics']['flesch_reading_ease']
        
        improvements_t5.append(t5_flesch - original_flesch)
        improvements_stylecheck.append(stylecheck_flesch - original_flesch)
    
    plt.figure(figsize=(10, 6))
    plt.scatter(range(len(improvements_t5)), improvements_t5, alpha=0.5, label='T5')
    plt.scatter(range(len(improvements_stylecheck)), improvements_stylecheck, alpha=0.5, label='StyleCheck')
    plt.axhline(y=0, color='r', linestyle='--')
    plt.title('Readability Improvements per Test Case')
    plt.xlabel('Test Case')
    plt.ylabel('Change in Flesch Reading Ease')
    plt.legend()
    plt.tight_layout()
    
    plt.savefig(os.path.join(save_dir, 'improvement_analysis.png'))
    plt.close()

def main():
    # Create charts directory if it doesn't exist
    save_dir = 'evaluation/charts'
    os.makedirs(save_dir, exist_ok=True)
    
    # Load results
    summary_results, detailed_results = load_results()
    
    # Create visualizations
    print("Creating GLEU comparison chart...")
    create_gleu_comparison(summary_results, save_dir)
    
    print("Creating readability comparison chart...")
    create_readability_comparison(summary_results, save_dir)
    
    print("Creating category performance chart...")
    create_category_performance(summary_results, save_dir)
    
    print("Creating readability distribution plots...")
    create_readability_distribution(detailed_results, save_dir)
    
    print("Creating improvement analysis chart...")
    create_improvement_analysis(detailed_results, save_dir)
    
    print("\nAll visualizations have been created and saved in the 'evaluation/charts' directory.")

if __name__ == "__main__":
    main()
