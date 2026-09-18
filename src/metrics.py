"""
Text quality metrics from Saini & Sengupta (2024).
Reproduces formulas from summary_score_tool.html.

Metrics:
- Word count, sentence count, syllables
- Lexical density (unique words / total)
- Text entropy (information density)
- Readability (Flesch Reading Ease)
- Cohesion (sentence structure)
- Coherence (repetition analysis)
- Summary Score (S_SS): aggregate of normalized components
- Additional: Compression ratio, key-fact coverage, ROUGE-L
"""

import re
import math
from typing import Dict, List, Tuple


def count_words(text: str) -> int:
    """Split by whitespace and count non-empty tokens."""
    return len(text.strip().split())


def count_sentences(text: str) -> int:
    """Count sentences by .!? marks. Minimum 1."""
    count = len(re.findall(r'[.!?]+', text))
    return max(1, count)


def count_syllables(text: str) -> int:
    """
    Estimate syllables by counting vowel groups.

    Rules:
    - Each vowel group = 1 syllable
    - If ends with 'e', subtract 1
    - If ends with 'le' (consonant before), add 1
    - Min 1
    """
    vowels = 'aeiouy'
    text_lower = text.lower()
    syllable_count = 0
    previous_was_vowel = False

    for char in text_lower:
        is_vowel = char in vowels
        if is_vowel and not previous_was_vowel:
            syllable_count += 1
        previous_was_vowel = is_vowel

    if text_lower.endswith('e'):
        syllable_count -= 1

    if text_lower.endswith('le') and len(text) > 2:
        if text_lower[-3] not in vowels:
            syllable_count += 1

    return max(1, syllable_count)


def calculate_entropy(text: str) -> float:
    """
    Shannon entropy over character frequencies.
    E = -Σ(p_i × log₂(p_i))
    Only count a-z and space; case-insensitive.
    Range: 0–8 bits/char.
    """
    text_lower = text.lower()
    freq = {}

    for char in text_lower:
        if char.isalpha() or char == ' ':
            freq[char] = freq.get(char, 0) + 1

    total = sum(freq.values())
    if total == 0:
        return 0.0

    entropy = 0.0
    for count in freq.values():
        p = count / total
        if p > 0:
            entropy -= p * math.log2(p)

    return entropy


def calculate_readability(word_count: int, sentence_count: int, syllable_count: int) -> float:
    """
    Flesch Reading Ease formula.
    R = 206.835 - 1.015(W/S) - 84.6(Sy/W)
    Clamped to 0–100.
    """
    if word_count == 0 or sentence_count == 0:
        return 0.0

    score = 206.835 - 1.015 * (word_count / sentence_count) - 84.6 * (syllable_count / word_count)
    return max(0, min(100, score))


def calculate_cohesion(word_count: int, sentence_count: int, avg_words_per_sentence: float) -> float:
    """
    Cohesion based on sentence structure and average length.
    C = S × [(S-1)/2] × (L_avg)²
    Normalized to 0–100 by dividing by (words * 2).
    """
    if word_count == 0 or sentence_count <= 1:
        return 50.0  # Default for single sentence

    t_units = sentence_count
    cohesion = t_units * ((t_units - 1) / 2) * (avg_words_per_sentence ** 2)
    normalized = max(0, min(100, (cohesion / (word_count * 2))))
    return normalized


def calculate_coherence(words: List[str]) -> float:
    """
    Coherence based on content word repetition.
    Ch = (unique_content / total_content) × 100

    Stop words (common function words) are filtered out;
    content words are those > 2 chars and not in stop list.
    """
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of',
        'is', 'was', 'are', 'be', 'been', 'being', 'have', 'has', 'had',
        'do', 'does', 'did', 'will', 'would', 'should', 'could', 'may', 'might', 'must', 'can'
    }

    content_words = [w.lower() for w in words if w.lower() not in stop_words and len(w) > 2]
    if not content_words:
        return 50.0  # Default if no content words

    unique_content = len(set(content_words))
    repetition_ratio = unique_content / len(content_words)
    return max(0, min(100, repetition_ratio * 100))


