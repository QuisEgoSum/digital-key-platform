from qstd_config import ConfigManager

from config.models.root import Config
from config.runtime.metadata import project_metadata, root_dir

manager = ConfigManager(
    Config,
    config_paths=["./config/default.yaml"],
    root_config_path=root_dir,
    default_config_values={
        "project": project_metadata["project"],
        "root_dir": root_dir,
    },
)

config: Config = manager.load_config_model()
