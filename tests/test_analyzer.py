"""Tests for the AI analyzer module."""

import pytest
from unittest.mock import patch, MagicMock

from analyzer import RehabAnalyzer


MOCK_ARTICLES = [
    {
        "pmid": "111",
        "title": "Stroke Rehabilitation Outcomes",
        "abstract": "Study on motor recovery after stroke using physical therapy.",
        "authors": ["Smith, J.", "Doe, A."],
        "journal": "Rehab Journal",
        "year": "2024",
        "url": "https://pubmed.ncbi.nlm.nih.gov/111/",
        "keywords": ["stroke", "rehabilitation"],
        "mesh_terms": ["Physical Therapy"],
    },
    {
        "pmid": "222",
        "title": "Virtual Reality in Spinal Cord Injury Rehab",
        "abstract": "VR-based interventions show promise for SCI patients.",
        "authors": ["Brown, B."],
        "journal": "VR Medicine",
        "year": "2023",
        "url": "https://pubmed.ncbi.nlm.nih.gov/222/",
        "keywords": ["VR", "spinal cord injury"],
        "mesh_terms": [],
    },
]


class TestRehabAnalyzer:

    def test_build_research_context(self):
        analyzer = RehabAnalyzer(api_key="test-key")
        context = analyzer._build_research_context(MOCK_ARTICLES)

        assert "Stroke Rehabilitation Outcomes" in context
        assert "Virtual Reality" in context
        assert "Smith, J.; Doe, A." in context
        assert "Article 1" in context
        assert "Article 2" in context

    def test_analyze_research_no_articles(self):
        analyzer = RehabAnalyzer(api_key="test-key")
        result = analyzer.analyze_research([], "What works?")
        assert "No articles" in result

    def test_analyze_research_success(self):
        analyzer = RehabAnalyzer(api_key="test-key")

        mock_message = MagicMock()
        mock_message.content = [MagicMock(text="Analysis: PT is effective for stroke recovery.")]

        with patch.object(analyzer.client.messages, "create", return_value=mock_message):
            result = analyzer.analyze_research(MOCK_ARTICLES, "What works best?")

        assert "PT is effective" in result

    def test_analyze_research_api_error(self):
        import anthropic
        analyzer = RehabAnalyzer(api_key="test-key")

        with patch.object(
            analyzer.client.messages, "create",
            side_effect=anthropic.APIError(
                message="Rate limit exceeded",
                request=MagicMock(),
                body=None,
            )
        ):
            result = analyzer.analyze_research(MOCK_ARTICLES, "test")

        assert "Error" in result

    def test_summarize_articles_no_articles(self):
        analyzer = RehabAnalyzer(api_key="test-key")
        result = analyzer.summarize_articles([])
        assert "No articles" in result

    def test_summarize_articles_success(self):
        analyzer = RehabAnalyzer(api_key="test-key")

        mock_message = MagicMock()
        mock_message.content = [MagicMock(text="Summary: Two studies examined rehab approaches.")]

        with patch.object(analyzer.client.messages, "create", return_value=mock_message):
            result = analyzer.summarize_articles(MOCK_ARTICLES)

        assert "Two studies" in result

    def test_compare_treatments_success(self):
        analyzer = RehabAnalyzer(api_key="test-key")

        mock_message = MagicMock()
        mock_message.content = [MagicMock(text="Comparison: PT vs VR - both show benefits.")]

        with patch.object(analyzer.client.messages, "create", return_value=mock_message):
            result = analyzer.compare_treatments(MOCK_ARTICLES, "Physical Therapy", "Virtual Reality")

        assert "both show benefits" in result
