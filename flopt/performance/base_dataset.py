class BaseDataset:
    """Base Dataset"""

    def create_instance(self, instance_name):
        """defined each dataset

        Parameters
        ----------
        instance_name : str

        Returns
        -------
        BaseInstance

        .. note::

          The formulation is changed by algorithm of solver

        """
        raise NotImplementedError()

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

    def __getitem__(self, instance_name):
        assert isinstance(instance_name, str)
        return self.createInstance(instance_name)

    def __str__(self):
        s = f"{self.name} Dataset\n\n"
        s += f"instances\n"
        s += f"---------\n"
        s += "\n".join(self.instance_names)
        return s


class BaseInstance:
    """Base Instance"""

    def createProblem(self, solver):
        """create probelm

        Parameters
        ----------
        solver : Solver

        Returns
        -------
        (bool, Problem)
          if solver can be solve this instance return
        """
        raise NotImplementedError()

    def getBestBound(self):
        """return the optimal value of objective function"""
        raise NotImplementedError()
