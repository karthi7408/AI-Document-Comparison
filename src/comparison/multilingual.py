import requests
import os
import time
from dotenv import load_dotenv

load_dotenv()

def chunk_text(text, max_chars=4000):
    if not text:
        return []
    return [text[i:i+max_chars] for i in range(0, len(text), max_chars)]

def azure_post_with_retry(url, headers, body, max_retries=5, timeout=10):
    for attempt in range(max_retries):
        try:
            response = requests.post(url, headers=headers, json=body, timeout=timeout)
            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", "2"))
                time.sleep(retry_after * (attempt + 1))
                continue
            if response.status_code in (502, 503, 504):
                time.sleep(2 ** attempt)
                continue
            return response
        except requests.RequestException:
            time.sleep(2 ** attempt)
    return None

class MultilingualService:
    def __init__(self, azure_translate_client=None, subscription_key=None, endpoint=None, region=None, azure_ai_service=None):
        self.azure_translate_client = azure_translate_client
        self.subscription_key = subscription_key or os.getenv('AZURE_TRANSLATOR_KEY')
        self.endpoint = endpoint or os.getenv('AZURE_TRANSLATOR_ENDPOINT')
        self.region = region or os.getenv('AZURE_TRANSLATOR_REGION')
        self.azure_ai_service = azure_ai_service

    def translate(self, text, target_language='en', source_language=None):
        """
        Translate the given text to the target language using Azure Translator Text API if configured.
        """
        if self.azure_translate_client:
            # If a client is provided, use it (custom implementation)
            return self.azure_translate_client.translate(text, target_language)
        elif self.subscription_key and self.endpoint:
            # Use Azure Translator REST API
            path = '/translate?api-version=3.0'
            params = f'&to={target_language}'
            if source_language:
                params += f'&from={source_language}'
            constructed_url = self.endpoint + path + params
            headers = {
                'Ocp-Apim-Subscription-Key': self.subscription_key,
                'Ocp-Apim-Subscription-Region': self.region or 'global',
                'Content-type': 'application/json'
            }
            translated_chunks = []
            for chunk in chunk_text(text):
                body = [{'text': chunk}]
                response = azure_post_with_retry(constructed_url, headers, body)
                if response and response.status_code == 200:
                    result = response.json()
                    if result and 'translations' in result[0]:
                        translated_chunks.append(result[0]['translations'][0]['text'])
                    elif result and isinstance(result[0], dict) and result[0].get('translations'):
                        translated_chunks.append(result[0]['translations'][0]['text'])
                    else:
                        translated_chunks.append(chunk)
                else:
                    translated_chunks.append(chunk)
            return "".join(translated_chunks)
        # Fallback: return text as-is
        return text

    def detect_language(self, text):
        """
        Detect the language of the given text using Azure Translator Text API if configured.
        """
        if self.subscription_key and self.endpoint:
            path = '/detect?api-version=3.0'
            constructed_url = self.endpoint + path
            headers = {
                'Ocp-Apim-Subscription-Key': self.subscription_key,
                'Ocp-Apim-Subscription-Region': self.region or 'global',
                'Content-type': 'application/json'
            }
            for chunk in chunk_text(text, 1000):
                body = [{'text': chunk}]
                response = azure_post_with_retry(constructed_url, headers, body)
                if response and response.status_code == 200:
                    result = response.json()
                    if result and 'language' in result[0]:
                        return result[0]['language']
                    elif result and isinstance(result[0], dict) and result[0].get('language'):
                        return result[0]['language']
            return None
        return None

    def summarize_text(self, text, language='en'):
        """
        Use Azure AI Service (GPT-4) to summarize the text in the specified language.
        Returns summary string or dict.
        """
        if self.azure_ai_service:
            return self.azure_ai_service.summarize_text(text, language=language)
        return text[:200] + "..." if len(text) > 200 else text

    def detect_pii(self, text, language='en'):
        """
        Use Azure AI Service (GPT-4) to detect PII in the text.
        Returns list of detected PII entities.
        """
        if self.azure_ai_service:
            return self.azure_ai_service.detect_pii(text, language=language)
        return []

    def extract_topics(self, text, language='en'):
        """
        Use Azure AI Service (GPT-4) to extract topics or key phrases from the text.
        Returns list of topics or key phrases.
        """
        if self.azure_ai_service and hasattr(self.azure_ai_service, "analyze_text"):
            result = self.azure_ai_service.analyze_text(text, language=language)
            return result.get("key_phrases", [])
        return []
