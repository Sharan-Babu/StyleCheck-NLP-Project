import json
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import os

def load_evaluation_results():
    """Load evaluation results from JSON file"""
    with open('results/evaluation_progress.json', 'r') as f:
        return json.load(f)

def create_overall_gleu_visualization(results, save_dir):
    """Create overall GLEU score comparison visualization"""
    # Set style and colors
    sns.set_theme(style="whitegrid")
    colors = ["#2ecc71", "#3498db"]  # Green and Blue
    
    # Prepare data
    overall_data = {
        'Model': ['T5', 'StyleCheck'],
        'GLEU Score': [
            results['overall']['t5']['gleu'],
            results['overall']['stylecheck']['gleu']
        ]
    }
    df = pd.DataFrame(overall_data)
    
    # Create figure
    plt.figure(figsize=(10, 6))
    ax = sns.barplot(data=df, x='Model', y='GLEU Score', palette=colors)
    
    # Customize plot
    plt.title('Overall GLEU Score Comparison', fontsize=14, pad=20)
    plt.ylabel('GLEU Score', fontsize=12)
    plt.xlabel('Model', fontsize=12)
    
    # Add value labels
    for i, v in enumerate(df['GLEU Score']):
        ax.text(i, v + 0.5, f'{v:.2f}', ha='center', fontsize=11)
    
    # Set y-axis limits with some padding
    plt.ylim(0, max(df['GLEU Score']) * 1.2)
    
    # Save plot
    plt.savefig(os.path.join(save_dir, 'overall_gleu_scores.png'), 
                dpi=300, bbox_inches='tight')
    plt.close()

def create_category_gleu_visualization(results, save_dir):
    """Create category-wise GLEU score visualization"""
    # Set style and colors
    sns.set_theme(style="whitegrid")
    colors = ["#2ecc71", "#3498db"]  # Green and Blue
    
    # Prepare data
    categories = list(results['by_category'].keys())
    category_data = {
        'Category': [],
        'GLEU Score': [],
        'Model': []
    }
    
    for category in categories:
        category_data['Category'].extend([category, category])
        category_data['GLEU Score'].extend([
            results['by_category'][category]['t5']['gleu'] / results['by_category'][category]['t5']['count'],
            results['by_category'][category]['stylecheck']['gleu'] / results['by_category'][category]['stylecheck']['count']
        ])
        category_data['Model'].extend(['T5', 'StyleCheck'])
    
    df = pd.DataFrame(category_data)
    
    # Create figure
    plt.figure(figsize=(12, 6))
    ax = sns.barplot(
        data=df,
        x='Category',
        y='GLEU Score',
        hue='Model',
        palette=colors
    )
    
    # Customize plot
    plt.title('Category-wise GLEU Score Comparison', fontsize=14, pad=20)
    plt.ylabel('GLEU Score', fontsize=12)
    plt.xlabel('Category', fontsize=12)
    
    # Rotate x-axis labels
    plt.xticks(rotation=45, ha='right')
    
    # Add value labels
    for i, v in enumerate(df['GLEU Score']):
        x = i // 2  # Calculate x position
        offset = -0.2 if i % 2 == 0 else 0.2  # Offset for T5 vs StyleCheck
        ax.text(x + offset, v + 0.5, f'{v:.2f}', ha='center', fontsize=9)
    
    # Adjust legend
    plt.legend(title='Model', bbox_to_anchor=(1.05, 1), loc='upper left')
    
    # Set y-axis limits with some padding
    plt.ylim(0, max(df['GLEU Score']) * 1.2)
    
    # Save plot
    plt.savefig(os.path.join(save_dir, 'category_gleu_scores.png'), 
                dpi=300, bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    # Ensure we're in the correct directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Create charts directory if it doesn't exist
    charts_dir = 'charts'
    os.makedirs(charts_dir, exist_ok=True)
    
    # Load results and create visualizations
    results = load_evaluation_results()
    create_overall_gleu_visualization(results, charts_dir)
    create_category_gleu_visualization(results, charts_dir)
    print("GLEU score visualizations have been created successfully!")