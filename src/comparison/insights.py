# Required libraries for insights.py and related analytics:
# matplotlib, numpy, wordcloud

# To install, run the following commands in your terminal or command prompt:
# pip install matplotlib numpy wordcloud

# If you use Azure NLP or translation services, you may also need:
# pip install requests

import matplotlib.pyplot as plt
import io
import base64
from wordcloud import WordCloud
import numpy as np

class InsightsGenerator:
    def __init__(self, semantic_analyzer, sentiment_classifier, tone_analyzer, diff_view, azure_ai_service=None):
        self.semantic_analyzer = semantic_analyzer
        self.sentiment_classifier = sentiment_classifier
        self.tone_analyzer = tone_analyzer
        self.diff_view = diff_view
        self.azure_ai_service = azure_ai_service

    def get_document_insights(self, doc1, doc2):
        """
        Generate insights from two documents using all analysis modules.
        Returns a dict with all metrics and insights.
        """
        # Semantic Analysis
        semantic = self.semantic_analyzer.analyze_semantics(doc1, doc2)
        semantic_outlier = None
        if hasattr(self.semantic_analyzer, "get_semantic_outliers"):
            semantic_outlier = self.semantic_analyzer.get_semantic_outliers([doc1, doc2])
        semantic_topics_doc1 = self.semantic_analyzer.get_document_topics(doc1)
        semantic_topics_doc2 = self.semantic_analyzer.get_document_topics(doc2)
        semantic_diversity = self.semantic_analyzer.get_semantic_diversity_score([doc1, doc2])
        semantic_common_unique = self.semantic_analyzer.get_common_and_unique_phrases([doc1, doc2])

        # Sentiment Analysis
        sentiment1 = self.sentiment_classifier.classify_sentiment(doc1)
        sentiment2 = self.sentiment_classifier.classify_sentiment(doc2)
        sentiment_comparison = self.sentiment_classifier.compare_sentiment(doc1, doc2)
        sentiment_risk1 = self.sentiment_classifier.assess_risk(sentiment1)
        sentiment_risk2 = self.sentiment_classifier.assess_risk(sentiment2)
        sentiment_alerts = self.sentiment_classifier.get_sentiment_alerts([doc1, doc2])
        sentiment_trend = self.sentiment_classifier.get_sentiment_trend([doc1, doc2])
        sentiment_variance = self.sentiment_classifier.get_sentiment_variance([doc1, doc2])
        sentiment_extreme = self.sentiment_classifier.get_most_extreme_sentiment([doc1, doc2])

        # Tone Shift
        tone_shift = self.tone_analyzer.analyze_tone_shift(doc1, doc2)
        tone_distribution = self.tone_analyzer.get_tone_distribution([doc1, doc2])
        tone_trend = self.tone_analyzer.get_tone_trend([doc1, doc2])
        tone_change_summary = self.tone_analyzer.get_tone_change_summary([doc1, doc2])
        tone_controversial_1 = self.tone_analyzer.is_tone_controversial(doc1)
        tone_controversial_2 = self.tone_analyzer.is_tone_controversial(doc2)
        
        # Diff
        diff_summary = self.diff_view.generate_diff_summary(doc1, doc2)
        diff_percentage = self.diff_view.get_diff_percentage(doc1, doc2)
        diff_stats = self.diff_view.get_diff_stats(doc1, doc2)
        diff_blocks = self.diff_view.get_diff_blocks(doc1, doc2)
        diff_word_stats = self.diff_view.get_word_diff_stats(doc1, doc2)
        diff_as_dict = self.diff_view.get_diff_as_dict(doc1, doc2)
        ai_diff_changes=self.diff_view.get_ai_generated_diff_explanation(doc1, doc2) if self.azure_ai_service else None
        ai_highlighted_changes = self.diff_view.get_ai_highlighted_changes(doc1, doc2) if self.azure_ai_service else None
        ai_risk_assessment = self.diff_view.get_ai_risk_assessment_on_diff(doc1, doc2) if self.azure_ai_service else None

        # Multilingual/Translation
        detected_lang_doc1 = self.semantic_analyzer.multilingual_service.detect_language(doc1) if self.semantic_analyzer.multilingual_service else 'en'
        detected_lang_doc2 = self.semantic_analyzer.multilingual_service.detect_language(doc2) if self.semantic_analyzer.multilingual_service else 'en'
     
        # Compliance & PII
        compliance_flags_doc1 = self.tone_analyzer.get_compliance_flags(doc1)
        compliance_flags_doc2 = self.tone_analyzer.get_compliance_flags(doc2)
        pii_doc1 = self.sentiment_classifier.detect_pii(doc1) if self.azure_ai_service else []
        pii_doc2 = self.sentiment_classifier.detect_pii(doc2) if self.azure_ai_service else []



        # Visualizations
        docs = [doc1, doc2]
        sentiment_heatmap = self.sentiment_classifier.get_sentiment_heatmap_data(docs)
        heatmap_img = self.generate_sentiment_heatmap(sentiment_heatmap)
        metrics_bar_img = self.generate_metrics_comparison_chart(doc1, doc2)



        # Compose insights
        insights = {
            #metrics
            "semantic_similarity": semantic.get("similarity_score"),
            "semantic_diversity": semantic_diversity,
            "diff_percentage": diff_percentage,
            "sentiment_doc1": sentiment1.get("sentiment"),
            "sentiment_doc2": sentiment2.get("sentiment"),
            "sentiment_risk_doc1": sentiment_risk1,
            "sentiment_risk_doc2": sentiment_risk2,
            "tone_doc1": tone_shift.get("document1_tone"),
            "tone_doc2": tone_shift.get("document2_tone"),
            "tone_shift_detected": tone_shift.get("tone_shift_detected"),
            "detected_language_doc1": detected_lang_doc1,
            "detected_language_doc2": detected_lang_doc2,

            # Semantic
            "semantic_outlier": semantic_outlier,
            "semantic_topics_doc1": semantic_topics_doc1,
            "semantic_topics_doc2": semantic_topics_doc2,
            "semantic_common_phrases": semantic_common_unique.get('common', []),
            "semantic_unique_phrases_doc1": semantic_common_unique.get('unique', [[], []])[0],
            "semantic_unique_phrases_doc2": semantic_common_unique.get('unique', [[], []])[1],
            "semantic_diversity": semantic_diversity,
            # Sentiment
            "sentiment_comparison": sentiment_comparison,
            "sentiment_trend": sentiment_trend,
            "sentiment_variance": sentiment_variance,
            "sentiment_extreme": sentiment_extreme,
            # Tone
            "tone_distribution": tone_distribution,
            "tone_trend": tone_trend,
            "tone_change_summary": tone_change_summary,
            "tone_controversial_doc1": tone_controversial_1,
            "tone_controversial_doc2": tone_controversial_2,
            # Diff
            "diff_summary": diff_summary,
            "diff_stats": diff_stats,
            "diff_blocks": diff_blocks,
            "diff_word_stats": diff_word_stats,
            "diff_as_dict": diff_as_dict,
            "ai_diff_changes": ai_diff_changes,
            "ai_highlighted_changes": ai_highlighted_changes,
            "ai_risk_assessment": ai_risk_assessment,
            # Compliance & PII
            "compliance_flags_doc1": compliance_flags_doc1,
            "compliance_flags_doc2": compliance_flags_doc2,
            "pii_doc1": pii_doc1,
            "pii_doc2": pii_doc2,

            # Visualizations
            "charts": self.generate_dashboard_charts(doc1, doc2),
            "sentiment_heatmap": heatmap_img,
            "metrics_comparison": metrics_bar_img,
        }
        return insights

    def generate_dashboard_charts(self, doc1, doc2):
        """
        Generate base64-encoded chart images for dashboard display.
        Returns a dict of chart names to base64 PNG strings.
        """
        charts = {}

        # Sentiment bar chart
        sentiment1 = self.sentiment_classifier.classify_sentiment(doc1)
        sentiment2 = self.sentiment_classifier.classify_sentiment(doc2)
        labels = ['Positive', 'Neutral', 'Negative']
        scores1 = [sentiment1['confidence_scores'].get(l.lower(), 0) for l in labels]
        scores2 = [sentiment2['confidence_scores'].get(l.lower(), 0) for l in labels]
        fig, ax = plt.subplots()
        x = range(len(labels))
        ax.bar([i - 0.2 for i in x], scores1, width=0.4, label='Doc 1')
        ax.bar([i + 0.2 for i in x], scores2, width=0.4, label='Doc 2')
        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        ax.set_ylabel('Sentiment Score')
        ax.set_title('Sentiment Comparison')
        ax.legend()
        charts['sentiment_comparison'] = self._fig_to_base64(fig)
        plt.close(fig)

        # Diff pie chart
        diff_stats = self.diff_view.get_diff_stats(doc1, doc2)
        pie_labels = ['Unchanged', 'Added', 'Removed']
        pie_sizes = [diff_stats['unchanged'], diff_stats['added'], diff_stats['removed']]
        fig2, ax2 = plt.subplots()
        ax2.pie(pie_sizes, labels=pie_labels, autopct='%1.1f%%', startangle=90)
        ax2.set_title('Document Diff Overview')
        charts['diff_pie'] = self._fig_to_base64(fig2)
        plt.close(fig2)

        # Semantic similarity gauge (as a bar)
        semantic_score = self.semantic_analyzer.analyze_semantics(doc1, doc2)['similarity_score']
        fig3, ax3 = plt.subplots(figsize=(4, 1))
        ax3.barh(['Similarity'], [semantic_score], color='skyblue')
        ax3.set_xlim(0, 1)
        ax3.set_title('Semantic Similarity')
        for spine in ax3.spines.values():
            spine.set_visible(False)
        charts['semantic_similarity'] = self._fig_to_base64(fig3)
        plt.close(fig3)

        # Tone shift bar
        tone1 = self.tone_analyzer.detect_tone(doc1)
        tone2 = self.tone_analyzer.detect_tone(doc2)
        tones = [tone1, tone2]
        fig4, ax4 = plt.subplots()
        ax4.bar(['Doc 1', 'Doc 2'], [1, 1], color=['green' if t == 'Positive' else 'red' if t == 'Negative' else 'gray' for t in tones])
        ax4.set_ylim(0, 1.5)
        ax4.set_title('Tone Overview')
        charts['tone_overview'] = self._fig_to_base64(fig4)
        plt.close(fig4)

        return charts

    def generate_wordcloud_chart(self, keyword_freq):
        """
        Generate a word cloud image from keyword frequency dict.
        Returns base64 PNG string.
        """
        if not keyword_freq:
            return ""
        wc = WordCloud(width=400, height=200, background_color='white')
        wc.generate_from_frequencies(keyword_freq)
        fig, ax = plt.subplots(figsize=(5, 2.5))
        ax.imshow(wc, interpolation='bilinear')
        ax.axis('off')
        img = self._fig_to_base64(fig)
        plt.close(fig)
        return img

    def generate_sentiment_heatmap(self, sentiment_heatmap):
        """
        Generate a heatmap for sentiment scores across documents.
        Returns base64 PNG string.
        """
        if not sentiment_heatmap:
            return ""
        arr = np.array(sentiment_heatmap)
        fig, ax = plt.subplots()
        cax = ax.imshow(arr, cmap='coolwarm', aspect='auto')
        ax.set_xticks([0, 1, 2])
        ax.set_xticklabels(['Positive', 'Neutral', 'Negative'])
        ax.set_yticks([0, 1])
        ax.set_yticklabels(['Doc 1', 'Doc 2'])
        fig.colorbar(cax, orientation='vertical')
        ax.set_title('Sentiment Heatmap')
        img = self._fig_to_base64(fig)
        plt.close(fig)
        return img

    def generate_metrics_comparison_chart(self, doc1, doc2):
        """
        Generate a bar chart comparing key metrics between two documents.
        Returns base64 PNG string.
        """
        metrics = [
            ('Semantic Similarity', self.semantic_analyzer.analyze_semantics(doc1, doc2)['similarity_score']),
            ('Diff %', self.diff_view.get_diff_percentage(doc1, doc2)),
            ('Sentiment Pos Doc1', self.sentiment_classifier.classify_sentiment(doc1)['confidence_scores'].get('positive', 0)),
            ('Sentiment Pos Doc2', self.sentiment_classifier.classify_sentiment(doc2)['confidence_scores'].get('positive', 0)),
            ('Sentiment Neg Doc1', self.sentiment_classifier.classify_sentiment(doc1)['confidence_scores'].get('negative', 0)),
            ('Sentiment Neg Doc2', self.sentiment_classifier.classify_sentiment(doc2)['confidence_scores'].get('negative', 0)),
        ]
        labels, values = zip(*metrics)
        fig, ax = plt.subplots(figsize=(8, 3))
        ax.bar(labels, values, color='skyblue')
        ax.set_ylabel('Score / Percentage')
        ax.set_title('Metrics Comparison')
        ax.set_xticklabels(labels, rotation=30, ha='right')
        img = self._fig_to_base64(fig)
        plt.close(fig)
        return img

    def _fig_to_base64(self, fig):
        """
        Convert a matplotlib figure to a base64-encoded PNG string.
        """
        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        buf.close()
        return img_base64
