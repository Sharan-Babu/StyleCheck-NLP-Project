## 📊 Evaluation System

### Performance Metrics
1. **GLEU Score Analysis**
   - Overall model comparison
   - Category-wise performance tracking
   - Detailed performance visualization

2. **Readability Metrics**
   - Flesch-Kincaid Grade Level

3. **Error Categories**
   - Simple Grammar
   - Complex Grammar
   - Style and Word Choice

### Visualization Components
Located in `evaluation/charts/`:
1. **GLEU Score Visualizations**
   - `overall_gleu_scores.png`: Overall model comparison
   - `category_gleu_scores.png`: Category-wise performance

2. **Readability Visualizations**
   - `overall_flesch_scores.png`: Overall Flesch Reading Ease comparison
   - `category_flesch_scores.png`: Category-wise readability analysis

### Results Storage
- `evaluation/results/evaluation_progress.json`: Summary statistics
- `evaluation/results/detailed_results.json`: Detailed per-case results

## Setup and Installation

### Environment Setup
1. Clone the repository:
   ```bash
   git clone [repository-url]
   cd stylecheck
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows it is: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Create a `.env` file with your API keys:
   ```
   MISTRAL_API_KEY=your_key_here
   ANTHROPIC_API_KEY=your_key_here
   GEMINI_API_KEY=your_key_here
   OPENAI_API_KEY=your_key_here
   ```

### Running the Application
1. Start the Flask server:
   ```bash
   python app.py
   ```
2. Access the application at `http://localhost:5000`

### Running Evaluations
1. Execute the evaluation script:
   ```bash
   cd evaluation
   python main.py
   ```
2. Generate visualizations:
   ```bash
   python gleu_visualization.py
   python flesch_visualization.py
   ```

## 📈 Results

### Model Performance
- StyleCheck consistently outperforms baseline T5 model
- Higher GLEU scores across all error categories
- Improved readability metrics, especially in complex grammar cases
