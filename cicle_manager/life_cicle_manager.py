import abc


class LifeCicleManager(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_current_state(self):
        raise NotImplementedError("Please Implement this method")

    @abc.abstractmethod
    def set_desired_state(self, state):
        raise NotImplementedError("Please Implement this method")

    _instance = None
    _data = None

    def get_instance(self):
        return self._instance

    def set_instance(self, instance):
        self._instance = instance

    def get_data(self):
        return self._data

    def set_data(self, data):
        self._data = data

    instance = property(get_instance, set_instance)
    data = property(get_data, set_data)
