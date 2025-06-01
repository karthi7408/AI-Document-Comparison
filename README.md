# Document Comparison App

## Overview

This application allows you to compare two documents for semantic similarity, sentiment, tone, and more.  
It uses local NLP (TextBlob and spaCy) for all core NLP features, ensuring fast and robust analysis without dependency on Azure NLP services.

## Features

- Document upload and comparison (txt, docx, pdf, csv, xlsx, md)
- Semantic similarity and difference analysis
- Sentiment analysis (TextBlob)
- Entity extraction (spaCy)
- Tone shift detection
- Diff and word-level comparison
- Visualizations (charts, word clouds)
- Multilingual support (Azure Translator, optional)
- Storage and audit logging (Azure Blob/Table, optional)
- AI-powered explanations (Azure OpenAI, optional)

## Requirements

- Python 3.8+
- See `requirements.txt` for dependencies

## Quick Start

1. Install dependencies:
    ```
    pip install -r requirements.txt
    ```
2. Download spaCy English model:
    ```
    python -m spacy download en_core_web_sm
    ```
3. Set up your `.env` file (see `.env.example` for reference).
4. Run the app:
    ```
    python src/main.py
    ```

## Notes

- **No Azure NLP**: All NLP is performed locally using TextBlob and spaCy.
- **Azure AI/Storage**: Azure AI (OpenAI), Blob, and Table services are still supported for advanced features and storage.
- **Multilingual**: Translation uses Azure Translator if configured, otherwise returns text as-is.
- **Performance**: Local NLP is fast and suitable for most document types.

## License

MIT License