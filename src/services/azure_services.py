import os
from dotenv import load_dotenv

load_dotenv()

try:
    from textblob import TextBlob
    import nltk
    try:
        nltk.data.find('corpora/brown')
    except LookupError:
        nltk.download('brown')
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt')
except ImportError:
    TextBlob = None

try:
    import spacy
    _spacy_nlp = spacy.load("en_core_web_sm")
except Exception:
    _spacy_nlp = None

def chunk_text(text, max_chars=4000):
    """
    Split text into chunks of max_chars for processing limits.
    """
    if not text:
        return []
    return [text[i:i+max_chars] for i in range(0, len(text), max_chars)]

def local_sentiment(text):
    if not TextBlob:
        return {'sentiment': 'neutral', 'confidence_scores': {'positive': 0.33, 'neutral': 0.34, 'negative': 0.33}}
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    if polarity > 0.2:
        return {'sentiment': 'positive', 'confidence_scores': {'positive': float(polarity), 'neutral': 1-abs(polarity), 'negative': 0.0}}
    elif polarity < -0.2:
        return {'sentiment': 'negative', 'confidence_scores': {'positive': 0.0, 'neutral': 1-abs(polarity), 'negative': float(-polarity)}}
    else:
        return {'sentiment': 'neutral', 'confidence_scores': {'positive': 0.0, 'neutral': 1.0, 'negative': 0.0}}

def local_key_phrases(text):
    if not TextBlob:
        return []
    try:
        blob = TextBlob(text)
        return list(set(blob.noun_phrases))
    except Exception:
        # Fallback: simple noun extraction if TextBlob fails (e.g., missing corpora)
        import re
        return list(set(re.findall(r'\b\w+\b', text)))

def local_entities(text):
    if _spacy_nlp:
        doc = _spacy_nlp(text)
        return [{'text': ent.text, 'category': ent.label_} for ent in doc.ents]
    # fallback: capitalized words
    import re
    return [{'text': m.group(), 'category': 'Unknown'} for m in re.finditer(r'\b[A-Z][a-z]+\b', text)]

class LocalNLPService:
    def __init__(self):
        self.healthy = True

    def health_check(self):
        return True

    def analyze_text(self, text, language="en"):
        return {
            "key_phrases": local_key_phrases(text),
            "entities": local_entities(text),
            **local_sentiment(text)
        }

    def get_sentiment(self, text, language="en"):
        return local_sentiment(text)

    def get_entities(self, text, language="en"):
        return {"entities": local_entities(text)}

    def get_key_phrases(self, text, language="en"):
        return local_key_phrases(text)

    def detect_language(self, text):
        # Simple heuristic
        if not text or not TextBlob:
            return "en"
        blob = TextBlob(text)
        try:
            return blob.detect_language()
        except Exception:
            return "en"

