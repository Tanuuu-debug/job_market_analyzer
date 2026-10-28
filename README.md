# Job Market Analyzer

## Project Overview

## 🚀 Run Project

[![Run Project](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://tanuuu-debug-job-market-analyzer-app-wqwpkn.streamlit.app/)

Click the button above to open the Job Market Analyzer dashboard.

The Job Market Analyzer is a Python-based data analytics project that analyzes historical and live job postings to identify hiring trends, frequently requested skills, job locations, companies, experience levels, and available salary information.

The dashboard is developed using Streamlit, Pandas, and Plotly.

## Features

- Historical job market analysis
- Live job collection from Adzuna, Greenhouse, and JSearch
- In-demand skill analysis
- Job title and company search
- Experience-level filtering
- Location filtering
- Employment-type filtering
- Job platform filtering
- Interactive charts and visualizations
- Salary analysis when comparable salary data is available
- Job application links

## Technologies Used

- Python
- Pandas
- Streamlit
- Plotly
- Regular expressions
- REST APIs
- CSV datasets

## Project Setup

### 1. Clone the repository

Clone this repository from GitHub or download it as a ZIP file.

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the virtual environment

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the dashboard

```bash
python -m streamlit run app.py
```

The dashboard will open in your browser.

## Live Data Collection

Live data collection requires the API credentials for the respective providers.

Create a `.env` file in the project root and configure the required credentials using the variable names expected by the collector scripts.

Never commit API keys or other credentials to GitHub.

The historical dashboard can be used without API credentials if the required historical dataset is included in the repository.

## Project Structure

```text
job-market-analyzer/
├── app.py
├── live_collector.py
├── greenhouse_collector.py
├── jsearch_collector.py
├── process_live_jobs.py
├── requirements.txt
├── README.md
├── .gitignore
├── analysis/
└── data/
```

## Notes

- Live listings can expire or change.
- Available data depends on the configured data providers.
- Skill counts represent mentions extracted from the collected job postings.
- Salary comparisons require consistent currencies and pay periods.
- Historical datasets and collected listings may have licensing or redistribution restrictions.

## Author

Job Market Analyzer Project