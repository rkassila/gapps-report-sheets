# Report Generator

A Cloud Run function that generates PDF sales reports with visualizations and AI-powered analysis.

## Features

- Generates sales graphs by region
- Creates profit analysis charts by product
- Provides AI-powered insights using OpenAI GPT-3.5
- Compiles everything into a PDF report

## Deployment

This project is configured for Google Cloud Run. **Pushing to the `master` branch automatically triggers a deployment and updates the Cloud Run function.**

## Usage

The function expects a POST request with the following JSON structure:

```json
{
  "headers": ["Date", "Region", "Product", "Sales", "Profit"],
  "rows": [
    ["2024-01-01", "North", "Product A", 1000, 200],
    ...
  ],
  "reportMonth": "January 2024"
}
```

The function returns:
- A PDF document containing:
  - Sales by region graph
  - Profit by product graph
  - AI-generated analysis text

## Requirements

- Python 3.10
- See `requirements.txt` for Python dependencies
