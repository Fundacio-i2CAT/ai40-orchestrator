import abc
import requests

class SimpleLifeCicleManager(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def getCurrentState(self, service_description_id):
        raise NotImplementedError("Please Implement this method")

    @abc.abstractmethod
    def setDesiredState(self, state):
        raise NotImplementedError("Please Implement this method")


class SimpleLifeCicleManagerImpl(SimpleLifeCicleManager):
    def setDesiredState(self, state):
        pass

    def getCurrentState(self, service_description_id):
        # Connect to BBDD . Get the data connection
        result = requests.get('http://0.0.0.0:8080/catalog/api/v0.1/service/context/'
                              + service_description_id)
        print result.text


if __name__ == "__main__":
    slcm = SimpleLifeCicleManagerImpl()
    slcm.getCurrentState("575aa1d2bccddd0603e3dd4d")
