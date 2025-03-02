from policies.base_policy import BasePolicy


class RoundRobinPolicy(BasePolicy):
    def __init__(self):
        super().__init__()
        self.idx = 0

    def act(self, env, task):
        self.idx = (self.idx + 1) % len(env.scenario.get_nodes())
        return self.idx
