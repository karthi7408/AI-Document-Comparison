class ToneShiftAnalyzer:
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

    def detect_tone(self, document, lang='en'):
        document = self.translate_document(document, lang)
        analysis = self.nlp_service.analyze_text(document)
        sentiment = analysis.get("sentiment", "neutral")
        if sentiment == "positive":
            return "Positive"
        if sentiment == "negative":
            return "Negative"
        return "Neutral"

    def analyze_tone_shift(self, document1, document2):
        tone1 = self.detect_tone(document1)
        tone2 = self.detect_tone(document2)
        shift_detected = tone1 != tone2
        details = self.get_tone_shift_details(document1, document2)
        return {
            "document1_tone": tone1,
            "document2_tone": tone2,
            "tone_shift_detected": shift_detected,
            "tone_shift_details": details
        }

    def get_tone_shift_details(self, document1, document2):
        tone1 = self.detect_tone(document1)
        tone2 = self.detect_tone(document2)
        if tone1 == tone2:
            return f"No tone shift detected. Both documents are '{tone1}'."
        return f"Tone shifted from '{tone1}' to '{tone2}'."

    def get_tone_distribution(self, documents):
        from collections import Counter
        tones = [self.detect_tone(doc) for doc in documents]
        return dict(Counter(tones))

    def is_tone_controversial(self, document, threshold=0.2):
        analysis = self.nlp_service.analyze_text(document)
        emotions = analysis.get("emotions", {})
        strong = [v for v in emotions.values() if v > threshold]
        return len(strong) > 1

    def get_compliance_flags(self, document):
        compliance_keywords = [
            "confidential", "policy", "regulation", "compliance", "violation",
            "breach", "audit", "legal", "mandatory", "prohibited", "restricted"
        ]
        flags = []
        text = document.lower()
        for word in compliance_keywords:
            if word in text:
                flags.append(f"Compliance keyword detected: '{word}'")
        tone = self.detect_tone(document)
        if tone == "Negative":
            flags.append("Negative tone detected, review for compliance risk.")
        return flags

    def highlight_important_tone_points(self, document):
        import re
        sentences = re.split(r'(?<=[.!?])\s+', document)
        important = []
        strong_words = ["must", "immediately", "critical", "urgent", "important", "required", "ensure", "not allowed"]
        for sent in sentences:
            sent_lower = sent.lower()
            if any(word in sent_lower for word in strong_words) or "!" in sent:
                important.append(sent.strip())
        return important

    def get_tone_shift_report(self, document1, document2):
        tone1 = self.detect_tone(document1)
        tone2 = self.detect_tone(document2)
        shift = tone1 != tone2
        shift_details = self.get_tone_shift_details(document1, document2)
        compliance_flags1 = self.get_compliance_flags(document1)
        compliance_flags2 = self.get_compliance_flags(document2)
        important1 = self.highlight_important_tone_points(document1)
        important2 = self.highlight_important_tone_points(document2)
        report = [
            f"Document 1 Tone: {tone1}",
            f"Document 2 Tone: {tone2}",
            f"Tone Shift Detected: {'Yes' if shift else 'No'}",
            f"Details: {shift_details}",
            "",
            "Compliance Flags in Document 1:" if compliance_flags1 else "",
            *compliance_flags1,
            "Compliance Flags in Document 2:" if compliance_flags2 else "",
            *compliance_flags2,
            "",
            "Important Points in Document 1:" if important1 else "",
            *important1,
            "Important Points in Document 2:" if important2 else "",
            *important2
        ]
        return "\n".join([line for line in report if line.strip()])

    def get_tone_score(self, document):
        if self.nlp_service:
            try:
                analysis = self.nlp_service.analyze_text(document)
                if "emotions" in analysis:
                    return analysis["emotions"]
                if "confidence_scores" in analysis:
                    return analysis["confidence_scores"]
            except Exception:
                pass
        text = document.lower()
        return {
            "positive": sum(word in text for word in ["happy", "joy", "delighted"]),
            "negative": sum(word in text for word in ["angry", "upset", "frustrated"]),
            "neutral": 1
        }

    def compare_tone_scores(self, doc1, doc2):
        scores1 = self.get_tone_score(doc1)
        scores2 = self.get_tone_score(doc2)
        all_keys = set(scores1) | set(scores2)
        diff = {k: scores1.get(k, 0) - scores2.get(k, 0) for k in all_keys}
        return diff

    def get_tone_trend(self, documents):
        return [self.detect_tone(doc) for doc in documents]

    def get_tone_shift_indices(self, documents):
        tones = self.get_tone_trend(documents)
        shifts = []
        for i in range(1, len(tones)):
            if tones[i] != tones[i-1]:
                shifts.append(i)
        return shifts

    def summarize_tone_analysis(self, documents):
        distribution = self.get_tone_distribution(documents)
        shifts = self.get_tone_shift_indices(documents)
        return (
            f"Tone Distribution: {distribution}\n"
            f"Tone Shift Indices: {shifts}\n"
            f"Total Shifts: {len(shifts)}"
        )

    def get_tone_confidence(self, document):
        analysis = self.nlp_service.analyze_text(document)
        if "emotions" in analysis and analysis["emotions"]:
            main_emotion = max(analysis["emotions"], key=analysis["emotions"].get)
            return {main_emotion: analysis["emotions"][main_emotion]}
        if "confidence_scores" in analysis and "sentiment" in analysis:
            sentiment = analysis["sentiment"]
            return {sentiment: analysis["confidence_scores"].get(sentiment, 0.0)}
        return {}

    def get_tone_change_summary(self, documents):
        tones = self.get_tone_trend(documents)
        changes = []
        for i in range(1, len(tones)):
            if tones[i] != tones[i-1]:
                changes.append(f"Tone changed from '{tones[i-1]}' to '{tones[i]}' at document {i+1}")
        if not changes:
            return "No tone changes detected."
        return "\n".join(changes)

    def get_tone_segments(self, document, segment_size=3):
        sentences = document.split('.')
        segments = [". ".join(sentences[i:i+segment_size]).strip() for i in range(0, len(sentences), segment_size)]
        return [(i+1, self.detect_tone(seg)) for i, seg in enumerate(segments) if seg]

    def get_emphasized_sentences(self, document):
        import re
        strong_words = ["must", "immediately", "critical", "urgent", "important", "required", "ensure", "not allowed",
                        "angry", "happy", "joy", "frustrated", "delighted", "upset"]
        sentences = re.split(r'(?<=[.!?])\s+', document)
        return [sent for sent in sentences if any(word in sent.lower() for word in strong_words)]