def calculate_summary_score(entropy: float, readability: float, cohesion: float, coherence: float) -> float:
    """
    Aggregate summary score: S_SS = [E_norm + R_norm + C_norm + Ch_norm] / 4 × 100

    Each component is normalized:
    - E_norm = min(entropy / 8, 1)
    - R_norm = min(readability / 100, 1)
    - C_norm = min(cohesion / 100, 1)
    - Ch_norm = min(coherence / 100, 1)
    """
    norm_entropy = min(entropy / 8, 1)
    norm_readability = min(readability / 100, 1)
    norm_cohesion = min(cohesion / 100, 1)
    norm_coherence = min(coherence / 100, 1)

    summary_score = ((norm_entropy + norm_readability + norm_cohesion + norm_coherence) / 4) * 100
    return summary_score


def calculate_all_metrics(text: str) -> Dict[str, float]:
    """
    Calculate all metrics for a given text.
    Returns dict with keys: wordCount, sentenceCount, avgWordsPerSentence,
    syllableCount, uniqueWords, lexicalDensity, entropy, readability,
    cohesion, coherence, summaryScore
    """
    words = text.strip().split()
    word_count = len(words)
    sentence_count = count_sentences(text)
    syllable_count = count_syllables(text)
    unique_words = len(set(w.lower() for w in words if w))

    if word_count == 0 or sentence_count == 0:
        raise ValueError("Text too short or invalid")

    avg_words_per_sentence = word_count / sentence_count
    lexical_density = (unique_words / word_count) * 100

    entropy = calculate_entropy(text)
    readability = calculate_readability(word_count, sentence_count, syllable_count)
    cohesion = calculate_cohesion(word_count, sentence_count, avg_words_per_sentence)
    coherence = calculate_coherence(words)
    summary_score = calculate_summary_score(entropy, readability, cohesion, coherence)

    return {
        'wordCount': word_count,
        'sentenceCount': sentence_count,
        'avgWordsPerSentence': round(avg_words_per_sentence, 3),
        'syllableCount': syllable_count,
        'uniqueWords': unique_words,
        'lexicalDensity': round(lexical_density, 2),
        'entropy': round(entropy, 4),
        'readability': round(readability, 2),
        'cohesion': round(cohesion, 2),
        'coherence': round(coherence, 2),
        'summaryScore': round(summary_score, 2),
    }


def compression_ratio(source_text: str, summary_text: str) -> float:
    """Compression ratio = summary_words / source_words."""
    source_words = len(source_text.strip().split())
    summary_words = len(summary_text.strip().split())
    if source_words == 0:
        return 0.0
    return round(summary_words / source_words, 3)


def check_length_compliance(summary_text: str, min_sentences: int = 3, max_sentences: int = 5) -> bool:
    """Check if summary has the required number of sentences."""
    num_sentences = count_sentences(summary_text)
    return min_sentences <= num_sentences <= max_sentences


def rouge_l_f1(reference: str, summary: str) -> float:
    """
    Simplified ROUGE-L F1 score (Longest Common Subsequence).
    F1 = 2 * (precision * recall) / (precision + recall)

    Uses word-level LCS.
    """
    ref_words = reference.lower().split()
    sum_words = summary.lower().split()

    if not ref_words or not sum_words:
        return 0.0

    lcs_len = _lcs_length(ref_words, sum_words)

    precision = lcs_len / len(sum_words) if sum_words else 0
    recall = lcs_len / len(ref_words) if ref_words else 0

    if precision + recall == 0:
        return 0.0

    f1 = 2 * (precision * recall) / (precision + recall)
    return round(f1, 4)


def _lcs_length(seq1: List[str], seq2: List[str]) -> int:
    """Compute length of longest common subsequence (dynamic programming)."""
    m, n = len(seq1), len(seq2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if seq1[i - 1] == seq2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

    return dp[m][n]


def check_facts_coverage(summary_text: str, facts: List[Dict]) -> float:
    """
    Check what fraction of key facts are covered in the summary.

    Args:
        summary_text: Generated summary
        facts: List of dicts with 'keywords' and 'regex' fields

    Returns:
        Coverage fraction (0.0 to 1.0)
    """
    summary_lower = summary_text.lower()
    found = 0

    for fact in facts:
        # Try keyword match (case-insensitive)
        if 'keywords' in fact:
            for keyword in fact['keywords']:
                if keyword.lower() in summary_lower:
                    found += 1
                    break
        # Try regex match
        elif 'regex' in fact:
            if re.search(fact['regex'], summary_text, re.IGNORECASE):
                found += 1

    if not facts:
        return 0.0

    return round(found / len(facts), 3)
