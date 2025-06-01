class Document:
    def __init__(self, title: str, content: str, language: str = "en", metadata: dict = None):
        self.title = title
        self.content = content
        self.language = language
        self.metadata = metadata or {}

    def __repr__(self):
        return f"<Document(title={self.title!r}, language={self.language!r})>"

    def get_word_count(self):
        return len(self.content.split())

    def get_summary(self, summarizer=None):
        """
        Returns a summary of the document using the provided summarizer function,
        or the first 200 characters if not available.
        """
        if summarizer:
            return summarizer(self.content)
        return self.content[:200] + "..." if len(self.content) > 200 else self.content

    def get_language(self):
        return self.language

    def get_metadata(self, key, default=None):
        return self.metadata.get(key, default)

    def set_metadata(self, key, value):
        self.metadata[key] = value

    def to_dict(self):
        return {
            "title": self.title,
            "content": self.content,
            "language": self.language,
            "metadata": self.metadata
        }

    @staticmethod
    def from_dict(data):
        return Document(
            title=data.get("title", ""),
            content=data.get("content", ""),
            language=data.get("language", "en"),
            metadata=data.get("metadata", {})
        )

    def contains_keyword(self, keyword):
        return keyword.lower() in self.content.lower()

    def get_line_count(self):
        return len(self.content.splitlines())

    def get_char_count(self):
        return len(self.content)

class AnalysisResult:
    def __init__(
        self,
        document: Document,
        semantic_analysis: dict,
        sentiment: str,
        tone_shifts: list,
        diff: dict = None,
        compliance_flags: list = None,
        pii_entities: list = None,
        ai_insights: dict = None,
        metrics: dict = None
    ):
        self.document = document
        self.semantic_analysis = semantic_analysis
        self.sentiment = sentiment
        self.tone_shifts = tone_shifts
        self.diff = diff or {}
        self.compliance_flags = compliance_flags or []
        self.pii_entities = pii_entities or []
        self.ai_insights = ai_insights or {}
        self.metrics = metrics or {}

    def __repr__(self):
        return f"<AnalysisResult(document={self.document.title!r}, sentiment={self.sentiment!r})>"

    def summary(self):
        """
        Returns a summary dictionary for the analysis result.
        """
        return {
            "title": self.document.title,
            "sentiment": self.sentiment,
            "main_topics": self.semantic_analysis.get("topics") if self.semantic_analysis else [],
            "compliance_flags": self.compliance_flags,
            "pii_entities": self.pii_entities,
            "metrics": self.metrics
        }

    def add_metric(self, key, value):
        self.metrics[key] = value

    def add_ai_insight(self, key, value):
        self.ai_insights[key] = value

    def add_compliance_flag(self, flag):
        self.compliance_flags.append(flag)

    def add_pii_entity(self, entity):
        self.pii_entities.append(entity)

    def to_dict(self):
        return {
            "document": self.document.to_dict(),
            "semantic_analysis": self.semantic_analysis,
            "sentiment": self.sentiment,
            "tone_shifts": self.tone_shifts,
            "diff": self.diff,
            "compliance_flags": self.compliance_flags,
            "pii_entities": self.pii_entities,
            "ai_insights": self.ai_insights,
            "metrics": self.metrics
        }

    @staticmethod
    def from_dict(data):
        return AnalysisResult(
            document=Document.from_dict(data.get("document", {})),
            semantic_analysis=data.get("semantic_analysis", {}),
            sentiment=data.get("sentiment", ""),
            tone_shifts=data.get("tone_shifts", []),
            diff=data.get("diff", {}),
            compliance_flags=data.get("compliance_flags", []),
            pii_entities=data.get("pii_entities", []),
            ai_insights=data.get("ai_insights", {}),
            metrics=data.get("metrics", {})
        )

    def get_flagged(self):
        """
        Returns True if there are compliance flags or PII entities.
        """
        return bool(self.compliance_flags or self.pii_entities)

    def get_main_topics(self):
        """
        Returns main topics from semantic analysis if available.
        """
        return self.semantic_analysis.get("topics") if self.semantic_analysis else []

    def get_summary_report(self):
        """
        Returns a concise summary report for UI or export.
        """
        return {
            "title": self.document.title,
            "sentiment": self.sentiment,
            "main_topics": self.get_main_topics(),
            "flags": self.compliance_flags,
            "pii": self.pii_entities,
            "metrics": self.metrics,
            "ai_insights": self.ai_insights
        }