# Company Score Analysis Dashboard

A Streamlit-based dashboard for analyzing company scores and portfolio composition.

## Features

- Upload Excel files containing company data
- Select and weight scoring criteria
- Filter companies based on percentile thresholds
- Visualize score distributions
- Analyze portfolio composition by:
  - Sector
  - Country
  - Market Cap Group
- Download filtered results as CSV

## Installation

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd <repository-name>
   ```

2. Install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the Streamlit app:

   ```bash
   streamlit run app.py
   ```

2. Open your web browser and navigate to the URL shown in the terminal (typically http://localhost:8501)

3. Upload an Excel file with the following columns:
   - `short_name`: Company identifiers
   - `score_1`, `score_2`, etc.: Scoring criteria columns
   - `gics_1_sector`: Industry sector classification
   - `country`: Company's country (optional)
   - `Market cap group`: Market capitalization category (optional)

## Data Format Example

Your Excel file should look something like this:

| short_name | score_1 | score_2 | score_3 | gics_1_sector | country | Market cap group |
| ---------- | ------- | ------- | ------- | ------------- | ------- | ---------------- |
| Company A  | 1       | 0       | 1       | IT            | USA     | Large Cap        |
| Company B  | 0       | 1       | 0       | Energy        | UK      | Mid Cap          |
| Company C  | 1       | 1       | 0       | IT            | USA     | Small Cap        |

## License

MIT License
