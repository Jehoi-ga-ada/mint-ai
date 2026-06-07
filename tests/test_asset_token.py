import pytest
from pydantic import ValidationError

from src.features.asset.schema import CreateAsset


class TestCreateAssetSchema:
    def test_uppercases_the_symbol(self):
        assert CreateAsset(symbol="sol").symbol == "SOL"

    def test_name_defaults_to_none(self):
        assert CreateAsset(symbol="SOL").name is None

    def test_rejects_non_alphanumeric_symbols(self):
        with pytest.raises(ValidationError):
            CreateAsset(symbol="SOL-USD")
        with pytest.raises(ValidationError):
            CreateAsset(symbol="")

    def test_rejects_overlong_symbols(self):
        with pytest.raises(ValidationError):
            CreateAsset(symbol="X" * 21)
