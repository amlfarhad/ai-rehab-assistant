"""AI-powered rehabilitation research analyzer using Anthropic's Claude API."""

import anthropic

from config import Config


class RehabAnalyzer:
    """Analyzes rehabilitation research articles using Claude LLM."""

    def __init__(self, api_key=None):
        self.client = anthropic.Anthropic(
            api_key=api_key or Config.ANTHROPIC_API_KEY
        )
        self.model = Config.CLAUDE_MODEL

    def _build_research_context(self, articles):
        """Format articles into a structured context string for the LLM."""
        context_parts = []
        for i, article in enumerate(articles, 1):
            authors_str = "; ".join(article.get("authors", []))
            keywords_str = ", ".join(article.get("keywords", []))
            context_parts.append(
                f"--- Article {i} ---\n"
                f"Title: {article['title']}\n"
                f"Authors: {authors_str}\n"
                f"Journal: {article.get('journal', 'N/A')} ({article.get('year', 'N/A')})\n"
                f"Abstract: {article['abstract']}\n"
                f"Keywords: {keywords_str}\n"
                f"URL: {article.get('url', 'N/A')}\n"
            )
        return "\n".join(context_parts)

    def analyze_research(self, articles, user_question):
        """Analyze research articles and answer a user question.

        Args:
            articles: List of article dicts from PubMedScraper.
            user_question: The user's specific question about the research.

        Returns:
            String containing the AI analysis.
        """
        if not articles:
            return "No articles were found for this query. Please try a different search term."

        context = self._build_research_context(articles)

        system_prompt = (
            "You are an expert rehabilitation research analyst. Your role is to:\n"
            "1. Synthesize findings from multiple research articles\n"
            "2. Identify key trends, methodologies, and outcomes in rehabilitation science\n"
            "3. Provide evidence-based insights with proper citations to the source articles\n"
            "4. Highlight areas of consensus and disagreement among studies\n"
            "5. Suggest practical implications for rehabilitation practitioners\n\n"
            "Always cite specific articles when making claims. Be thorough but accessible."
        )

        user_prompt = (
            f"Based on the following rehabilitation research articles, please answer "
            f"this question:\n\n"
            f"Question: {user_question}\n\n"
            f"Research Articles:\n{context}\n\n"
            f"Provide a comprehensive analysis with citations to specific articles."
        )

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=Config.MAX_TOKENS,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )
            return message.content[0].text
        except anthropic.APIError as e:
            return f"Error communicating with AI service: {e}"

    def summarize_articles(self, articles):
        """Generate a high-level summary of all articles.

        Args:
            articles: List of article dicts.

        Returns:
            String containing the summary.
        """
        if not articles:
            return "No articles to summarize."

        context = self._build_research_context(articles)

        system_prompt = (
            "You are an expert rehabilitation research summarizer. "
            "Provide concise, accurate summaries that highlight the most "
            "important findings and their clinical relevance."
        )

        user_prompt = (
            f"Please provide a structured summary of the following {len(articles)} "
            f"rehabilitation research articles. Include:\n"
            f"1. Overall themes across the research\n"
            f"2. Key findings from each study\n"
            f"3. Common methodologies used\n"
            f"4. Gaps in the current research\n"
            f"5. Suggested directions for future research\n\n"
            f"Articles:\n{context}"
        )

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=Config.MAX_TOKENS,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )
            return message.content[0].text
        except anthropic.APIError as e:
            return f"Error communicating with AI service: {e}"

    def compare_treatments(self, articles, treatment_a, treatment_b):
        """Compare two rehabilitation treatments based on the research.

        Args:
            articles: List of article dicts.
            treatment_a: First treatment to compare.
            treatment_b: Second treatment to compare.

        Returns:
            String containing the comparison analysis.
        """
        context = self._build_research_context(articles)

        system_prompt = (
            "You are an expert rehabilitation research analyst specializing in "
            "evidence-based treatment comparison. Provide balanced, objective "
            "comparisons grounded in the available research."
        )

        user_prompt = (
            f"Based on the following research articles, compare these two "
            f"rehabilitation approaches:\n\n"
            f"Treatment A: {treatment_a}\n"
            f"Treatment B: {treatment_b}\n\n"
            f"Please compare them on:\n"
            f"1. Efficacy and outcomes\n"
            f"2. Patient populations studied\n"
            f"3. Duration and intensity of treatment\n"
            f"4. Side effects or limitations\n"
            f"5. Cost-effectiveness (if mentioned)\n"
            f"6. Overall recommendation based on evidence\n\n"
            f"Research Articles:\n{context}"
        )

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=Config.MAX_TOKENS,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )
            return message.content[0].text
        except anthropic.APIError as e:
            return f"Error communicating with AI service: {e}"
