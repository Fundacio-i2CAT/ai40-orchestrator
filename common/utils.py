from enums.desired_state import DesiredState
from enums.final_state import FinalState


def get_state(state):
    switcher = {
        "ACTIVE": FinalState.ACTIVE.value,
        "INACTIVE": FinalState.INACTIVE.value,
        "STARTED": DesiredState.STARTED.value,
        "STOPPED": DesiredState.STOPPED.value,
    }
    return switcher.get(state)