class AzureAIService:
    def __init__(self, endpoint=None, api_key=None, region=None, deployment_name=None):
        self.endpoint =  os.getenv('AZURE_AI_ENDPOINT')
        # Ensure both OpenAI and Azure OpenAI env vars are set for SDK compatibility
        self.api_key =  os.getenv('AZURE_AI_API_KEY') 
        self.region = os.getenv('AZURE_AI_REGION')
        self.deployment_name = deployment_name or os.getenv('AZURE_AI_DEPLOYMENT', 'gpt-4')
        # Try to import Azure OpenAI SDK if available and credentials are present
        self.azure_openai = None
        if self.api_key:
            try:
                from openai import AzureOpenAI
                self.azure_openai = AzureOpenAI(
                    api_key=self.api_key,
                    azure_endpoint=self.endpoint,
                    api_version="2025-01-01-preview",
                    azure_deployment=self.deployment_name
                )
            except ImportError:
                self.azure_openai = None
            except Exception as ex:
                print("AzureOpenAI SDK initialization error:", ex)
                self.azure_openai = None

    def _headers(self):
        return {
            "api-key": self.api_key,
            "Content-Type": "application/json"
        }

    def _get_chat_url(self):
        if not self.endpoint or not self.deployment_name:
            return None
        endpoint = self.endpoint.rstrip("/")
        return f"{endpoint}/openai/deployments/{self.deployment_name}/chat/completions?api-version=2024-02-15-preview"

    def summarize_text(self, text, language="en"):
        if self.azure_openai:
            try:
                response = self.azure_openai.chat.completions.create(
                    model=self.deployment_name,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": f"Summarize the following text in {language}:\n\n{text}"}
                    ],
                    max_tokens=256,
                    temperature=0.3
                )
                return response.choices[0].message.content.strip()
            except Exception:
                pass


    def generate_text(self, prompt, language="en"):
        if self.azure_openai:
            try:
                response = self.azure_openai.chat.completions.create(
                    model=self.deployment_name,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=256,
                    temperature=0.3
                )
                content = response.choices[0].message.content.strip()
                if content:
                    return {"generated_text": content}
            except Exception:
                pass


    def detect_pii(self, text, language="en"):
        if self.azure_openai:
            try:
                response = self.azure_openai.chat.completions.create(
                    model=self.deployment_name,
                    messages=[
                        {"role": "system", "content": "You are a data privacy assistant."},
                        {"role": "user", "content":
                            "Extract all personally identifiable information (PII) such as names, addresses, phone numbers, emails, "
                            "government IDs, and any sensitive data from the following text. "
                            "Return the PII as a JSON list of strings. If none, return an empty list.\n\n"
                            f"Text:\n{text}"
                        }
                    ],
                    max_tokens=256,
                    temperature=0.0
                )
                import json
                content = response.choices[0].message.content.strip()
                try:
                    pii_entities = json.loads(content)
                    if isinstance(pii_entities, list):
                        return pii_entities
                except Exception:
                    return [content]
            except Exception:
                pass
        
class AzureBlobStorageService:
    def __init__(self, connection_string=None, container_name=None):
        from azure.storage.blob import BlobServiceClient
        connection_string = connection_string or os.getenv('AZURE_BLOB_CONNECTION_STRING')
        container_name = container_name or os.getenv('AZURE_BLOB_CONTAINER', 'documents')
        self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        self.container_client = self.blob_service_client.get_container_client(container_name)
        try:
            self.container_client.create_container()
        except Exception:
            pass

    def upload_text(self, blob_name, text):
        self.container_client.upload_blob(blob_name, text, overwrite=True)

    def download_text(self, blob_name):
        blob_client = self.container_client.get_blob_client(blob_name)
        return blob_client.download_blob().readall().decode('utf-8')

    def list_blobs(self):
        return [blob.name for blob in self.container_client.list_blobs()]

class AzureTableAuditService:
    def __init__(self, connection_string=None, table_name=None):
        from azure.data.tables import TableServiceClient
        connection_string = connection_string or os.getenv('AZURE_TABLE_CONNECTION_STRING')
        table_name = table_name or os.getenv('AZURE_TABLE_NAME', 'AuditLog')
        self.table_service = TableServiceClient.from_connection_string(conn_str=connection_string)
        self.table_client = self.table_service.get_table_client(table_name)
        try:
            self.table_client.create_table()
        except Exception:
            pass

    def log_audit(self, user_id, action, doc1_name, doc2_name, result_summary, status="Success"):
        from uuid import uuid4
        import datetime
        entity = {
            "PartitionKey": user_id or "anonymous",
            "RowKey": str(uuid4()),
            "Action": action,
            "Doc1Name": doc1_name,
            "Doc2Name": doc2_name,
            "ResultSummary": result_summary,
            "Status": status,
            "Timestamp": datetime.datetime.utcnow().isoformat()
        }
        self.table_client.create_entity(entity=entity)

    def get_audit_logs(self, user_id=None):
        if user_id:
            return list(self.table_client.query_entities(f"PartitionKey eq '{user_id}'"))
        return list(self.table_client.list_entities())

