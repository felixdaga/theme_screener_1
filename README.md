# Company Theme Screener

An interactive Jupyter notebook tool for screening and shortlisting companies based on multiple criteria. This tool allows you to:

1. Upload company data from Excel files
2. Select and weight different criteria for company evaluation
3. Calculate composite scores based on weighted criteria
4. Filter companies based on score percentiles
5. Visualize results with interactive plots

## Features

- Interactive file upload widget for Excel data
- Dynamic criteria selection and weighting
- Score normalization and composite score calculation
- Percentile-based filtering
- Interactive visualizations using Plotly
- User-friendly interface with IPywidgets

## Requirements

- Python 3.x
- Jupyter Notebook
- Required Python packages:
  - pandas
  - numpy
  - plotly
  - ipywidgets
  - openpyxl (for Excel file support)

## Installation

1. Clone this repository:

   ```bash
   git clone https://github.com/felixdaga/theme_screener_1.git
   cd theme_screener_1
   ```

2. Install required packages:

   ```bash
   pip install pandas numpy plotly ipywidgets openpyxl
   ```

3. Launch Jupyter Notebook:

   ```bash
   jupyter notebook
   ```

4. Open `theme_screener_steps.ipynb`

## Usage

1. Upload your Excel file containing company data using the file upload widget
2. Select the criteria you want to use for evaluation
3. Adjust the weights for each criterion using the sliders
4. Click "Calculate Scores" to generate composite scores
5. Use the percentile slider to filter companies based on their scores

## Input Data Format

Your Excel file should contain:

- One row per company
- Columns for different criteria/metrics
- Numerical values for each criterion

## License

This project is open source and available under the MIT License.
