# TODO: Add error log report for records that were skipped or not added to the database.  # noqa: FIX002
from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import TYPE_CHECKING

import psycopg
from psycopg.connection import Connection
from psycopg_pool import ConnectionPool

if TYPE_CHECKING:
    from collections.abc import Generator

    from .types import CallReportLog, CallReportRep

import config

from . import queries

logger = logging.getLogger(__name__)

@contextmanager
def create_service() -> Generator[DbService]:
    with ConnectionPool(
        kwargs= {
            "user": config.DB_USER,
            "password": config.DB_PASS,
            "host": config.DB_HOST,
            "dbname": config.DB_NAME,
        },
        connection_class=Connection,
        min_size=1,
        max_size=5,
        timeout=5.0,
    ) as pool:
        yield DbService(pool)


class DbService:
    def __init__(self, pool: ConnectionPool):
        self._pool = pool

    # define database querys here:
    def insert_rep_phone(self, dto: CallReportRep) -> None:
        with self._pool.connection() as conn, conn.transaction():
            try:
                conn.execute(
                    queries.INSERT_REP_PHONES,
                    (
                        dto.rep_num, dto.rep_name
                    ),
                )
                logger.info("Successful SQL Execution")
            except psycopg.Error:
                logger.exception("Failed SQL Execution")

    def insert_call_data(self, dto: CallReportLog) -> None:
        with self._pool.connection() as conn, conn.transaction():
            try:
                conn.execute(
                    queries.INSERT_CALL_DATA,
                    (
                        dto.rep_num,
                        dto.date,
                        dto.time,
                        dto.customer_num,
                        dto.mins_on_phone,
                        dto.caller_location,
                    ),
                )
            except psycopg.Error:
                logger.exception("Failed SQL Execution")
