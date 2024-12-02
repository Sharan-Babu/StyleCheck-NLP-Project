import json
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Dict, List, Any
import os
import pandas as pd
from tqdm import tqdm

class TestType(str, Enum):
    MINIMUM_FUNCTIONALITY = "minimum_functionality"
    INVARIANCE = "invariance"
    DIRECTIONAL = "directional"
    NEGATION = "negation"

class Capability(str, Enum):
    SUBJECT_VERB_AGREEMENT = "subject_verb_agreement"
    TENSE_CONSISTENCY = "tense_consistency"
    ARTICLE_USAGE = "article_usage"
    PREPOSITION_USAGE = "preposition_usage"
    NEGATION_HANDLING = "negation_handling"
    VOCABULARY_CHOICE = "vocabulary_choice"
    COMPLEX_SENTENCES = "complex_sentences"
    PUNCTUATION = "punctuation"
    # Advanced test capabilities
    LENGTH_INVARIANCE = "length_invariance"
    TEMPORAL_INVARIANCE = "temporal_invariance"
    NAME_ENTITY_INVARIANCE = "name_entity_invariance"
    LOCATION_INVARIANCE = "location_invariance"
    GENDER_INVARIANCE = "gender_invariance"
    NUMBER_INVARIANCE = "number_invariance"
    POLARITY_INVARIANCE = "polarity_invariance"
    SYNONYM_INVARIANCE = "synonym_invariance"

@dataclass
class TestCase:
    input_text: str
    expected_output: str
    capability: Capability
    test_type: TestType
    description: str
    metadata: Dict[str, Any] = None

