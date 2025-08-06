import logging

import config
import psql_data

config.logging_setup()
logger = logging.getLogger(__name__)



def main() -> None:
    try:
        dtos = psql_data.format_logs(src_logs=config.src_logs.iterdir(), stage_logs=config.stage_logs)
        psql_data.sync(dtos)

    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt caught, exiting program")
        return


if __name__ == "__main__":
    main()
