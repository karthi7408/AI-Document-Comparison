class SemanticAnalyzer:
    def __init__(self, nlp_service=None, multilingual_service=None, azure_ai_service=None):
        self.nlp_service = nlp_service
        self.multilingual_service = multilingual_service
        self.azure_ai_service = azure_ai_service

    def health_check(self):
        return True

    def translate_document(self, document, target_language='en'):
        """
        Translate the document to the target language using multilingual service if available.
        """
        if self.multilingual_service:
            return self.multilingual_service.translate(document, target_language)
        return document

    def analyze_semantics(self, document1, document2, lang1='en', lang2='en'):
        """
        Analyze the semantics of two documents and highlight differences.
        Optionally translate documents to English before analysis.
        """
        doc1 = self.translate_document(document1, target_language=lang1)
        doc2 = self.translate_document(document2, target_language=lang2)

        analysis1 = self.nlp_service.analyze_text(doc1)
        analysis2 = self.nlp_service.analyze_text(doc2)
        key_phrases1 = set(analysis1.get("key_phrases", []))
        key_phrases2 = set(analysis2.get("key_phrases", []))
        intersection = key_phrases1 & key_phrases2
        union = key_phrases1 | key_phrases2
        similarity = len(intersection) / len(union) if union else 1.0
        semantic_diff = {
            "unique_to_doc1": list(key_phrases1 - key_phrases2),
            "unique_to_doc2": list(key_phrases2 - key_phrases1)
        }
        return {
            "similarity_score": round(similarity, 3),
            "semantic_difference": semantic_diff,
            "local_analysis_doc1": analysis1,
            "local_analysis_doc2": analysis2
        }

    def extract_entities(self, document, lang='en'):
        """
        Extract entities from a document using the local NLP service.
        Translates document if multilingual_service is available.
        """
        doc = self.translate_document(document, target_language=lang)

        analysis = self.nlp_service.analyze_text(doc)
        entities = analysis.get("entities", [])
        categorized = {}
        for ent in entities:
            text = ent.get("text") if isinstance(ent, dict) else ent
            category = ent.get("category", "Unknown") if isinstance(ent, dict) else "Unknown"
            categorized.setdefault(category, set()).add(text)
        return categorized

    def compare_entities(self, document1, document2, lang1='en', lang2='en'):
        """
        Compare categorized entities between two documents.
        Translates documents if multilingual_service is available.
        """
        entities1 = self.extract_entities(document1, lang=lang1)
        entities2 = self.extract_entities(document2, lang=lang2)
        all_types = set(entities1.keys()) | set(entities2.keys())
        comparison = {}
        for etype in all_types:
            set1 = entities1.get(etype, set())
            set2 = entities2.get(etype, set())
            comparison[etype] = {
                "unique_to_doc1": list(set1 - set2),
                "unique_to_doc2": list(set2 - set1),
                "common": list(set1 & set2)
            }
        return comparison

    def get_semantic_similarity_matrix(self, documents):
        """
        Returns a matrix of pairwise semantic similarity scores for a list of documents.
        """
        n = len(documents)
        matrix = [[0.0 for _ in range(n)] for _ in range(n)]
        for i in range(n):
            for j in range(i, n):
                sim = self.analyze_semantics(documents[i], documents[j])['similarity_score']
                matrix[i][j] = sim
                matrix[j][i] = sim
        return matrix

    def get_most_similar_document_pair(self, documents):
        """
        Finds the pair of documents with the highest semantic similarity.
        Returns:
        dict: {'pair': (i, j), 'similarity': float}
        """
        n = len(documents)
        max_sim = -1
        pair = (None, None)
        for i in range(n):
            for j in range(i + 1, n):
                sim = self.analyze_semantics(documents[i], documents[j])['similarity_score']
                if sim > max_sim:
                    max_sim = sim
                    pair = (i, j)
        return {'pair': pair, 'similarity': max_sim}

    def get_most_dissimilar_document_pair(self, documents):
        """
        Finds the pair of documents with the lowest semantic similarity.
        Returns:
        dict: {'pair': (i, j), 'similarity': float}
        """
        n = len(documents)
        min_sim = float('inf')
        pair = (None, None)
        for i in range(n):
            for j in range(i + 1, n):
                sim = self.analyze_semantics(documents[i], documents[j])['similarity_score']
                if sim < min_sim:
                    min_sim = sim
                    pair = (i, j)
        return {'pair': pair, 'similarity': min_sim}

    def get_semantic_alerts(self, documents, threshold=0.3):
        """
        Returns a list of document pairs with low semantic similarity (possible misalignment).
        """
        n = len(documents)
        alerts = []
        for i in range(n):
            for j in range(i + 1, n):
                sim = self.analyze_semantics(documents[i], documents[j])['similarity_score']
                if sim < threshold:
                    alerts.append({'pair': (i, j), 'similarity': sim, 'alert': 'Low semantic similarity'})
        return alerts

    def get_common_and_unique_phrases(self, documents):
        """
        Returns phrases common to all documents and unique to each.
        """
        if not documents:
            return {'common': [], 'unique': []}
        phrase_sets = []
        for doc in documents:
            if self.nlp_service:
                analysis = self.nlp_service.analyze_text(doc)
                phrases = set(analysis.get("key_phrases", []))
            else:
                phrases = set(doc.lower().split())
            phrase_sets.append(phrases)
        common = set.intersection(*phrase_sets)
        unique = [list(phrases - common) for phrases in phrase_sets]
        return {'common': list(common), 'unique': unique}

    def get_semantic_summary_report(self, document1, document2):
        """
        Generate a detailed semantic comparison report as a string.
        """
        analysis = self.analyze_semantics(document1, document2)
        overlap = analysis['similarity_score']
        diff = analysis['semantic_difference']
        print(diff)
        entities = self.compare_entities(document1, document2)
        report = [
            f"Semantic Similarity Score: {overlap}",
            f"Unique to Document 1: {', '.join(diff['unique_to_doc1']) if diff['unique_to_doc1'] else 'None'}",
            f"Unique to Document 2: {', '.join(diff['unique_to_doc2']) if diff['unique_to_doc2'] else 'None'}",
            "Entity Comparison:"
        ]
        for etype, vals in entities.items():
            report.append(
                f"{etype} - Unique to Doc1: {', '.join(vals['unique_to_doc1']) if vals['unique_to_doc1'] else 'None'} | "
                f"Unique to Doc2: {', '.join(vals['unique_to_doc2']) if vals['unique_to_doc2'] else 'None'} | "
                f"Common: {', '.join(vals['common']) if vals['common'] else 'None'}"
            )
        return "\n".join(report)

    def get_document_topics(self, document):
        """
        Extracts main topics or themes from a document using the local NLP service.
        Returns:
        list: List of topics/themes.
        """
        if self.nlp_service:
            analysis = self.nlp_service.analyze_text(document)
            return analysis.get("topics", []) or analysis.get("key_phrases", [])
        else:
            # Fallback: most common words as topics
            from collections import Counter
            words = [w for w in document.lower().split() if len(w) > 3]
            return [w for w, _ in Counter(words).most_common(5)]

    def get_semantic_overlap_report(self, documents):
        """
        Returns a report of semantic overlap (commonality) between all documents.
        """
        if not documents:
            return "No documents provided."
        overlap_matrix = self.get_semantic_similarity_matrix(documents)
        report_lines = []
        n = len(documents)
        for i in range(n):
            for j in range(i + 1, n):
                report_lines.append(
                    f"Doc {i+1} vs Doc {j+1}: Similarity = {overlap_matrix[i][j]}"
                )
        return "\n".join(report_lines)

    def get_unique_keywords_across_documents(self, documents):
        """
        Returns a set of keywords that are unique to each document (not present in others).
        """
        all_keywords = []
        for doc in documents:
            if self.nlp_service:
                analysis = self.nlp_service.analyze_text(doc)
                keywords = set(analysis.get("key_phrases", []))
            else:
                keywords = set(doc.lower().split())
            all_keywords.append(keywords)
        unique_keywords = []
        for i, kws in enumerate(all_keywords):
            others = set().union(*(all_keywords[:i] + all_keywords[i+1:]))
            unique_keywords.append(list(kws - others))
        return unique_keywords

    def get_semantic_change_points(self, documents, threshold=0.3):
        """
        Returns indices where semantic similarity drops below a threshold between consecutive documents.
        """
        change_points = []
        for i in range(1, len(documents)):
            sim = self.analyze_semantics(documents[i-1], documents[i])['similarity_score']
            if sim < threshold:
                change_points.append(i)
        return change_points

    def get_document_similarity_ranking(self, documents, reference_index=0):
        """
        Returns a ranking of all documents by semantic similarity to a reference document.
        Parameters:
        documents (list): List of document texts.
        reference_index (int): Index of the reference document.
        Returns:
        list of tuples: (doc_index, similarity_score), sorted descending.
        """
        reference_doc = documents[reference_index]
        scores = []
        for i, doc in enumerate(documents):
            if i == reference_index:
                continue
            sim = self.analyze_semantics(reference_doc, doc)['similarity_score']
            scores.append((i, sim))
        return sorted(scores, key=lambda x: x[1], reverse=True)

    def get_documents_with_no_overlap(self, documents):
        """
        Returns indices of document pairs with zero semantic overlap (no shared key phrases/tokens).
        """
        n = len(documents)
        no_overlap = []
        for i in range(n):
            for j in range(i + 1, n):
                result = self.analyze_semantics(documents[i], documents[j])
                if result['similarity_score'] == 0.0:
                    no_overlap.append((i, j))
        return no_overlap

    def get_semantic_keyword_frequency(self, documents):
        """
        Returns a frequency count of all key phrases (Azure) or tokens across all documents.
        """
        from collections import Counter
        freq = Counter()
        for doc in documents:
            if self.nlp_service:
                analysis = self.nlp_service.analyze_text(doc)
                phrases = analysis.get("key_phrases", [])
            else:
                phrases = doc.lower().split()
            freq.update(phrases)
        return dict(freq)

    def get_semantic_gap_report(self, doc1, doc2):
        """
        Returns a report of the main semantic gaps between two documents.
        """
        result = self.analyze_semantics(doc1, doc2)
        unique1 = result['semantic_difference'].get('unique_to_doc1', [])
        unique2 = result['semantic_difference'].get('unique_to_doc2', [])
        lines = []
        if unique1:
            lines.append(f"Terms unique to Document 1: {', '.join(unique1)}")
        if unique2:
            lines.append(f"Terms unique to Document 2: {', '.join(unique2)}")
        if not lines:
            return "No significant semantic gaps found."
        return "\n".join(lines)

    def get_semantic_diversity_score(self, documents):
        """
        Returns a diversity score (0.0 to 1.0) indicating how semantically diverse the set of documents is.
        Higher is more diverse.
        """
        if not documents or len(documents) < 2:
            return 0.0
        sims = []
        n = len(documents)
        for i in range(n):
            for j in range(i + 1, n):
                sim = self.analyze_semantics(documents[i], documents[j])['similarity_score']
                sims.append(sim)
        if not sims:
            return 0.0
        avg_sim = sum(sims) / len(sims)
        return round(1.0 - avg_sim, 3)

    def get_semantic_outliers(self, documents, threshold=0.4):
        """
        Returns indices of documents that are semantic outliers (low average similarity to others).
        """
        n = len(documents)
        outliers = []
        for i in range(n):
            sims = []
            for j in range(n):
                if i != j:
                    sim = self.analyze_semantics(documents[i], documents[j])['similarity_score']
                    sims.append(sim)
            avg_sim = sum(sims) / len(sims) if sims else 1.0
            if avg_sim < threshold:
                outliers.append(i)
        return outliers

    def detect_pii(self, document, language='en'):
        """
        Detect PII in a document using Azure AI Service (GPT-4) if available.
        Returns list of detected PII entities.
        """
        if self.azure_ai_service:
            return self.azure_ai_service.detect_pii(document, language=language)
        return []

    def analyze_healthcare_entities(self, document, language='en'):
        """
        Analyze healthcare entities using Azure AI Service if available.
        Returns list of detected healthcare entities.
        """
        if self.azure_ai_service:
            return self.azure_ai_service.analyze_healthcare_entities(document, language=language)
        return []

    def analyze_conversation(self, conversation, language='en'):
        """
        Analyze a conversation (list of utterances) using Azure AI Service if available.
        Returns analysis results.
        """
        if self.azure_ai_service:
            return self.azure_ai_service.analyze_conversation(conversation, language=language)
        return {}