class BehavioralTestSuite:
    def __init__(self, model_corrector: Callable[[str], str]):
        self.model_corrector = model_corrector
        self.test_cases: List[TestCase] = []
        self.results = []
        
    def add_test_case(self, test_case: TestCase):
        """Add a test case to the suite"""
        self.test_cases.append(test_case)
    
    def add_test_cases_from_json(self, json_file: str):
        """Load test cases from a JSON file"""
        with open(json_file, 'r') as f:
            data = json.load(f)
            for case in data['test_cases']:  # Access the 'test_cases' array
                self.add_test_case(TestCase(
                    input_text=case['input_text'],
                    expected_output=case['expected_output'],
                    capability=Capability(case['capability']),
                    test_type=TestType(case['test_type']),
                    description=case['description'],
                    metadata=case.get('metadata', {})
                ))
    
    def run_tests(self) -> Dict:
        """Run all test cases and return results"""
        self.results = []
        overall_results = {'total': 0, 'passed': 0}
        capability_results = {}
        test_type_results = {}

        for test_case in tqdm(self.test_cases, desc="Running tests"):
            # Get model correction
            actual_output = self.model_corrector(test_case.input_text)
            passed = actual_output.strip() == test_case.expected_output.strip()

            # Store detailed result
            result = {
                'input': test_case.input_text,
                'expected': test_case.expected_output,
                'actual': actual_output,
                'passed': passed,
                'capability': test_case.capability,
                'test_type': test_case.test_type,
                'description': test_case.description,
                'metadata': test_case.metadata or {}
            }
            self.results.append(result)

            # Update overall stats
            overall_results['total'] += 1
            if passed:
                overall_results['passed'] += 1

            # Update capability stats
            if test_case.capability not in capability_results:
                capability_results[test_case.capability] = {'total': 0, 'passed': 0}
            capability_results[test_case.capability]['total'] += 1
            if passed:
                capability_results[test_case.capability]['passed'] += 1

            # Update test type stats
            if test_case.test_type not in test_type_results:
                test_type_results[test_case.test_type] = {'total': 0, 'passed': 0}
            test_type_results[test_case.test_type]['total'] += 1
            if passed:
                test_type_results[test_case.test_type]['passed'] += 1

        return {
            'overall': overall_results,
            'by_capability': capability_results,
            'by_test_type': test_type_results,
            'detailed_results': self.results
        }

    def save_results(self, output_dir: str):
        """Save test results to files"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Save detailed results to JSON
        with open(os.path.join(output_dir, 'test_results.json'), 'w') as f:
            json.dump({
                'results': self.results
            }, f, indent=2)
        
        # Create DataFrame for analysis
        df = pd.DataFrame(self.results)
        df.to_csv(os.path.join(output_dir, 'test_results.csv'), index=False)
    
    def _evaluate_correction(self, model_output: str, expected_output: str) -> bool:
        """
        Evaluate if the model's correction matches the expected output.
        This can be enhanced with more sophisticated comparison methods.
        """
        return model_output.strip().lower() == expected_output.strip().lower()

def generate_test_cases() -> List[TestCase]:
    """Generate comprehensive test cases following CheckList methodology"""
    test_cases = []
    
    # 1. Minimum Functionality Tests (MFT)
    test_cases.extend([
        TestCase(
            input_text="The cats is sleeping.",
            expected_output="The cats are sleeping.",
            capability=Capability.SUBJECT_VERB_AGREEMENT,
            test_type=TestType.MINIMUM_FUNCTIONALITY,
            description="Basic subject-verb agreement with plural noun"
        ),
        TestCase(
            input_text="I has been working here.",
            expected_output="I have been working here.",
            capability=Capability.SUBJECT_VERB_AGREEMENT,
            test_type=TestType.MINIMUM_FUNCTIONALITY,
            description="Basic subject-verb agreement with first person"
        ),
    ])
    
    # 2. Invariance Tests
    test_cases.extend([
        TestCase(
            input_text="Despite of the rain, we continued playing.",
            expected_output="Despite the rain, we continued playing.",
            capability=Capability.PREPOSITION_USAGE,
            test_type=TestType.INVARIANCE,
            description="Incorrect preposition usage with 'despite'"
        ),
        TestCase(
            input_text="The man which I saw yesterday is my teacher.",
            expected_output="The man whom I saw yesterday is my teacher.",
            capability=Capability.COMPLEX_SENTENCES,
            test_type=TestType.INVARIANCE,
            description="Relative pronoun usage"
        ),
    ])
    
    # 3. Directional Tests
    test_cases.extend([
        TestCase(
            input_text="The movie was very good.",
            expected_output="The movie was excellent.",
            capability=Capability.VOCABULARY_CHOICE,
            test_type=TestType.DIRECTIONAL,
            description="Improve word choice for better expression"
        ),
        TestCase(
            input_text="He made a decision to go.",
            expected_output="He decided to go.",
            capability=Capability.VOCABULARY_CHOICE,
            test_type=TestType.DIRECTIONAL,
            description="Convert verbose phrase to concise verb"
        ),
    ])
    
    # 4. Negation Tests
    test_cases.extend([
        TestCase(
            input_text="He don't know nothing about it.",
            expected_output="He doesn't know anything about it.",
            capability=Capability.NEGATION_HANDLING,
            test_type=TestType.NEGATION,
            description="Double negation correction"
        ),
        TestCase(
            input_text="I didn't saw him yesterday.",
            expected_output="I didn't see him yesterday.",
            capability=Capability.NEGATION_HANDLING,
            test_type=TestType.NEGATION,
            description="Past tense with negation"
        ),
    ])
    
    return test_cases

if __name__ == "__main__":
    from llm_integrations import get_all_corrections
    
    # Initialize test suite with your model
    def model_corrector(text: str) -> str:
        """Wrapper for your model's correction function"""
        correction_result = get_all_corrections(text)
        return correction_result.get("corrected_phrase", text)
    
    test_suite = BehavioralTestSuite(model_corrector)
    
    # Generate and add test cases
    test_cases = generate_test_cases()
    for test_case in test_cases:
        test_suite.add_test_case(test_case)
    
    # Run tests
    results = test_suite.run_tests()
    
    # Save results
    test_suite.save_results('evaluation/behavioral_tests/results')
    
    # Print summary
    print("\nTest Results Summary:")
    print(f"Total Tests: {results['overall']['total']}")
    print(f"Passed Tests: {results['overall']['passed']}")
    print(f"Overall Pass Rate: {results['overall']['passed'] / results['overall']['total'] * 100:.2f}%")
