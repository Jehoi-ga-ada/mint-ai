from decimal import Decimal

from src.features.pricing.service import FxService


class FakeRateRepo:
    def __init__(self, rows=None):
        self.rows = rows or []
        self.created = []

    def list(self, **kwargs):
        return self.rows

    def create(self, entity):
        self.created.append(entity)
        return entity


class FakeFxProvider:
    def __init__(self, rates):
        self._rates = rates
        self.calls = 0

    def fetch_rates(self, base):
        self.calls += 1
        return self._rates


def _service(repo, provider, ttl=3600):
    return FxService(rate_repo=repo, provider=provider, ttl_seconds=ttl)


def test_same_currency_returns_one_without_fetching():
    provider = FakeFxProvider({})
    svc = _service(FakeRateRepo(), provider)

    assert svc.get_rate("USD", "USD") == Decimal(1)
    assert provider.calls == 0


def test_fetches_and_caches_rate_when_no_snapshot():
    provider = FakeFxProvider({"IDR": Decimal("16000")})
    repo = FakeRateRepo()
    svc = _service(repo, provider)

    assert svc.get_rate("USD", "IDR") == Decimal("16000")
    assert provider.calls == 1
    assert len(repo.created) == 1  # rate persisted as a snapshot


def test_convert_multiplies_by_rate():
    provider = FakeFxProvider({"IDR": Decimal("16000")})
    svc = _service(FakeRateRepo(), provider)

    assert svc.convert(Decimal(2), "USD", "IDR") == Decimal("32000")


def test_returns_none_when_provider_has_no_rate_and_no_cache():
    provider = FakeFxProvider({})  # provider down / unknown pair
    svc = _service(FakeRateRepo(), provider)

    assert svc.get_rate("USD", "IDR") is None
    assert svc.convert(Decimal(5), "USD", "IDR") is None
