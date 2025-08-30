# preprocessor.py

import re
from typing import List, Dict


def clean_article_content(text: str) -> str:
    """
    Performs minimal but essential cleaning on a single piece of text.
    """
    # 1. Remove the NewsAPI truncation notice, e.g., "... [+123 chars]"
    # This regex looks for a space, square brackets with a plus sign, digits,
    # the word "chars", and then the end of the string.
    text = re.sub(r'\s*\[\+\d+\s*chars\]\s*$', '', text)

    # 2. Collapse multiple whitespace characters (spaces, tabs, newlines) into a single space
    text = re.sub(r'\s+', ' ', text)

    # 3. Remove any leading or trailing whitespace
    return text.strip()


def preprocess_articles(articles: List[Dict]) -> List[Dict]:
    """
    The main function for Module 2. It takes a list of articles, cleans their
    content, and filters out any that are empty after cleaning.
    """
    print("\n--- Running Module 2: Preprocessing ---")

    processed_articles = []
    for article in articles:
        # Ensure the article has content and it's a string
        if not article.get('content') or not isinstance(article['content'], str):
            continue

        cleaned_content = clean_article_content(article['content'])

        # Only include articles that still have text after cleaning
        if cleaned_content:
            # We add a new key 'cleaned_content' to preserve the original.
            # This is good practice for debugging and traceability.
            article['cleaned_content'] = cleaned_content
            processed_articles.append(article)

    print(f"Filtered down to {len(processed_articles)} articles with valid content.")
    return processed_articles