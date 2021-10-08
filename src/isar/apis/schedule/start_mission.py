from dataclasses import asdict
from http import HTTPStatus
from typing import Optional

from fastapi.param_functions import Query
from injector import inject

from isar.config.log import logging
from isar.mission_planner.mission_planner_interface import (
    MissionPlannerError,
    MissionPlannerInterface,
)
from isar.models.communication.messages.start_message import StartMissionMessages
from isar.models.mission import Mission
from isar.services.utilities.scheduling_utilities import SchedulingUtilities


class StartMission:
    @inject
    def __init__(
        self,
        mission_planner: MissionPlannerInterface,
        scheduling_utilities: SchedulingUtilities,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger("api")
        self.mission_planner = mission_planner
        self.scheduling_utilities = scheduling_utilities

    def get(
        self,
        mission_id: Optional[int] = Query(
            None,
            alias="ID",
            title="Mission ID",
            description="ID-number for predefined mission",
        ),
    ):

        if not self.mission_planner.mission_id_valid(mission_id):
            message = StartMissionMessages.invalid_mission_id(mission_id)
            self.logger.error(message)
            return message, HTTPStatus.NOT_FOUND

        mission: Mission = self.mission_planner.get_mission(mission_id)
        if mission is None:
            message = StartMissionMessages.mission_not_found()
            return message, HTTPStatus.NOT_FOUND

        ready, response = self.scheduling_utilities.ready_to_start_mission()
        if not ready:
            return response

        response = self.scheduling_utilities.start_mission(mission=mission)

        self.logger.info(response)
        return response
