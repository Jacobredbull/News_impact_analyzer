# 📈 AI-Powered Stock News Analysis Dashboard

[![Python Version](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Streamlit](https://img.shields.io/badge/Made%20with-Streamlit-red.svg)](https://streamlit.io)

An interactive web application that fetches the latest financial news, uses Large Language Models (LLMs) to perform sentiment analysis, and presents actionable insights on which company stocks are trending in the news.

---
## 📸 Screenshot

*Replace this with a screenshot of your running application.*
![Dashboard Screenshot](app_screenshot.png)

---
## ✨ Features

* **📰 Multi-Source News Aggregation**: Fetches top business headlines from the US using the NewsAPI.
* **🧠 Flexible LLM Backend**: Supports multiple LLM providers for analysis:
    * **Local**: Ollama (e.g., Llama 3, Mistral)
    * **Cloud**: OpenAI (e.g., GPT-4o-mini) and Google (Gemini 1.5 Flash)
* **🤖 AI-Powered Analysis**: For each news article, the LLM extracts sentiment, affected companies, a summary, potential impact, and a confidence score.
* **✔️ Ticker Validation**: Automatically validates extracted entities against official NASDAQ and NYSE ticker lists to filter out irrelevant information.
* **🖥️ Interactive Dashboard**: A user-friendly interface built with Streamlit that allows you to:
    * Run the data fetching and analysis pipelines with separate buttons.
    * Filter results based on the AI's confidence score.
    * Click on a specific stock to get a "Deep Dive" view of the source articles that influenced its score.

---
## 🚀 Setup and Installation

Follow these steps to get the application running on your local machine.

## 1. Clone the Repository
```bash
# git clone https://github.com/Jacobredbull/News_impact_analyzer.git
cd News_impact_analyzer
```
## 2. Install Dependencies

It's recommended to use a Python virtual environment.
Create and activate a virtual environment
``` python
python -m venv .venv
source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
```

### Install all required packages from the requirements file
```python
pip install -r requirements.txt
```
## 3. Set Up API Keys

You need a NewsAPI.org key for this project.

Go to NewsAPI.org and register for a free developer key.

Set the key as an environment variable named NEWS_API_KEY.

If you plan to use OpenAI or Google Gemini, you will need to get their respective API keys and paste them into the input box in the app's sidebar.

## 4. (Optional) Set Up Ollama

If you want to use a local model:

Install Ollama.

Pull a model from your command line, for example: ollama pull llama3.1

## 5. Create the Ticker Cache

Before your first run, you must download the list of valid stock tickers. Run the validator script once from your terminal:

```Bash
python ticker_validator.py
This creates an all_tickers.txt file in your project directory.
```
