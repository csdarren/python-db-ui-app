import logging
import sys
from os import environ
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
from src.db import create_service
from src.db.types import CallReportRep

numbers_raw = environ["PHONE_NUMBERS_FORMATTED"]
rep_strs = numbers_raw.split(",")
rep_nums = [int(s) for s in rep_strs]

logger = logging.getLogger(__name__)

def generate_rep_identity_sql() -> None:
    sql_str = """
    CREATE TABLE IF NOT EXISTS public.rep_identity
    (
        rep_id SERIAL PRIMARY KEY,
        rep_num BIGINT UNIQUE NOT NULL,
        rep_name TEXT
    );
    """
    sql_path = Path("rep_identity.sql")
    sql_path.write_text(sql_str)

def generate_call_log_sql() -> None:
    sql_str = """
    CREATE TABLE IF NOT EXISTS public.call_log
    (
        log_id SERIAL PRIMARY KEY,
        rep_num BIGINT REFERENCES public.rep_identity(rep_num),
        date DATE NOT NULL,
        time TIME WITHOUT TIME ZONE NOT NULL,
        customer_num BIGINT NOT NULL,
        mins_on_phone SMALLINT NOT NULL,
        caller_location TEXT NOT NULL
    );
    """
    sql_path = Path("call_log.sql")
    sql_path.write_text(sql_str)

def generate_all_sql() -> None:
    generate_rep_identity_sql()
    generate_call_log_sql()

def build_db() -> None:
    generate_all_sql()
    # TODO: find a way to run the psql command to actual create the tables on the server

    with create_service() as dbs:
        for num in rep_nums:
            dto = CallReportRep(rep_num=num, rep_name=None)
            dbs.insert_rep_phone(dto)

if __name__ == "__main__":
    build_db()
