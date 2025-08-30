# analyzer.py

import ollama
import openai
import google.generativeai as genai
import json
from typing import List, Dict

# --- The Prompt is now a shared constant ---
ANALYSIS_PROMPT = """
As an expert financial analyst, analyze the following news article.
Provide your output strictly in a JSON format with the following keys:
- "sentiment": "Positive", "Negative", or "Neutral".
- "affected_entities": A list of stock tickers or market sectors directly affected.
- "event_summary": A brief, one-sentence summary of the key event.
- "potential_impact": A concise analysis of the potential impact on the entities.
- "confidence_score": A score from 1 to 5 on your confidence in this analysis.

Article: "{article_content}"

JSON Output:
"""


# --- Base Class (Defines the interface) ---
class LLMAnalyzer:
    """Abstract base class for different LLM providers."""

    def analyze(self, article_content: str) -> Dict:
        raise NotImplementedError("Subclasses must implement this method.")


# --- Ollama Implementation ---
class OllamaAnalyzer(LLMAnalyzer):
    def __init__(self, model_name: str = "llama3.1"):
        self.model_name = model_name

    def analyze(self, article_content: str) -> Dict:
        prompt = ANALYSIS_PROMPT.format(article_content=article_content)
        response = ollama.chat(
            model=self.model_name,
            messages=[{'role': 'user', 'content': prompt}],
            format='json'
        )
        return json.loads(response['message']['content'])


# --- OpenAI (ChatGPT) Implementation ---
class OpenAIAnalyzer(LLMAnalyzer):
    def __init__(self, api_key: str, model_name: str = "gpt-4o-mini"):
        openai.api_key = api_key
        self.model_name = model_name

    def analyze(self, article_content: str) -> Dict:
        prompt = ANALYSIS_PROMPT.format(article_content=article_content)
        response = openai.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)


# --- Google (Gemini) Implementation ---
class GeminiAnalyzer(LLMAnalyzer):
    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash"):
        genai.configure(api_key=api_key)
        self.model_name = model_name

    def analyze(self, article_content: str) -> Dict:
        # Gemini needs a slightly different prompt to ensure JSON output
        prompt = ANALYSIS_PROMPT.format(
            article_content=article_content) + "\nEnsure your entire response is only the raw JSON object, without any markdown formatting."

        model = genai.GenerativeModel(self.model_name)
        response = model.generate_content(prompt)

        # Clean up Gemini's occasional markdown formatting
        cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
        return json.loads(cleaned_response)


# --- Factory Function (To easily create an analyzer) ---
def get_analyzer(provider: str, api_key: str = None, model_name: str = None) -> LLMAnalyzer:
    """Factory function to get the correct analyzer instance."""
    if provider == "Ollama":
        return OllamaAnalyzer(model_name=model_name or "llama3.1")
    elif provider == "OpenAI":
        if not api_key: raise ValueError("OpenAI API key is required.")
        return OpenAIAnalyzer(api_key=api_key, model_name=model_name or "gpt-4o-mini")
    elif provider == "Google Gemini":
        if not api_key: raise ValueError("Google Gemini API key is required.")
        return GeminiAnalyzer(api_key=api_key, model_name=model_name or "gemini-1.5-flash")
    else:
        raise ValueError(f"Unknown LLM provider: {provider}")