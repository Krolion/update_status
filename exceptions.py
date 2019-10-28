class NoTaskData(Exception):
    """Raised when Tracker do not return tasks list"""


class NoTransition(Exception):
    """Raised when transition not found"""


class CantMakeTransition(Exception):
    """Raised when can't make transition (status_code not in [200, 201])"""


class CantGetTransitions(Exception):
    """Raised when can't get transitions (status_code not in [200, 201])"""
