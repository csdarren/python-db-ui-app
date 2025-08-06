import logging

import config
from src.psql_data import format_logs, sync_logs

config.logging_setup()
logger = logging.getLogger(__name__)


def main() -> None:
    try:
        dtos = format_logs(src_logs=config.src_logs.iterdir(), stage_logs=config.stage_logs)
        sync_logs(dtos)

    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt caught, exiting program")
        return


if __name__ == "__main__":
    main()
