# AI Rehabilitation Research Assistant

A comprehensive AI-powered tool that scrapes PubMed for rehabilitation research and uses Claude (Anthropic's LLM) to analyze, summarize, and compare findings.

## Features

- **PubMed Search**: Search rehabilitation research articles using NCBI E-utilities API
- **Web Scraping**: Extract keywords and MeSH terms from article pages using BeautifulSoup
- **AI Analysis**: Ask questions about research findings using Claude 3 Sonnet
- **Research Summarization**: Get structured summaries across multiple articles
- **Treatment Comparison**: Compare rehabilitation approaches based on available evidence

## Tech Stack

- **Backend**: Flask (Python)
- **AI**: Anthropic Claude API (Claude 3 Sonnet)
- **Scraping**: BeautifulSoup4, requests
- **Data Source**: PubMed / NCBI E-utilities

## Setup

1. Clone the repository and navigate to this directory
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # macOS/Linux
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env and add your Anthropic API key
   ```
5. Run the application:
   ```bash
   python app.py
   ```
6. Open http://localhost:5000 in your browser

## Testing

```bash
pytest tests/ -v
```

## Project Structure

```
ai-rehab-assistant/
├── app.py              # Flask application and routes
├── scraper.py          # PubMed scraping logic
├── analyzer.py         # Claude AI analysis engine
├── config.py           # Configuration management
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variable template
├── templates/
│   └── index.html      # Web interface
└── tests/
    ├── test_app.py     # Route tests
    ├── test_scraper.py # Scraper tests
    └── test_analyzer.py# Analyzer tests
```
