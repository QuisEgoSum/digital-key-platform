import os

if not os.environ.get("CONFIG"):
    os.environ["CONFIG"] = "./config/test.yaml"

pytest_plugins = [
    "tests.fixtures.sanic_apps",
    "tests.fixtures.shared",
    "tests.fixtures.infra",
    "tests.fixtures.user",
]
