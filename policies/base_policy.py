from abc import ABCMeta, abstractmethod


class BasePolicy(metaclass=ABCMeta):
    """The base class of offloading policies."""

    def __init__(self) -> None:
        pass

    @abstractmethod
    def act(self, env, task):
        pass
