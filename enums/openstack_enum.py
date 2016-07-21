from enum import Enum


class OpenstackEnum(Enum):
    ACTIVE = "RUNNING"
    SHUTOFF = "DEPLOYED"
    PROVISIONED = "PROVISIONED"
    RUNNING = {"os-start": None}
    DEPLOYED = {"os-stop": None}
    DESTROYED = "DESTROYED"
