from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

import pandas as pd

from .db import create_service
from .db.types import CallReportLog

if TYPE_CHECKING:
    from collections.abc import Iterable

logger = logging.getLogger(__name__)

def check_file_type(file: Path) -> bool:
    """
    Loop through a dictionary of strings that identifies which file types are supported.
    In order to add new file types, you must add to the dictionary list at the top of this file.
    """
    file_supported = False
    for suffix in ".xls":
        if file.suffix == suffix:
            file_supported = True
            break


    return file_supported


def create_dtos(rep_num: int, rows: Iterable[tuple]) -> list[CallReportLog]:
    """
    Create dto objects using row data from a dataframe tuple
    """
    dtos = []
    for row in rows:
        # form dto for a log entry
        logger.info("rows: %s", row)
        dto = CallReportLog (
            rep_num=rep_num,
            date=pd.to_datetime(row[0]).date(),
            time=pd.to_datetime(row[1]).time(),
            customer_num=row[2],
            mins_on_phone=row[3],
            caller_location=row[4],
        )
        # add created dto to list
        dtos.append(dto)
    return dtos


def format_logs(src_logs: Iterable[Path], stage_logs: Path) -> list[CallReportLog] | None:
    """
    Prepares all documents regardless of type for database by converting them to csv and formatting them properly

    Loops through files and prepares them for the database by cleaning them up and removing unnecessary information

    Returns:
        dtos :class:'list[CallReportLog]'
            data transfer object, with format ready for database merge
    """

    dtos = []
    for file in src_logs:
        # define which row the data starts in the file
        header_row = 4

        if not check_file_type(file):
            logger.critical("no files exist in %s that are supported", src_logs)
            return None

        # create pandas DataFrame object of input file
        pd_excel = pd.read_excel(file, header=header_row, engine="openpyxl")


        # Remove "." from file name and change to csv
        formatted_file = Path(file.stem.replace(".", "") + ".csv")
        #
        # Loop through every row and store the row as an iterable list starting at index 0
        dtos = create_dtos(int(formatted_file.stem), pd_excel.itertuples(index=False, name=None))

        # move to stage_logs and save as csv for backup
        stage_path = stage_logs / formatted_file
        pd_excel.to_csv(stage_path, index=False)

        logger.info("Document preparation successfull")
    # If all goes well, return a list of dtos
    return dtos


def sync(dtos: list[CallReportLog] | None) -> bool:
    with create_service() as dbs:

        if not dtos:
            return False
        for dto in dtos:
            dbs.insert_call_data(dto)
        return True

