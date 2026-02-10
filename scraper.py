"""PubMed web scraper for rehabilitation research articles."""

import time
import xml.etree.ElementTree as ET

import requests
from bs4 import BeautifulSoup

from config import Config


class PubMedScraper:
    """Scrapes PubMed for rehabilitation research articles using E-utilities API."""

    def __init__(self):
        self.base_url = Config.PUBMED_SEARCH_URL
        self.session = requests.Session()
        self.session.headers.update(
            {"User-Agent": "RehabResearchBot/1.0 (Educational Project)"}
        )

    def search_articles(self, query, max_results=None):
        """Search PubMed for articles matching the query.

        Args:
            query: Search term for PubMed.
            max_results: Maximum number of article IDs to return.

        Returns:
            List of PubMed article IDs.
        """
        if max_results is None:
            max_results = Config.MAX_ARTICLES

        params = {
            "db": "pubmed",
            "term": f"{query} AND rehabilitation",
            "retmax": max_results,
            "retmode": "json",
            "sort": "relevance",
        }

        try:
            response = self.session.get(
                f"{self.base_url}/esearch.fcgi", params=params, timeout=15
            )
            response.raise_for_status()
            data = response.json()
            return data.get("esearchresult", {}).get("idlist", [])
        except requests.RequestException as e:
            print(f"Error searching PubMed: {e}")
            return []

    def fetch_article_details(self, article_ids):
        """Fetch detailed information for a list of PubMed article IDs.

        Args:
            article_ids: List of PubMed IDs.

        Returns:
            List of dicts with article title, abstract, authors, journal, date.
        """
        if not article_ids:
            return []

        ids_str = ",".join(article_ids)
        params = {
            "db": "pubmed",
            "id": ids_str,
            "retmode": "xml",
        }

        try:
            response = self.session.get(
                f"{self.base_url}/efetch.fcgi", params=params, timeout=15
            )
            response.raise_for_status()
            return self._parse_xml_response(response.text)
        except requests.RequestException as e:
            print(f"Error fetching article details: {e}")
            return []

    def _parse_xml_response(self, xml_text):
        """Parse PubMed XML response into structured article data."""
        articles = []
        try:
            root = ET.fromstring(xml_text)
        except ET.ParseError:
            return articles

        for article_elem in root.findall(".//PubmedArticle"):
            article = self._extract_article_data(article_elem)
            if article:
                articles.append(article)

        return articles

    def _extract_article_data(self, article_elem):
        """Extract structured data from a single PubmedArticle XML element."""
        medline = article_elem.find(".//MedlineCitation")
        if medline is None:
            return None

        pmid_elem = medline.find(".//PMID")
        pmid = pmid_elem.text if pmid_elem is not None else "Unknown"

        title_elem = medline.find(".//ArticleTitle")
        title = title_elem.text if title_elem is not None else "No title available"

        abstract_parts = medline.findall(".//AbstractText")
        if abstract_parts:
            abstract = " ".join(
                part.text for part in abstract_parts if part.text
            )
        else:
            abstract = "No abstract available."

        authors = []
        for author in medline.findall(".//Author"):
            last = author.find("LastName")
            first = author.find("ForeName")
            if last is not None and first is not None:
                authors.append(f"{last.text}, {first.text}")
            elif last is not None:
                authors.append(last.text)

        journal_elem = medline.find(".//Journal/Title")
        journal = journal_elem.text if journal_elem is not None else "Unknown Journal"

        year_elem = medline.find(".//PubDate/Year")
        year = year_elem.text if year_elem is not None else "N/A"

        return {
            "pmid": pmid,
            "title": title,
            "abstract": abstract,
            "authors": authors[:5],  # Limit to first 5 authors
            "journal": journal,
            "year": year,
            "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
        }

    def scrape_full_article_page(self, pmid):
        """Scrape the full PubMed article page for additional content.

        Args:
            pmid: PubMed article ID.

        Returns:
            Dict with additional scraped content (keywords, mesh terms, etc).
        """
        url = f"{Config.PUBMED_BASE_URL}/{pmid}/"
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            keywords = []
            keyword_section = soup.find("div", class_="keywords-section")
            if keyword_section:
                for kw in keyword_section.find_all("button", class_="keyword-actions-trigger"):
                    text = kw.get_text(strip=True)
                    if text:
                        keywords.append(text)

            mesh_terms = []
            mesh_section = soup.find("div", class_="mesh-terms")
            if mesh_section:
                for term in mesh_section.find_all("button"):
                    text = term.get_text(strip=True)
                    if text:
                        mesh_terms.append(text)

            return {
                "keywords": keywords,
                "mesh_terms": mesh_terms,
            }
        except requests.RequestException as e:
            print(f"Error scraping article page {pmid}: {e}")
            return {"keywords": [], "mesh_terms": []}

    def get_research_data(self, query, max_results=None):
        """Full pipeline: search, fetch details, and return structured data.

        Args:
            query: Search query for rehabilitation research.
            max_results: Maximum number of articles.

        Returns:
            List of complete article data dicts.
        """
        article_ids = self.search_articles(query, max_results)
        if not article_ids:
            return []

        articles = self.fetch_article_details(article_ids)

        # Rate-limit scraping of individual pages
        for article in articles:
            extra = self.scrape_full_article_page(article["pmid"])
            article.update(extra)
            time.sleep(0.5)  # Be respectful to PubMed servers

        return articles
