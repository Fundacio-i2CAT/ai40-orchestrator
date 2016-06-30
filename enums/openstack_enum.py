from enum import Enum


class OpenstackEnum(Enum):
    ACTIVE = "ACTIVE"
    SHUTOFF = "DEPLOYED"
    PROVISIONED = "PROVISIONED"
    RUNNING = {"os-start": None}
    DEPLOYED = {"os-stop": None}
    DESTROYED = "DESTROYED"
