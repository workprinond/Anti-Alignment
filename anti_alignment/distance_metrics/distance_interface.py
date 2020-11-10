from abc import ABC, abstractmethod


class DistanceMetricInterface(ABC):


    def __init__(self):        
        super(DistanceMetricInterface, self).__init__()

    @abstractmethod
    def get_distance(self, trace, antialignment):
        pass








