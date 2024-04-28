from ..base_policy import BasePolicy

import random


class DemoRandom(BasePolicy):

    def act(self, env, task):
        return random.randint(0, len(env.scenario.get_nodes()) - 1)
