from enum import Enum


class DesiredState(Enum):
    RUNNING = "start"
    DEPLOYED = "stop"
    PROVISIONED = ""

