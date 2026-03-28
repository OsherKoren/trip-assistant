"""Question normalization and hashing for cache key generation."""

import hashlib
import re


def normalize_question(question: str) -> str:
    """Normalize a question for cache key comparison.

    Lowercases, strips whitespace, removes punctuation (keeps ?),
    and collapses internal whitespace.

    Args:
        question: Raw user question.

    Returns:
        Normalized question string.
    """
    text = question.lower().strip()
    text = re.sub(r"[^\w\s?]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def hash_question(normalized: str) -> str:
    """Generate a SHA-256 hash of a normalized question.

    Args:
        normalized: Normalized question string.

    Returns:
        Hex digest of the SHA-256 hash.
    """
    return hashlib.sha256(normalized.encode()).hexdigest()
