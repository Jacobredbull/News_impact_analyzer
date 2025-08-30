# pipeline.py

import json
import os
from news_fetcher import NewsFetcher
from preprocessor import preprocess_articles
from analyzer import get_analyzer

# Define standard filenames
PREPROCESSED_FILE = "preprocessed_articles.json"
ANALYZED_FILE = "analyzed_articles.json"


def run_fetch_pipeline():
    """
    Runs Module 1 (Fetch) and Module 2 (Preprocess).
    Saves the result to preprocessed_articles.json.
    """
    print("--- Running Fetch & Preprocess Pipeline ---")
    fetcher = NewsFetcher()

    print("Fetching US headlines...")
    us_articles = fetcher.fetch_us_headlines()
    # (You can add international fetching logic back here if you wish)

    # De-duplicate
    unique_articles = []
    seen_urls = set()
    for article in us_articles:
        if article['url'] not in seen_urls:
            unique_articles.append(article)
            seen_urls.add(article['url'])
    print(f"Fetched {len(unique_articles)} unique articles.")

    processed_articles = preprocess_articles(unique_articles)
    if not processed_articles:
        print("No articles left after preprocessing.")
        return False

    with open(PREPROCESSED_FILE, 'w', encoding='utf-8') as f:
        json.dump(processed_articles, f, ensure_ascii=False, indent=4)

    print(f"✅ Fetch pipeline complete. Saved {len(processed_articles)} articles to {PREPROCESSED_FILE}")
    return True


def run_analysis_pipeline(llm_provider: str, api_key: str = None, model_name: str = None):
    """
    Runs Module 3 (Analysis) on the preprocessed data.
    """
    print(f"--- Running Analysis Pipeline with {llm_provider} ---")
    if not os.path.exists(PREPROCESSED_FILE):
        print(f"Error: {PREPROCESSED_FILE} not found. Please run the fetch pipeline first.")
        return False

    with open(PREPROCESSED_FILE, 'r', encoding='utf-8') as f:
        processed_articles = json.load(f)

    try:
        analyzer = get_analyzer(llm_provider, api_key, model_name)
    except ValueError as e:
        print(f"Error initializing analyzer: {e}")
        return False

    analyzed_articles = []
    total = len(processed_articles)
    for i, article in enumerate(processed_articles, 1):
        print(f"-> Analyzing article {i}/{total}: '{article['title'][:50]}...'")
        try:
            analysis_data = analyzer.analyze(article['cleaned_content'])
            article['analysis'] = analysis_data
        except Exception as e:
            print(f"❗️ Error analyzing article {i}: {e}")
            article['analysis'] = {"error": str(e)}
        analyzed_articles.append(article)

    with open(ANALYZED_FILE, 'w', encoding='utf-8') as f:
        json.dump(analyzed_articles, f, ensure_ascii=False, indent=4)

    print(f"✅ Analysis pipeline complete. Results saved to {ANALYZED_FILE}")
    return True