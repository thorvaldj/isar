import logging
import logging.config

import yaml
from fastapi import FastAPI
from injector import Injector

from isar.apis.schedule.router import create_scheduler_router
from isar.config import config
from isar.services.utilities.json_service import EnhancedJSONEncoder


def create_app(injector: Injector):

    tags_metadata = [
        {
            "name": "Scheduler",
            "description": "Mission functionality",
        }
    ]

    logging.config.dictConfig(yaml.safe_load(open(f"./src/isar/config/logging.conf")))
    logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(
        config.get("logging", "azure_storage_logging_level")
    )
    logging.getLogger("transitions.core").setLevel(
        config.get("logging", "transitions_core_logging_level")
    )

    app = FastAPI(openapi_tags=tags_metadata)

    app.include_router(router=create_scheduler_router(injector=injector))

    return app
