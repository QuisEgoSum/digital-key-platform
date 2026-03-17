from qstd_config import ConfigManager

from config.models.root import AppConfig
from config.runtime.metadata import project_metadata, root_dir

manager = ConfigManager(
    AppConfig,
    config_paths=["./config/default.yaml"],
    root_config_path=root_dir,
    default_config_values={
        "project": project_metadata["project"],
        "root_dir": root_dir,
    },
)

_config: AppConfig = manager.load_config_model()


def get_config() -> AppConfig:
    return _config
