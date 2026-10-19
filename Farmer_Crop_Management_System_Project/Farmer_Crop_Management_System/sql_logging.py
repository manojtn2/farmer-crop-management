"""Enable SQL query logging helper for local debugging and profiling.

Usage:
    from sql_logging import enable_sql_logging
    enable_sql_logging(level='INFO')

This will configure the `sqlalchemy.engine` logger to INFO and optionally set echo on the
engine when using SQLAlchemy's `create_engine`. For Flask-SQLAlchemy, setting echo in the
app config or enabling the logger is sufficient.
"""

import logging


def enable_sql_logging(level='INFO'):
    """Enable SQLAlchemy engine logging to stdout.

    level: one of 'DEBUG', 'INFO', 'WARNING', 'ERROR'
    """
    lvl = getattr(logging, level.upper(), logging.INFO)
    logger = logging.getLogger('sqlalchemy.engine')
    logger.setLevel(lvl)
    if not logger.handlers:
        ch = logging.StreamHandler()
        ch.setLevel(lvl)
        fmt = logging.Formatter('%(asctime)s %(levelname)s %(name)s - %(message)s')
        ch.setFormatter(fmt)
        logger.addHandler(ch)
    # Also enable the root logger at debug to ensure output shows up
    logging.getLogger().setLevel(min(logging.getLogger().level, lvl))
