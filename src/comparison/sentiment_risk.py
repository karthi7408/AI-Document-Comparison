class SentimentRiskClassifier:
    def __init__(self, nlp_service=None, multilingual_service=None, azure_ai_service=None):
        self.nlp_service = nlp_service
        self.multilingual_service = multilingual_service
        self.azure_ai_service = azure_ai_service

    def health_check(self):
        return True

    def translate_document(self, document, target_language='en'):
        if self.multilingual_service:
            return self.multilingual_service.translate(document, target_language)
        return document

    def classify_sentiment(self, document_content, lang='en'):
        document_content = self.translate_document(document_content, lang)
        sentiment_result = self.nlp_service.get_sentiment(document_content)
        return sentiment_result

    def assess_risk(self, sentiment_result):
        """
        Assess risk based on sentiment result.

        Returns:
        str: 'High', 'Medium', or 'Low'
        """
        sentiment = sentiment_result.get('sentiment', 'neutral')
        scores = sentiment_result.get('confidence_scores', {})
        if sentiment == 'negative' and scores.get('negative', 0) > 0.7:
            return 'High'
        elif sentiment == 'neutral' or scores.get('neutral', 0) > 0.5:
            return 'Medium'
        else:
            return 'Low'

    def get_sentiment_details(self, document_content):
        """
        Get detailed sentiment analysis including scores and label.
        """
        return self.classify_sentiment(document_content)

    def compare_sentiment(self, doc1, doc2):
        """
        Compare sentiment between two documents.

        Returns:
        dict: Sentiment and score comparison.
        """
        sentiment1 = self.classify_sentiment(doc1)
        sentiment2 = self.classify_sentiment(doc2)
        return {
            "doc1_sentiment": sentiment1,
            "doc2_sentiment": sentiment2,
            "same_sentiment": sentiment1['sentiment'] == sentiment2['sentiment']
        }

    def get_sentiment_trend(self, documents):
        """
        Analyze sentiment trend across a list of documents.
        Returns:
        list of dict: [{'sentiment': str, 'confidence_scores': dict}, ...]
        """
        return [self.classify_sentiment(doc) for doc in documents]

    def get_sentiment_distribution(self, documents):
        """
        Get distribution of sentiment labels in a list of documents.
        Returns:
        dict: {sentiment_label: count}
        """
        from collections import Counter
        sentiments = [self.classify_sentiment(doc)['sentiment'] for doc in documents]
        return dict(Counter(sentiments))

    def explain_sentiment(self, sentiment_result):
        """
        Provide a human-readable explanation for the sentiment result.
        """
        sentiment = sentiment_result.get('sentiment', 'neutral')
        scores = sentiment_result.get('confidence_scores', {})
        explanation = f"Sentiment: {sentiment.capitalize()} ("
        explanation += ", ".join(f"{k}: {v:.2f}" for k, v in scores.items())
        explanation += ")"
        if sentiment == 'positive':
            explanation += " - The document expresses a positive tone."
        elif sentiment == 'negative':
            explanation += " - The document expresses a negative tone."
        else:
            explanation += " - The document is mostly neutral."
        return explanation

    def get_average_sentiment_score(self, documents):
        """
        Compute the average sentiment scores across a list of documents.
        Returns:
        dict: {'positive': float, 'neutral': float, 'negative': float}
        """
        if not documents:
            return {'positive': 0.0, 'neutral': 0.0, 'negative': 0.0}
        total = {'positive': 0.0, 'neutral': 0.0, 'negative': 0.0}
        for doc in documents:
            scores = self.classify_sentiment(doc).get('confidence_scores', {})
            for k in total:
                total[k] += scores.get(k, 0.0)
        count = len(documents)
        return {k: round(v / count, 3) for k, v in total.items()}

    def get_most_extreme_sentiment(self, documents):
        """
        Find the document with the most extreme sentiment (highest positive or negative score).
        Returns:
        dict: {'index': int, 'sentiment': str, 'score': float}
        """
        max_score = -1
        max_idx = -1
        max_sentiment = None
        for idx, doc in enumerate(documents):
            scores = self.classify_sentiment(doc).get('confidence_scores', {})
            for sentiment in ['positive', 'negative']:
                if scores.get(sentiment, 0) > max_score:
                    max_score = scores[sentiment]
                    max_idx = idx
                    max_sentiment = sentiment
        return {'index': max_idx, 'sentiment': max_sentiment, 'score': max_score}

    def is_document_controversial(self, document_content, threshold=0.15):
        """
        Returns True if the sentiment confidence scores are close (no clear dominant sentiment).
        """
        scores = self.classify_sentiment(document_content).get('confidence_scores', {})
        if not scores:
            return False
        values = sorted(scores.values(), reverse=True)
        if len(values) < 2:
            return False
        return abs(values[0] - values[1]) < threshold

    def get_sentiment_summary_report(self, documents):
        """
        Returns a human-readable summary for a list of documents.
        """
        distribution = self.get_sentiment_distribution(documents)
        avg_scores = self.get_average_sentiment_score(documents)
        return (
            f"Sentiment Distribution: {distribution}\n"
            f"Average Scores: {avg_scores}\n"
            f"Most Extreme Sentiment: {self.get_most_extreme_sentiment(documents)}"
        )

    def get_sentiment_variance(self, documents):
        """
        Measures variance in sentiment scores across documents.
        Returns:
        dict: {'positive': float, 'neutral': float, 'negative': float}
        """
        import numpy as np
        scores = {'positive': [], 'neutral': [], 'negative': []}
        for doc in documents:
            cs = self.classify_sentiment(doc).get('confidence_scores', {})
            for k in scores:
                scores[k].append(cs.get(k, 0.0))
        return {k: float(np.var(scores[k])) if scores[k] else 0.0 for k in scores}

    def get_priority_actions(self, document_content):
        """
        Identify priority actions based on sentiment and risk assessment.

        Returns:
        list: List of recommended actions for the user.
        """
        sentiment_result = self.classify_sentiment(document_content)
        risk = self.assess_risk(sentiment_result)
        actions = []

        if risk == 'High':
            actions.append("Immediate review required due to high negative sentiment.")
            actions.append("Escalate to management or compliance team.")
        elif risk == 'Medium':
            actions.append("Monitor document for potential issues.")
            actions.append("Consider a follow-up review.")
        else:
            actions.append("No immediate action required. Document is low risk.")

        # Additional suggestions based on sentiment
        sentiment = sentiment_result.get('sentiment', 'neutral')
        if sentiment == 'negative':
            actions.append("Investigate causes of negative sentiment.")
        elif sentiment == 'positive':
            actions.append("Leverage positive aspects in communications.")

        # Controversial/uncertain sentiment
        if self.is_document_controversial(document_content):
            actions.append("Sentiment is mixed; consider manual review for clarity.")

        return actions

    def get_priority_action_report(self, document_content):
        """
        Generate a user-friendly report of priority actions for the document.

        Returns:
        str: Formatted action list.
        """
        actions = self.get_priority_actions(document_content)
        if not actions:
            return "No priority actions identified."
        return "Priority Actions:\n" + "\n".join(f"- {action}" for action in actions)

    def get_sentiment_time_series(self, documents, timestamps):
        """
        Returns a time series of sentiment scores for plotting/document tracking.
        Parameters:
        documents (list): List of document texts.
        timestamps (list): List of timestamps corresponding to documents.
        Returns:
        list of dict: [{'timestamp': ..., 'sentiment': ..., 'scores': {...}}, ...]
        """
        series = []
        for doc, ts in zip(documents, timestamps):
            result = self.classify_sentiment(doc)
            series.append({
                'timestamp': ts,
                'sentiment': result.get('sentiment'),
                'scores': result.get('confidence_scores', {})
            })
        return series

    def get_sentiment_alerts(self, documents, threshold=0.7):
        """
        Returns a list of alerts for documents with high negative sentiment.
        Parameters:
        documents (list): List of document texts.
        threshold (float): Negative score threshold for alerting.
        Returns:
        list of dict: [{'index': i, 'alert': str}, ...]
        """
        alerts = []
        for i, doc in enumerate(documents):
            scores = self.classify_sentiment(doc).get('confidence_scores', {})
            if scores.get('negative', 0) > threshold:
                alerts.append({'index': i, 'alert': 'High negative sentiment detected'})
        return alerts

    def get_sentiment_change_points(self, documents):
        """
        Returns indices where sentiment label changes in a sequence of documents.
        """
        sentiments = [self.classify_sentiment(doc).get('sentiment') for doc in documents]
        change_points = []
        for i in range(1, len(sentiments)):
            if sentiments[i] != sentiments[i-1]:
                change_points.append(i)
        return change_points

    def get_sentiment_heatmap_data(self, documents):
        """
        Returns a matrix of sentiment scores for each document for heatmap visualization.
        Returns:
        list of lists: [[positive, neutral, negative], ...]
        """
        heatmap = []
        for doc in documents:
            scores = self.classify_sentiment(doc).get('confidence_scores', {})
            heatmap.append([
                scores.get('positive', 0.0),
                scores.get('neutral', 0.0),
                scores.get('negative', 0.0)
            ])
        return heatmap

    def detect_pii(self, document_content, lang='en'):
        """
        Detect PII in the document using Azure AI Service (GPT-4) if available.
        Returns list of detected PII entities.
        """
        if self.azure_ai_service:
            return self.azure_ai_service.detect_pii(document_content, language=lang)
        return []

    def get_ai_sentiment_explanation(self, document_content, lang='en'):
        """
        Use Azure AI (GPT-4) to generate a plain-language explanation of the sentiment analysis result.
        """
        if self.azure_ai_service:
            sentiment = self.classify_sentiment(document_content, lang)
            prompt = (
                "Given the following document and its sentiment analysis result, explain in simple terms why this sentiment was detected. "
                "Highlight any important phrases or sections that contributed to the sentiment.\n\n"
                f"Document:\n{document_content}\n\n"
                f"Sentiment Analysis Result: {sentiment}\n"
            )
            result = self.azure_ai_service.generate_text(prompt, language=lang)
            return result.get("generated_text", "")
        return self.explain_sentiment(self.classify_sentiment(document_content, lang))
