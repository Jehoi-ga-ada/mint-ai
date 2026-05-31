"""Ensure every ORM model is registered before any test touches the mappers.

SQLAlchemy configures all mappers the first time one is used; relationships use
string references, so every related model must be imported or resolution fails.
The running app imports them transitively via the router — tests import them here.
"""

import src.infra.models.account  # noqa: F401
import src.infra.models.asset  # noqa: F401
import src.infra.models.category  # noqa: F401
import src.infra.models.fx_rate  # noqa: F401
import src.infra.models.investment_transaction  # noqa: F401
import src.infra.models.networth_snapshot  # noqa: F401
import src.infra.models.portfolio  # noqa: F401
import src.infra.models.portfolio_snapshot  # noqa: F401
import src.infra.models.price_snapshot  # noqa: F401
import src.infra.models.transaction  # noqa: F401
import src.infra.models.user  # noqa: F401
