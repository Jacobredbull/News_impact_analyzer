# dashboard.py

import streamlit as st
import json
import re
import os
import pandas as pd
from collections import defaultdict
from typing import List, Dict, Tuple
from datetime import datetime

# Import your pipeline functions and validator
from pipeline import run_fetch_pipeline, run_analysis_pipeline
from ticker_validator import get_ticker_list

# --- Constants and Helper Functions ---
ANALYZED_FILE = "analyzed_articles.json"
PREPROCESSED_FILE = "preprocessed_articles.json"
VALID_TICKERS = get_ticker_list()


def get_file_mtime(filename):
    if os.path.exists(filename):
        return datetime.fromtimestamp(os.path.getmtime(filename)).strftime('%Y-%m-%d %H:%M:%S')
    return "Never"


# --- Core Logic Functions (unchanged) ---
def load_analyzed_data(filename: str = ANALYZED_FILE) -> List[Dict]:
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return None


def extract_valid_signals(articles: List[Dict], confidence_threshold: int) -> List[Tuple[str, str]]:
    signals = []
    for article in articles:
        analysis = article.get('analysis')
        if not analysis or "error" in analysis: continue
        if analysis.get('confidence_score', 0) < confidence_threshold: continue
        sentiment = analysis.get('sentiment')
        if sentiment not in ["Positive", "Negative"]: continue
        for entity in analysis.get('affected_entities', []):
            if isinstance(entity, str):
                potential_tickers = re.findall(r'\b[A-Z]{1,5}\b', entity)
                for ticker in potential_tickers:
                    if ticker in VALID_TICKERS:
                        signals.append((ticker, sentiment))
    return signals


def score_tickers(signals: List[Tuple[str, str]]) -> Dict:
    ticker_scores = defaultdict(lambda: {'positive': 0, 'negative': 0})
    for ticker, sentiment in signals:
        if sentiment == "Positive":
            ticker_scores[ticker]['positive'] += 1
        elif sentiment == "Negative":
            ticker_scores[ticker]['negative'] += 1
    scored_tickers = {}
    for ticker, scores in ticker_scores.items():
        net_score = scores['positive'] - scores['negative']
        if net_score != 0:
            scored_tickers[ticker] = {
                'positive': scores['positive'],
                'negative': scores['negative'],
                'net_score': net_score
            }
    return scored_tickers


def display_interactive_table(title: str, dataframe: pd.DataFrame):
    st.subheader(title)
    header_cols = st.columns([0.5, 2, 1.5, 1.5, 1.5])
    header_cols[1].write("**Ticker**")
    header_cols[2].write("**Positive**")
    header_cols[3].write("**Negative**")
    header_cols[4].write("**Net Score**")
    for _, row in dataframe.iterrows():
        with st.container(border=True):
            row_cols = st.columns([0.5, 2, 1.5, 1.5, 1.5])
            if row_cols[0].button("🔎", key=f"btn_{row['Ticker']}", help=f"See details for {row['Ticker']}"):
                st.session_state['selected_ticker'] = row['Ticker']
            row_cols[1].markdown(f"<div style='margin-top: 5px;'>{row['Ticker']}</div>", unsafe_allow_html=True)
            row_cols[2].markdown(f"<div style='margin-top: 5px;'>{row['positive']}</div>", unsafe_allow_html=True)
            row_cols[3].markdown(f"<div style='margin-top: 5px;'>{row['negative']}</div>", unsafe_allow_html=True)
            row_cols[4].markdown(f"<div style='margin-top: 5px;'>{row['net_score']}</div>", unsafe_allow_html=True)


# --- Streamlit App UI ---
st.set_page_config(page_title="Stock News Sentiment Dashboard", layout="wide")
st.title("📈 Stock News Sentiment Dashboard")

if 'selected_ticker' not in st.session_state:
    st.session_state['selected_ticker'] = None

