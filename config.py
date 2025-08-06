import logging
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


#download_logs config
ITLOGIN = os.environ["ITLOGIN"]
PASSID = os.environ["PASSID"]
numbers_raw = os.environ["PHONE_NUMBERS"]
PHONE_NUMBERS = numbers_raw.split(",")
ACCOUNT_NUMBER = os.environ["ACCOUNT_NUMBER"]
EMAIL_SENDER = os.environ["DEBUG_EMAIL_SENDER"]
EMAIL_ONE = os.environ["DEBUG_EMAIL_ONE"]
EMAIL_TWO = os.environ["DEBUG_EMAIL_TWO"]
BROWSER_PATH = os.environ["BROWSER_PATH"]
BASE_URL = os.environ["BASE_URL"]
BASE_LOGIN_URL = os.environ["BASE_LOGIN_URL"]
CHECK_LOGIN_URL = os.environ["CHECK_LOGIN_URL"]
ACC_HOLDER_NAME = os.environ["ACC_HOLDER_NAME"]

SCREENSHOTS_PATH = Path("./screenshots")
SITECACHE_PATH = Path("./sitecache.json")

#sync_logs config
src_logs = Path("./logs/xls/")
stage_logs = Path("./logs/csv/")

#db config
DB_USER = os.environ["DB_USER"]
DB_PASS = os.environ["DB_PASS"]
DB_NAME = os.environ["DB_NAME"]
DB_HOST = os.environ["DB_HOST"]


def logging_setup() -> None:
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
