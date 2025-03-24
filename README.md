# Theme Investment Screener

An interactive tool for screening companies based on their relevance to investment themes, with customizable scoring weights and automated analysis capabilities.

## Features

- Upload and analyze Excel files containing company data
- Customize scoring weights for different metrics
- View top companies based on weighted scores
- Interactive visualizations of portfolio characteristics:
  - Sector distribution
  - Country distribution
  - Score distribution
- Conference call analysis using custom AI function
- Export results to Excel

## Setup

1. Clone this repository:

   ```bash
   git clone https://github.com/yourusername/theme_screener.git
   cd theme_screener
   ```

2. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Ensure your custom AI function is properly imported and configured

## Usage

### Running in Jupyter Notebook

1. Start Jupyter Notebook:

   ```bash
   jupyter notebook
   ```

2. Open `theme_screener.ipynb`

3. Run the cells in order:

   - First cell: Imports required libraries
   - Second cell: Launches the Streamlit application

4. The application will open in your default web browser at http://localhost:8501

### Running as Standalone Script

1. Run the Streamlit application:
   ```bash
   streamlit run theme_screener.py
   ```

## Excel File Format

Your Excel file should contain the following columns:

- Company (company name)
- Country
- Sector
- Score columns (numeric values, preferably 0 or 1)
- Revenue alignment columns (numeric values)
- Conference_Call (text)

## Notes

- The tool automatically detects numeric columns containing "score" or "revenue" in their names for weighting
- Conference call analysis uses the custom AI function `AI.get_surface_chat_completion()`
- Results are sorted by weighted score in descending order
- Default score columns are those ending with "\_final"
