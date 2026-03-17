import os
import time

from bootstrap.logging import setup_logging
from bootstrap.tracing import setup_tracer
from config.runtime.loader import get_config, manager
from shared.enums.project import ProjectServiceType
from shared.runtime.process import set_linux_proc_name
from shared.utils.logger import get_logger

logger = get_logger(__name__)

os.environ["TZ"] = "UTC"

time.tzset()

_config = get_config()

set_linux_proc_name("dkp")
setup_tracer()
setup_logging(_config.logger)


def main() -> None:
    logger.info("Start application service", service=_config.project.service)
    logger.info(
        "Use config files",
        config_paths=[config_path.as_posix() for config_path in manager.config_paths],
    )

    if manager.used_env_list:
        logger.info(
            "Use config environment variables",
            used_env=[env.name for env in manager.used_env_list],
        )

    match _config.project.service:
        case ProjectServiceType.USER_HTTP:
            from entrypoint.user_http.main import main
        case _:
            raise NotImplementedError(f"{_config.project.service} is not supported")

    main()


if __name__ == "__main__":
    main()
