from enum import Enum


class FinalState(Enum):
    ACTIVE = "RUNNING"
    INACTIVE = "DEPLOYED"
    PROVISIONED = "PROVISIONED"
    FAILED = "FAILED"
