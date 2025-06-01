class DiffView:
    def __init__(self, multilingual_service=None, azure_ai_service=None):
        self.multilingual_service = multilingual_service
        self.azure_ai_service = azure_ai_service

    def translate_document(self, document, target_language='en'):
        if self.multilingual_service:
            return self.multilingual_service.translate(document, target_language)
        return document

    def generate_diff_view(self, doc1, doc2, lang1='en', lang2='en'):
        doc1 = self.translate_document(doc1, lang1)
        doc2 = self.translate_document(doc2, lang2)
        """
        Generate a user-friendly view of the differences between two documents.
        
        Parameters:
        doc1 (str): The first document text.
        doc2 (str): The second document text.
        
        Returns:
        str: A formatted string showing the differences.
        """
        from difflib import unified_diff

        diff = unified_diff(
            doc1.splitlines(keepends=True),
            doc2.splitlines(keepends=True),
            fromfile='Document 1',
            tofile='Document 2',
            lineterm=''
        )

        return ''.join(diff)

    def generate_side_by_side_html(self, doc1, doc2, lang1='en', lang2='en'):
        doc1 = self.translate_document(doc1, lang1)
        doc2 = self.translate_document(doc2, lang2)
        """
        Generate a side-by-side HTML diff view of the differences between two documents.

        Parameters:
        doc1 (str): The first document text.
        doc2 (str): The second document text.

        Returns:
        str: An HTML string showing the differences side by side.
        """
        from difflib import HtmlDiff

        html_diff = HtmlDiff(tabsize=4, wrapcolumn=80)
        html = html_diff.make_file(
            doc1.splitlines(),
            doc2.splitlines(),
            fromdesc='Document 1',
            todesc='Document 2',
            context=True,
            numlines=3
        )
        return html

    def generate_inline_diff(self, doc1, doc2, lang1='en', lang2='en'):
        doc1 = self.translate_document(doc1, lang1)
        doc2 = self.translate_document(doc2, lang2)
        """
        Generate an inline diff view of the differences between two documents.

        Parameters:
        doc1 (str): The first document text.
        doc2 (str): The second document text.

        Returns:
        str: An HTML string showing the inline differences.
        """
        from difflib import HtmlDiff

        html_diff = HtmlDiff(tabsize=4, wrapcolumn=80)
        html = html_diff.make_table(
            doc1.splitlines(),
            doc2.splitlines(),
            fromdesc='Document 1',
            todesc='Document 2',
            context=False,
            numlines=0
        )
        return html

    def generate_diff_summary(self, doc1, doc2):
        """
        Summarize the number of lines added, removed, and changed between two documents.

        Returns:
        dict: {'added': int, 'removed': int, 'changed': int}
        """
        from difflib import Differ
        differ = Differ()
        diff = list(differ.compare(doc1.splitlines(), doc2.splitlines()))
        added = sum(1 for line in diff if line.startswith('+ '))
        removed = sum(1 for line in diff if line.startswith('- '))
        changed = sum(1 for line in diff if line.startswith('? '))
        return {'added': added, 'removed': removed, 'changed': changed}

    def get_changed_lines(self, doc1, doc2):
        """
        Get the line numbers and content of changed lines between two documents.

        Returns:
        list of tuples: (line_number, change_type, content)
        change_type: 'added', 'removed', or 'changed'
        """
        from difflib import ndiff
        diff = list(ndiff(doc1.splitlines(), doc2.splitlines()))
        changes = []
        line_num1 = line_num2 = 0
        for line in diff:
            if line.startswith('  '):
                line_num1 += 1
                line_num2 += 1
            elif line.startswith('- '):
                changes.append((line_num1 + 1, 'removed', line[2:]))
                line_num1 += 1
            elif line.startswith('+ '):
                changes.append((line_num2 + 1, 'added', line[2:]))
                line_num2 += 1
            elif line.startswith('? '):
                # This line indicates a change detail, can be skipped or marked as 'changed'
                pass
        return changes

    def get_diff_stats(self, doc1, doc2):
        """
        Get statistics about the diff: total, unchanged, added, and removed lines.

        Returns:
        dict: {'total_doc1': int, 'total_doc2': int, 'unchanged': int, 'added': int, 'removed': int}
        """
        from difflib import ndiff
        diff = list(ndiff(doc1.splitlines(), doc2.splitlines()))
        unchanged = sum(1 for line in diff if line.startswith('  '))
        added = sum(1 for line in diff if line.startswith('+ '))
        removed = sum(1 for line in diff if line.startswith('- '))
        return {
            'total_doc1': len(doc1.splitlines()),
            'total_doc2': len(doc2.splitlines()),
            'unchanged': unchanged,
            'added': added,
            'removed': removed
        }

    def get_similarity_score(self, doc1, doc2):
        """
        Return a similarity score (0.0 to 1.0) between the two documents.
        """
        from difflib import SequenceMatcher
        return SequenceMatcher(None, doc1, doc2).ratio()

    def highlight_word_level_diff(self, doc1, doc2):
        """
        Return a list of tuples showing word-level changes for each changed line.
        Each tuple: (line_num, changes), where changes is a list of (type, word).
        """
        from difflib import ndiff
        lines1 = doc1.splitlines()
        lines2 = doc2.splitlines()
        max_lines = max(len(lines1), len(lines2))
        results = []
        for i in range(max_lines):
            l1 = lines1[i] if i < len(lines1) else ""
            l2 = lines2[i] if i < len(lines2) else ""
            if l1 != l2:
                word_diff = list(ndiff(l1.split(), l2.split()))
                changes = []
                for w in word_diff:
                    if w.startswith('  '):
                        changes.append(('unchanged', w[2:]))
                    elif w.startswith('- '):
                        changes.append(('removed', w[2:]))
                    elif w.startswith('+ '):
                        changes.append(('added', w[2:]))
                results.append((i + 1, changes))
        return results

    def summarize_diff_changes(self, doc1, doc2):
        """
        Return a summary string describing the main types of changes.
        """
        summary = self.generate_diff_summary(doc1, doc2)
        parts = []
        if summary['added']:
            parts.append(f"{summary['added']} lines added")
        if summary['removed']:
            parts.append(f"{summary['removed']} lines removed")
        if summary['changed']:
            parts.append(f"{summary['changed']} lines changed")
        if not parts:
            return "No changes detected."
        return ", ".join(parts)

    def get_diff_as_dict(self, doc1, doc2):
        """
        Return the diff as a dictionary: {'added': [...], 'removed': [...], 'unchanged': [...]}
        """
        from difflib import ndiff
        diff = list(ndiff(doc1.splitlines(), doc2.splitlines()))
        result = {'added': [], 'removed': [], 'unchanged': []}
        for line in diff:
            if line.startswith('  '):
                result['unchanged'].append(line[2:])
            elif line.startswith('- '):
                result['removed'].append(line[2:])
            elif line.startswith('+ '):
                result['added'].append(line[2:])
        return result

    def get_diff_percentage(self, doc1, doc2):
        """
        Return the percentage of changed lines between two documents.
        """
        from difflib import ndiff
        lines1 = doc1.splitlines()
        lines2 = doc2.splitlines()
        diff = list(ndiff(lines1, lines2))
        total = max(len(lines1), len(lines2))
        changed = sum(1 for line in diff if line.startswith('- ') or line.startswith('+ '))
        return round(100 * changed / total, 2) if total else 0.0

    def get_added_removed_lines(self, doc1, doc2):
        """
        Return lists of added and removed lines.
        """
        from difflib import ndiff
        diff = list(ndiff(doc1.splitlines(), doc2.splitlines()))
        added = [line[2:] for line in diff if line.startswith('+ ')]
        removed = [line[2:] for line in diff if line.startswith('- ')]
        return {'added': added, 'removed': removed}

    def get_contextual_diff(self, doc1, doc2, context=2):
        """
        Return a diff with a specified number of context lines around changes.
        """
        from difflib import unified_diff
        diff = unified_diff(
            doc1.splitlines(),
            doc2.splitlines(),
            fromfile='Document 1',
            tofile='Document 2',
            n=context,
            lineterm=''
        )
        return '\n'.join(diff)

    def get_line_mapping(self, doc1, doc2):
        """
        Returns a mapping of original to new line numbers for unchanged lines.
        Returns:
        list of tuples: (line_num_doc1, line_num_doc2, content)
        """
        from difflib import SequenceMatcher
        lines1 = doc1.splitlines()
        lines2 = doc2.splitlines()
        matcher = SequenceMatcher(None, lines1, lines2)
        mapping = []
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                for idx1, idx2 in zip(range(i1, i2), range(j1, j2)):
                    mapping.append((idx1 + 1, idx2 + 1, lines1[idx1]))
        return mapping

    def get_diff_summary_report(self, doc1, doc2):
        """
        Returns a human-readable summary report of the diff.
        """
        stats = self.get_diff_stats(doc1, doc2)
        percent = self.get_diff_percentage(doc1, doc2)
        summary = self.summarize_diff_changes(doc1, doc2)
        return (
            f"Document 1 lines: {stats['total_doc1']}\n"
            f"Document 2 lines: {stats['total_doc2']}\n"
            f"Unchanged lines: {stats['unchanged']}\n"
            f"Added lines: {stats['added']}\n"
            f"Removed lines: {stats['removed']}\n"
            f"Changed lines: {stats.get('changed', 0)}\n"
            f"Change Percentage: {percent}%\n"
            f"Summary: {summary}"
        )

    def get_word_diff_stats(self, doc1, doc2):
        """
        Returns statistics about word-level changes (added/removed words).
        Returns:
        dict: {'added': int, 'removed': int, 'common': int}
        """
        from difflib import ndiff
        words1 = doc1.split()
        words2 = doc2.split()
        diff = list(ndiff(words1, words2))
        added = sum(1 for w in diff if w.startswith('+ '))
        removed = sum(1 for w in diff if w.startswith('- '))
        common = sum(1 for w in diff if w.startswith('  '))
        return {'added': added, 'removed': removed, 'common': common}

    def get_diff_blocks(self, doc1, doc2, context=2):
        """
        Returns blocks of changes with context for easier UI highlighting.
        Each block is a dict: {'start1': int, 'end1': int, 'start2': int, 'end2': int, 'lines1': list, 'lines2': list}
        """
        from difflib import SequenceMatcher
        lines1 = doc1.splitlines()
        lines2 = doc2.splitlines()
        matcher = SequenceMatcher(None, lines1, lines2)
        blocks = []
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag != 'equal':
                start1 = max(i1 - context, 0)
                end1 = min(i2 + context, len(lines1))
                start2 = max(j1 - context, 0)
                end2 = min(j2 + context, len(lines2))
                blocks.append({
                    'start1': start1 + 1,
                    'end1': end1,
                    'start2': start2 + 1,
                    'end2': end2,
                    'lines1': lines1[start1:end1],
                    'lines2': lines2[start2:end2],
                    'change_type': tag
                })
        return blocks

    def keyword_based_comparison(self, doc1, doc2, keywords, case_sensitive=False):
        """
        Compare two documents based on user-supplied keywords (can be multiple).
        Returns a dict with keyword presence and context in both documents.

        Parameters:
        doc1 (str): The first document text.
        doc2 (str): The second document text.
        keywords (list[str]): List of keywords to compare.
        case_sensitive (bool): Whether to match case-sensitively.

        Returns:
        dict: {
            'keyword': {
                'in_doc1': bool,
                'in_doc2': bool,
                'lines_in_doc1': [line numbers],
                'lines_in_doc2': [line numbers]
            }, ...
        }
        """
        if not case_sensitive:
            doc1_lines = [line.lower() for line in doc1.splitlines()]
            doc2_lines = [line.lower() for line in doc2.splitlines()]
            keywords = [kw.lower() for kw in keywords]
        else:
            doc1_lines = doc1.splitlines()
            doc2_lines = doc2.splitlines()

        result = {}
        for kw in keywords:
            lines1 = [i+1 for i, line in enumerate(doc1_lines) if kw in line]
            lines2 = [i+1 for i, line in enumerate(doc2_lines) if kw in line]
            result[kw] = {
                'in_doc1': bool(lines1),
                'in_doc2': bool(lines2),
                'lines_in_doc1': lines1,
                'lines_in_doc2': lines2
            }
        return result

    def get_ai_generated_diff_explanation(self, doc1, doc2, lang1='en', lang2='en'):
        """
        Use Azure AI Service (OpenAI or similar) to generate a natural language explanation of the diff.
        Returns a string explanation.
        """
        if self.azure_ai_service:
            prompt = (
                "Compare the following two documents and explain the main differences in plain language:\n\n"
                f"Document 1:\n{doc1}\n\nDocument 2:\n{doc2}\n\n"
                "Provide a concise summary of the key differences.\n"
                "Format it in a way that is easy to understand for a non-technical audience.\n"
            )
            result = self.azure_ai_service.generate_text(prompt, language=lang1)
            return result.get("generated_text", "")
        return "AI explanation not available."

    def get_ai_similarity_explanation(self, doc1, doc2, lang1='en', lang2='en'):
        """
        Use Azure AI to generate a plain-language explanation of why the documents are similar or different.
        """
        if self.azure_ai_service:
            prompt = (
                "Given the following two documents, explain in simple terms why they are similar or different. "
                "Highlight any important similarities or differences in content, tone, or structure.\n\n"
                f"Document 1:\n{doc1}\n\nDocument 2:\n{doc2}\n"
                                "Format it in a way that is easy to understand for a non-technical audience.\n"
            )
            result = self.azure_ai_service.generate_text(prompt, language=lang1)
            return result.get("generated_text", "")
        return "AI similarity explanation not available."

    def get_ai_suggested_edits(self, doc1, doc2, lang1='en', lang2='en'):
        """
        Use Azure AI to suggest edits to make doc1 more similar to doc2.
        Returns a string with suggested edits or instructions.
        """
        if self.azure_ai_service:
            prompt = (
                "Suggest specific edits or changes to Document 1 so that it matches Document 2 as closely as possible. "
                "List the edits as actionable steps.\n\n"
                f"Document 1:\n{doc1}\n\nDocument 2:\n{doc2}\n"
                                "Format it in a way that is easy to understand for a non-technical audience.\n"
            )
            result = self.azure_ai_service.generate_text(prompt, language=lang1)
            return result.get("generated_text", "")
        return "AI edit suggestions not available."

    def get_ai_structural_comparison(self, doc1, doc2, lang1='en', lang2='en'):
        """
        Use Azure AI to compare the structure (sections, headings, order) of two documents.
        Returns a string with structural comparison.
        """
        if self.azure_ai_service:
            prompt = (
                "Compare the structure of the following two documents. "
                "Describe differences in sections, headings, and order of content.\n\n"
                f"Document 1:\n{doc1}\n\nDocument 2:\n{doc2}\n"
                                "Format it in a way that is easy to understand for a non-technical audience.\n"
            )
            result = self.azure_ai_service.generate_text(prompt, language=lang1)
            return result.get("generated_text", "")
        return "AI structural comparison not available."

    def get_ai_section_alignment(self, doc1, doc2, lang1='en', lang2='en'):
        """
        Use Azure AI to align and compare sections/headings between two documents.
        Returns a mapping or explanation of section alignment.
        """
        if self.azure_ai_service:
            prompt = (
                "Analyze the following two documents and provide a mapping of corresponding sections or headings. "
                "If sections do not align, explain the differences.\n\n"
                f"Document 1:\n{doc1}\n\nDocument 2:\n{doc2}\n"
                                "Format it in a way that is easy to understand for a non-technical audience.\n"
            )
            result = self.azure_ai_service.generate_text(prompt, language=lang1)
            return result.get("generated_text", "")
        return "AI section alignment not available."

    def get_ai_highlighted_changes(self, doc1, doc2, lang1='en', lang2='en'):
        """
        Use Azure AI to highlight the most important changes between two documents.
        Returns a summary or list of highlighted changes.
        """
        if self.azure_ai_service:
            prompt = (
                "Highlight the most important changes between the following two documents. "
                "List the changes in order of significance.\n\n"
                f"Document 1:\n{doc1}\n\nDocument 2:\n{doc2}\n"
                                "Format it in a way that is easy to understand for a non-technical audience.\n"
            )
            result = self.azure_ai_service.generate_text(prompt, language=lang1)
            return result.get("generated_text", "")
        return "AI highlighted changes not available."

    def get_ai_risk_assessment_on_diff(self, doc1, doc2, lang1='en', lang2='en'):
        """
        Use Azure AI to assess if any changes between the documents introduce risk or compliance issues.
        Returns a risk assessment summary.
        """
        if self.azure_ai_service:
            prompt = (
                "Review the differences between the following two documents and assess if any changes introduce risk, "
                "compliance issues, or require urgent attention. Summarize your findings.\n\n"
                f"Document 1:\n{doc1}\n\nDocument 2:\n{doc2}\n"
                                "Format it in a way that is easy to understand for a non-technical audience.\n"
            )
            result = self.azure_ai_service.generate_text(prompt, language=lang1)
            return result.get("generated_text", "")
        return "AI risk assessment not available."