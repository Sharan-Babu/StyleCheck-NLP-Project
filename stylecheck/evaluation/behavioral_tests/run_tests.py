import os
import sys
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from test_suite import BehavioralTestSuite
sys.path.append('../..')
from llm_integrations import get_all_corrections

def create_model_corrector():
    """Create a wrapper for the model correction function"""
    def model_corrector(text: str) -> str:
        correction_result = get_all_corrections(text)
        return correction_result.get("corrected_phrase", text)
    return model_corrector

def create_visualizations(results, output_dir):
    """Create visualizations for test results"""
    # Set style
    sns.set_theme(style="whitegrid")
    colors = ["#2ecc71", "#e74c3c"]
    
    # 1. Overall Results
    plt.figure(figsize=(10, 6))
    overall_data = pd.DataFrame([{
        'Status': 'Passed',
        'Count': results['overall']['passed']
    }, {
        'Status': 'Failed',
        'Count': results['overall']['total'] - results['overall']['passed']
    }])
    
    ax = sns.barplot(data=overall_data, x='Status', y='Count', palette=colors)
    plt.title('Overall Test Results', fontsize=14, pad=20)
    plt.ylabel('Number of Tests', fontsize=12)
    
    # Add value labels
    for i, v in enumerate(overall_data['Count']):
        ax.text(i, v + 0.5, str(v), ha='center', fontsize=11)
    
    plt.savefig(os.path.join(output_dir, 'overall_results.png'), 
                dpi=300, bbox_inches='tight')
    plt.close()
    
    # 2. Results by Capability
    capability_data = []
    for cap, stats in results['by_capability'].items():
        capability_data.append({
            'Capability': cap,
            'Status': 'Passed',
            'Count': stats['passed']
        })
        capability_data.append({
            'Capability': cap,
            'Status': 'Failed',
            'Count': stats['total'] - stats['passed']
        })
    
    plt.figure(figsize=(12, 6))
    df = pd.DataFrame(capability_data)
    ax = sns.barplot(data=df, x='Capability', y='Count', hue='Status', palette=colors)
    
    plt.title('Test Results by Capability', fontsize=14, pad=20)
    plt.ylabel('Number of Tests', fontsize=12)
    plt.xlabel('Capability', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    
    # Add value labels
    for i in ax.containers:
        ax.bar_label(i, padding=3)
    
    plt.legend(title='Status', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    
    plt.savefig(os.path.join(output_dir, 'capability_results.png'), 
                dpi=300, bbox_inches='tight')
    plt.close()
    
    # 3. Results by Test Type
    test_type_data = []
    for test_type, stats in results['by_test_type'].items():
        test_type_data.append({
            'Test Type': test_type,
            'Status': 'Passed',
            'Count': stats['passed']
        })
        test_type_data.append({
            'Test Type': test_type,
            'Status': 'Failed',
            'Count': stats['total'] - stats['passed']
        })
    
    plt.figure(figsize=(12, 6))
    df = pd.DataFrame(test_type_data)
    ax = sns.barplot(data=df, x='Test Type', y='Count', hue='Status', palette=colors)
    
    plt.title('Test Results by Test Type', fontsize=14, pad=20)
    plt.ylabel('Number of Tests', fontsize=12)
    plt.xlabel('Test Type', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    
    # Add value labels
    for i in ax.containers:
        ax.bar_label(i, padding=3)
    
    plt.legend(title='Status', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    
    plt.savefig(os.path.join(output_dir, 'test_type_results.png'), 
                dpi=300, bbox_inches='tight')
    plt.close()

def generate_report(results, output_dir):
    """Generate a detailed markdown report"""
    report = f"""# StyleCheck Behavioral Testing Report

## Overall Results
- Total Tests: {results['overall']['total']}
- Passed Tests: {results['overall']['passed']}
- Pass Rate: {(results['overall']['passed'] / results['overall']['total'] * 100):.2f}%

## Results by Capability
"""
    
    for cap, stats in results['by_capability'].items():
        pass_rate = (stats['passed'] / stats['total'] * 100)
        report += f"### {cap.replace('_', ' ').title()}\n"
        report += f"- Total Tests: {stats['total']}\n"
        report += f"- Passed Tests: {stats['passed']}\n"
        report += f"- Pass Rate: {pass_rate:.2f}%\n\n"
    
    report += "## Results by Test Type\n"
    for test_type, stats in results['by_test_type'].items():
        pass_rate = (stats['passed'] / stats['total'] * 100)
        report += f"### {test_type.replace('_', ' ').title()}\n"
        report += f"- Total Tests: {stats['total']}\n"
        report += f"- Passed Tests: {stats['passed']}\n"
        report += f"- Pass Rate: {pass_rate:.2f}%\n\n"
    
    report += "## Failed Test Cases\n"
    for result in results['detailed_results']:
        if not result['passed']:
            report += f"### Test Case: {result['description']}\n"
            report += f"- Input: {result['input']}\n"
            report += f"- Expected: {result['expected']}\n"
            report += f"- Actual: {result['actual']}\n"
            report += f"- Capability: {result['capability']}\n"
            report += f"- Test Type: {result['test_type']}\n\n"
    
    with open(os.path.join(output_dir, 'behavioral_test_report.md'), 'w') as f:
        f.write(report)

def main():
    # Ensure we're in the correct directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Create results directory
    results_dir = 'results'
    os.makedirs(results_dir, exist_ok=True)
    
    # Initialize test suite
    test_suite = BehavioralTestSuite(create_model_corrector())
    
    # Load test cases from JSON
    test_suite.add_test_cases_from_json('test_cases.json')
    
    # Run tests
    print("\nRunning behavioral tests...")
    results = test_suite.run_tests()
    
    # Save results
    test_suite.save_results(results_dir)
    
    # Create visualizations
    print("\nGenerating visualizations...")
    create_visualizations(results, results_dir)
    
    # Generate report
    print("\nGenerating report...")
    generate_report(results, results_dir)
    
    # Print summary
    print("\nTest Results Summary:")
    print(f"Total Tests: {results['overall']['total']}")
    print(f"Passed Tests: {results['overall']['passed']}")
    print(f"Overall Pass Rate: {results['overall']['passed'] / results['overall']['total'] * 100:.2f}%")
    print("\nDetailed results and visualizations have been saved to the 'results' directory.")

if __name__ == "__main__":
    main()
