
class BaseDataset:
    """
    Base Dataset
    """
    def create_instance(self, instance_name):
        """
        defined each dataset

        .. note::

          The formulation is changed by algorithm of solver

        """
        pass

    def genInstances(self):
        """
        generator of function instance
        """
        for instance_name in self.instance_names:
            yield self.createInstance(instance_name)

    def createProblem(self, solver):
        """
        Create problem according to solver
        """
        return None

    def __iter__(self):
        return self.genInstances()


class BaseInstance:
    """
    Base Instance
    """
    def getBestValue(self):
        """
        return the optimal value of objective function
        """
        return None