# --- Sidebar Controls ---
with st.sidebar:
    st.header("⚙️ Controls")
    st.subheader("Step 1: Fetch News")
    if st.button("Fetch Latest News"):
        with st.spinner("Fetching and preprocessing news..."):
            success = run_fetch_pipeline()
            if success:
                st.success("News fetched successfully!")
                if 'analysis_data' in st.session_state: del st.session_state['analysis_data']
                st.session_state['selected_ticker'] = None
                st.rerun()
            else:
                st.error("Failed to fetch news.")
    st.info(f"Preprocessed data last updated:\n{get_file_mtime(PREPROCESSED_FILE)}")
    st.markdown("---")

    # =====================================================================
    # ============== FIX: Corrected LLM Selection Logic ===============
    # =====================================================================
    st.subheader("Step 2: Analyze News")
    llm_provider = st.selectbox("Choose LLM Provider", ("Ollama", "OpenAI", "Google Gemini"))

    api_key = None
    # Use explicit if/elif to render the text input with a unique, static key
    if llm_provider == "OpenAI":
        api_key = st.text_input("Enter OpenAI API Key", type="password", key="openai_api_key")
    elif llm_provider == "Google Gemini":
        api_key = st.text_input("Enter Google Gemini API Key", type="password", key="gemini_api_key")

    if st.button("Analyze News", disabled=not os.path.exists(PREPROCESSED_FILE)):
        # This conditional check remains the same, but will now work correctly
        if llm_provider != "Ollama" and not api_key:
            st.warning(f"Please enter your {llm_provider} API key.")
        else:
            with st.spinner(f"Analyzing with {llm_provider}..."):
                success = run_analysis_pipeline(llm_provider, api_key)
                if success:
                    st.success("Analysis complete!")
                    if 'analysis_data' in st.session_state: del st.session_state['analysis_data']
                    st.session_state['selected_ticker'] = None
                    st.rerun()
                else:
                    st.error("Analysis failed.")
    st.info(f"Analysis last performed:\n{get_file_mtime(ANALYZED_FILE)}")
    # =====================================================================

# --- Main Dashboard Display (unchanged) ---
if 'analysis_data' not in st.session_state:
    st.session_state['analysis_data'] = load_analyzed_data()
articles = st.session_state['analysis_data']
if articles:
    # ... (The rest of the display logic is exactly the same)
    st.header("Analysis Results")
    confidence_thresh = st.slider(
        "Select Confidence Score Threshold (1-5)",
        min_value=1, max_value=5, value=3,
        help="Only analyses with a confidence score above this value will be included."
    )
    signals = extract_valid_signals(articles, confidence_thresh)
    scored_tickers = score_tickers(signals)
    if scored_tickers:
        df = pd.DataFrame.from_dict(scored_tickers, orient='index').reset_index().rename(columns={'index': 'Ticker'})
        bullish_df = df[df['net_score'] > 0].sort_values(by='net_score', ascending=False)
        bearish_df = df[df['net_score'] < 0].sort_values(by='net_score', ascending=True)

        st.subheader("Dashboard Overview")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Articles Analyzed", len(articles))
        col2.metric("Bullish Tickers Found 🟢", len(bullish_df))
        col3.metric("Bearish Tickers Found 🔴", len(bearish_df))
        st.markdown("---")

        col1, col2 = st.columns(2)
        with col1:
            display_interactive_table("Top Companies to Look At (Bullish Signals)", bullish_df)
        with col2:
            display_interactive_table("Top Companies to Look At (Bearish Signals)", bearish_df)

        if st.session_state['selected_ticker']:
            selected_ticker = st.session_state['selected_ticker']
            st.markdown("---")
            st.subheader(f"🔎 Deep Dive for: {selected_ticker}")
            relevant_articles = [
                article for article in articles
                if selected_ticker in str(article.get('analysis', {}).get('affected_entities', []))
            ]
            for article in relevant_articles:
                with st.container(border=True):
                    st.markdown(f"**{article['title']}** (Source: {article['source']})")
                    st.markdown(f"**[Read Full Article]({article['url']})** 🔗")
                    st.markdown(f"**Cleaned Content:**")
                    st.write(article.get('cleaned_content', 'NA'))
                    st.markdown(f"**AI Analysis:**")
                    st.json(article.get('analysis', {}))
                st.write("")
    else:
        st.info("No significant stock signals found with the current settings.")
else:
    st.info("Welcome! Use the controls in the sidebar to fetch and then analyze news to see the dashboard.")

st.markdown("---")
st.warning("**Disclaimer:** This is an AI-powered research tool and not financial advice.")