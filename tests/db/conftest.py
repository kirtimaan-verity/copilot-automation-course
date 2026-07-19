"""
Shared pytest fixtures for database tests.

Referenced in Module 4 Lab 17. Demonstrates the two critical patterns
the slides describe:
  1. The rollback fixture (test isolation at the DB level)
  2. PRAGMA foreign_keys = ON (SQLite does NOT enforce FKs by default)

Run: source ../../.venv/bin/activate
     TEST_DB_URL=sqlite:///./db/app.db pytest tests/db/ -v
"""
import os
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session


@pytest.fixture(scope="session")
def db_engine():
    """One SQLAlchemy engine for the whole test session."""
    url = os.environ.get("TEST_DB_URL", "sqlite:///./db/app.db")
    engine = create_engine(url)
    yield engine
    engine.dispose()


@pytest.fixture
def db_session(db_engine):
    """
    Each test gets a fresh transaction that is rolled back afterwards.

    Critical details:
      - PRAGMA foreign_keys = ON enables FK enforcement (off by default
        in SQLite). Without it, FK constraint tests pass incorrectly.
      - The transaction.rollback() at the end undoes everything the test
        did, keeping tests isolated. Runs even on exception.
    """
    connection = db_engine.connect()
    # Enable FK enforcement for THIS connection.
    # In SQLAlchemy 2.0, execute() autobegins a transaction; PRAGMA itself
    # is NOT transactional, so we end the autobegun transaction with
    # rollback() (the pragma stays in effect on the connection) and then
    # start our explicit test transaction.
    connection.execute(text("PRAGMA foreign_keys = ON"))
    connection.rollback()
    transaction = connection.begin()
    session = Session(bind=connection)

    yield session  # ---- test runs here ----

    session.close()
    transaction.rollback()
    connection.close()
