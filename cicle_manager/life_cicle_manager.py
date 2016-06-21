import abc


class LifeCicleManager(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def getCurrentState(self, service_description_id):
        raise NotImplementedError("Please Implement this method")

    @abc.abstractmethod
    def setDesiredState(self, service_project_id, state):
        raise NotImplementedError("Please Implement this method")

