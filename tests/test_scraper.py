"""Tests for the PubMed scraper module."""

import pytest
from unittest.mock import patch, MagicMock

from scraper import PubMedScraper


@pytest.fixture
def scraper():
    return PubMedScraper()


SAMPLE_SEARCH_RESPONSE = {
    "esearchresult": {
        "idlist": ["12345678", "87654321", "11223344"]
    }
}

SAMPLE_XML_RESPONSE = """<?xml version="1.0"?>
<PubmedArticleSet>
  <PubmedArticle>
    <MedlineCitation>
      <PMID>12345678</PMID>
      <Article>
        <ArticleTitle>Effects of Physical Therapy on Stroke Recovery</ArticleTitle>
        <Abstract>
          <AbstractText>This study examines the impact of early physical therapy intervention on motor recovery following ischemic stroke.</AbstractText>
        </Abstract>
        <AuthorList>
          <Author>
            <LastName>Smith</LastName>
            <ForeName>John</ForeName>
          </Author>
          <Author>
            <LastName>Doe</LastName>
            <ForeName>Jane</ForeName>
          </Author>
        </AuthorList>
        <Journal>
          <Title>Journal of Rehabilitation Medicine</Title>
        </Journal>
      </Article>
      <DateCompleted>
        <Year>2024</Year>
      </DateCompleted>
    </MedlineCitation>
  </PubmedArticle>
</PubmedArticleSet>
"""

SAMPLE_HTML_PAGE = """
<html>
<body>
<div class="keywords-section">
    <button class="keyword-actions-trigger">stroke</button>
    <button class="keyword-actions-trigger">rehabilitation</button>
</div>
<div class="mesh-terms">
    <button>Physical Therapy</button>
    <button>Stroke Recovery</button>
</div>
</body>
</html>
"""


class TestPubMedScraper:

    def test_search_articles_success(self, scraper):
        mock_response = MagicMock()
        mock_response.json.return_value = SAMPLE_SEARCH_RESPONSE
        mock_response.raise_for_status = MagicMock()

        with patch.object(scraper.session, "get", return_value=mock_response):
            ids = scraper.search_articles("stroke rehabilitation")

        assert ids == ["12345678", "87654321", "11223344"]

    def test_search_articles_empty_results(self, scraper):
        mock_response = MagicMock()
        mock_response.json.return_value = {"esearchresult": {"idlist": []}}
        mock_response.raise_for_status = MagicMock()

        with patch.object(scraper.session, "get", return_value=mock_response):
            ids = scraper.search_articles("zzzznonexistentzzz")

        assert ids == []

    def test_search_articles_network_error(self, scraper):
        import requests
        with patch.object(scraper.session, "get", side_effect=requests.RequestException("Timeout")):
            ids = scraper.search_articles("stroke")

        assert ids == []

    def test_fetch_article_details_success(self, scraper):
        mock_response = MagicMock()
        mock_response.text = SAMPLE_XML_RESPONSE
        mock_response.raise_for_status = MagicMock()

        with patch.object(scraper.session, "get", return_value=mock_response):
            articles = scraper.fetch_article_details(["12345678"])

        assert len(articles) == 1
        assert articles[0]["pmid"] == "12345678"
        assert "Physical Therapy" in articles[0]["title"]
        assert articles[0]["authors"] == ["Smith, John", "Doe, Jane"]

    def test_fetch_article_details_empty_ids(self, scraper):
        articles = scraper.fetch_article_details([])
        assert articles == []

    def test_parse_xml_malformed(self, scraper):
        articles = scraper._parse_xml_response("<broken>xml<")
        assert articles == []

    def test_scrape_full_article_page(self, scraper):
        mock_response = MagicMock()
        mock_response.text = SAMPLE_HTML_PAGE
        mock_response.raise_for_status = MagicMock()

        with patch.object(scraper.session, "get", return_value=mock_response):
            extra = scraper.scrape_full_article_page("12345678")

        assert "stroke" in extra["keywords"]
        assert "rehabilitation" in extra["keywords"]

    def test_scrape_full_article_page_network_error(self, scraper):
        import requests
        with patch.object(scraper.session, "get", side_effect=requests.RequestException("Fail")):
            extra = scraper.scrape_full_article_page("12345678")

        assert extra["keywords"] == []
        assert extra["mesh_terms"] == []

    def test_get_research_data_integration(self, scraper):
        """Test the full pipeline with mocked network calls."""
        search_response = MagicMock()
        search_response.json.return_value = {"esearchresult": {"idlist": ["12345678"]}}
        search_response.raise_for_status = MagicMock()

        fetch_response = MagicMock()
        fetch_response.text = SAMPLE_XML_RESPONSE
        fetch_response.raise_for_status = MagicMock()

        page_response = MagicMock()
        page_response.text = SAMPLE_HTML_PAGE
        page_response.raise_for_status = MagicMock()

        with patch.object(scraper.session, "get", side_effect=[search_response, fetch_response, page_response]):
            with patch("scraper.time.sleep"):  # Skip sleep in tests
                articles = scraper.get_research_data("stroke", max_results=1)

        assert len(articles) == 1
        assert articles[0]["pmid"] == "12345678"
        assert "stroke" in articles[0].get("keywords", [])
