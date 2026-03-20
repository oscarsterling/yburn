"""Tests for the classification engine."""

import pytest

from yburn.classifier import classify


def test_classify_not_implemented():
    """Classifier is not yet implemented."""
    with pytest.raises(NotImplementedError):
        classify(None)
