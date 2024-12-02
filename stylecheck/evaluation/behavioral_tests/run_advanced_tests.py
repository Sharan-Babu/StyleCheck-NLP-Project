import os
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import f1_score, precision_score, recall_score
from test_suite import BehavioralTestSuite
from mock_llm import get_all_corrections

def create_model_corrector():
    """Create a wrapper for the model correction function"""
    def model_corrector(text: str) -> str:
        correction_result = get_all_corrections(text)
        return correction_result.get("corrected_phrase", text)
    return model_corrector

def analyze_test_families(results):
    """Analyze results by test family"""
    family_results = {}
    
    for result in results['detailed_results']:
        family = result['metadata']['test_family']
        if family not in family_results:
            family_results[family] = {'total': 0, 'passed': 0, 'examples': []}
        
        family_results[family]['total'] += 1
        if result['passed']:
            family_results[family]['passed'] += 1
        
        family_results[family]['examples'].append({
            'input': result['input'],
            'expected': result['expected'],
            'actual': result['actual'],
            'passed': result['passed']
        })
    
    return family_results

def calculate_metrics(results):
    """Calculate precision, recall, and F1 score for test results"""
    y_true = []
    y_pred = []
    
    for result in results['detailed_results']:
        # For our case, true positive is when expected == actual
        y_true.append(1)  # We expect all test cases to be correct
        y_pred.append(1 if result['passed'] else 0)
    
    metrics = {
        'precision': precision_score(y_true, y_pred, zero_division=0),
        'recall': recall_score(y_true, y_pred, zero_division=0),
        'f1': f1_score(y_true, y_pred, zero_division=0)
    }
    
    return metrics

def create_metrics_visualization(metrics, family_results, output_dir):
    """Create visualization for precision, recall, and F1 scores"""
    # Overall metrics plot
    plt.figure(figsize=(10, 6))
    metrics_data = pd.DataFrame({
        'Metric': ['Precision', 'Recall', 'F1 Score'],
        'Score': [metrics['precision'], metrics['recall'], metrics['f1']]
    })
    
    colors = ['#2ecc71', '#3498db', '#e67e22']
    ax = sns.barplot(data=metrics_data, x='Metric', y='Score', palette=colors)
    
    plt.title('Overall Performance Metrics', fontsize=14, pad=20)
    plt.ylabel('Score', fontsize=12)
    
    # Add value labels
    for i, v in enumerate(metrics_data['Score']):
        ax.text(i, v + 0.01, f'{v:.3f}', ha='center', fontsize=11)
    
    plt.ylim(0, 1.1)
    plt.savefig(os.path.join(output_dir, 'overall_metrics.png'), 
                dpi=300, bbox_inches='tight')
    plt.close()
    
    # Calculate and plot F1 scores by family
    family_metrics = []
    for family, stats in family_results.items():
        y_true = [1] * stats['total']  # All should be correct
        y_pred = [1] * stats['passed'] + [0] * (stats['total'] - stats['passed'])
        f1 = f1_score(y_true, y_pred, zero_division=0)
        
        family_metrics.append({
            'Family': family.replace('_', ' ').title(),
            'F1 Score': f1
        })
    
    plt.figure(figsize=(12, 6))
    df = pd.DataFrame(family_metrics)
    ax = sns.barplot(data=df, x='Family', y='F1 Score', 
                    palette=['#2ecc71' if score >= 0.8 else '#e74c3c' 
                            for score in df['F1 Score']])
    
    plt.title('F1 Scores by Test Family', fontsize=14, pad=20)
    plt.ylabel('F1 Score', fontsize=12)
    plt.xlabel('Test Family', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    
    # Add value labels
    for i, v in enumerate(df['F1 Score']):
        ax.text(i, v + 0.01, f'{v:.3f}', ha='center', fontsize=10)
    
    plt.ylim(0, 1.1)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'family_f1_scores.png'), 
                dpi=300, bbox_inches='tight')
    plt.close()
    
    return family_metrics

