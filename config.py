import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev-secret-key")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    PUBMED_BASE_URL = "https://pubmed.ncbi.nlm.nih.gov"
    PUBMED_SEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    MAX_ARTICLES = 10
    CLAUDE_MODEL = "claude-3-sonnet-20240229"
    MAX_TOKENS = 4096
