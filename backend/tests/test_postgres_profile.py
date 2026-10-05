import pytest
from sqlalchemy import text

from app.database import engine


pytestmark = [pytest.mark.integration, pytest.mark.postgres]


def test_postgres_profile_connects_and_runs_query():
    assert engine.dialect.name == "postgresql"

    with engine.connect() as connection:
        assert connection.execute(text("SELECT 1")).scalar_one() == 1