def create_family_visualizations(family_results, output_dir):
    """Create visualizations for test family results"""
    # Set style
    sns.set_theme(style="whitegrid")
    colors = ["#2ecc71", "#e74c3c"]  # Green for pass, Red for fail
    
    # Prepare data
    family_data = []
    for family, stats in family_results.items():
        pass_rate = (stats['passed'] / stats['total']) * 100
        family_data.append({
            'Family': family.replace('_', ' ').title(),
            'Pass Rate': pass_rate
        })
    
    df = pd.DataFrame(family_data)
    
    # Create bar plot
    plt.figure(figsize=(12, 6))
    ax = sns.barplot(data=df, x='Family', y='Pass Rate', 
                    palette=['#2ecc71' if rate >= 80 else '#e74c3c' for rate in df['Pass Rate']])
    
    plt.title('Test Family Performance', fontsize=14, pad=20)
    plt.ylabel('Pass Rate (%)', fontsize=12)
    plt.xlabel('Test Family', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    
    # Add value labels
    for i, v in enumerate(df['Pass Rate']):
        ax.text(i, v + 1, f'{v:.1f}%', ha='center', fontsize=10)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'family_performance.png'), dpi=300, bbox_inches='tight')
    plt.close()

def generate_advanced_report(results, family_results, output_dir):
    """Generate a detailed markdown report for advanced tests"""
    # Calculate metrics
    metrics = calculate_metrics(results)
    
    report = """# StyleCheck Advanced Behavioral Testing Report

## Overview
This report focuses on advanced behavioral tests including:
- Length Variability
- Temporal Invariance
- Named Entity Invariance
- Location Invariance
- Gender Invariance
- Number Invariance
- Polarity Invariance
- Synonym Invariance

## Overall Results
- Total Tests: {total}
- Passed Tests: {passed}
- Overall Pass Rate: {pass_rate:.2f}%

## Performance Metrics
- Precision: {precision:.3f}
- Recall: {recall:.3f}
- F1 Score: {f1:.3f}

## Test Family Analysis
""".format(
        total=results['overall']['total'],
        passed=results['overall']['passed'],
        pass_rate=(results['overall']['passed'] / results['overall']['total'] * 100),
        precision=metrics['precision'],
        recall=metrics['recall'],
        f1=metrics['f1']
    )
    
    # Calculate F1 scores for each family
    for family, stats in family_results.items():
        y_true = [1] * stats['total']
        y_pred = [1] * stats['passed'] + [0] * (stats['total'] - stats['passed'])
        f1 = f1_score(y_true, y_pred, zero_division=0)
        
        pass_rate = (stats['passed'] / stats['total'] * 100)
        report += f"\n### {family.replace('_', ' ').title()}\n"
        report += f"- Pass Rate: {pass_rate:.2f}%\n"
        report += f"- Tests Passed: {stats['passed']}/{stats['total']}\n"
        report += f"- F1 Score: {f1:.3f}\n"
        report += "\nExample Tests:\n"
        
        # Add examples
        for example in stats['examples'][:2]:
            report += f"\n**Input:** {example['input']}\n"
            report += f"**Expected:** {example['expected']}\n"
            report += f"**Actual:** {example['actual']}\n"
            report += f"**Result:** {'✅ Passed' if example['passed'] else '❌ Failed'}\n"
    
    with open(os.path.join(output_dir, 'advanced_test_report.md'), 'w') as f:
        f.write(report)

def main():
    # Ensure we're in the correct directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Create results directory for advanced tests
    results_dir = 'advanced_results'
    os.makedirs(results_dir, exist_ok=True)
    
    # Initialize test suite
    test_suite = BehavioralTestSuite(create_model_corrector())
    
    # Load advanced test cases
    test_suite.add_test_cases_from_json('advanced_test_cases.json')
    
    # Run tests
    print("\nRunning advanced behavioral tests...")
    results = test_suite.run_tests()
    
    # Analyze results by test family
    print("\nAnalyzing test families...")
    family_results = analyze_test_families(results)
    
    # Calculate metrics
    metrics = calculate_metrics(results)
    print("\nMetrics:")
    print(f"Precision: {metrics['precision']:.3f}")
    print(f"Recall: {metrics['recall']:.3f}")
    print(f"F1 Score: {metrics['f1']:.3f}")
    
    # Create visualizations
    print("\nGenerating visualizations...")
    create_family_visualizations(family_results, results_dir)
    create_metrics_visualization(metrics, family_results, results_dir)
    
    # Generate report
    print("\nGenerating advanced test report...")
    generate_advanced_report(results, family_results, results_dir)
    
    # Print summary
    print("\nAdvanced Test Results Summary:")
    print(f"Total Tests: {results['overall']['total']}")
    print(f"Passed Tests: {results['overall']['passed']}")
    print(f"Overall Pass Rate: {results['overall']['passed'] / results['overall']['total'] * 100:.2f}%")
    print("\nDetailed results and visualizations have been saved to the 'advanced_results' directory.")

if __name__ == "__main__":
    main()
