"""Tests for the converter module."""

import pytest

from yburn.converter import convert


def test_convert_not_implemented():
    """Converter is not yet implemented."""
    with pytest.raises(NotImplementedError):
        convert(None, "/tmp")
