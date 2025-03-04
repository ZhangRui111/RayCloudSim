import torch
import torch.nn as nn
import torch.optim as optim
import random
from torch.distributions import Categorical  # (optional for epsilon random selection)

class DQRLPolicy:
    def __init__(self, env, config):
        """
        A simple deep Q-learning policy.

        Args:
            env: The simulation environment.
            config (dict): A configuration dictionary containing:
                - training: with keys 'lr', 'gamma', 'epsilon'
                - model: with key 'd_model' (used as the hidden size)
        """
        self.env = env
        # Observation dimension: for instance, free CPU frequency per node plus additional info.
        self.n_observations = 3 * len(env.scenario.get_nodes()) - 2
        self.num_actions = len(env.scenario.node_id2name)

        # Retrieve configuration parameters.
        self.gamma = config["training"]["gamma"]
        self.epsilon = config["training"]["epsilon"]
        lr = config["training"]["lr"]
        hidden_size = config["model"]["d_model"]

        # Build the neural network model.
        self.model = nn.Sequential(
            nn.Linear(self.n_observations, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, self.num_actions)
        )
        self.optimizer = optim.Adam(self.model.parameters(), lr=lr)
        self.criterion = nn.MSELoss()

        # Replay buffer for transitions.
        self.replay_buffer = []

    def _make_observation(self, env, task):
        """
        Returns a flat observation vector.
        For instance, returns free CPU frequency for each node combined with free bandwidth per link.
        """
        cpu_obs = [env.scenario.get_node(node_name).free_cpu_freq 
                   for node_name in env.scenario.get_nodes()]
        bw_obs = [env.scenario.get_link(link_name[0], link_name[1]).free_bandwidth
                  for link_name in env.scenario.get_links()]
        obs = cpu_obs + bw_obs
        return obs

    def act(self, env, task):
        """
        Chooses an action using an ε-greedy strategy and records the current state.
        """
        state = self._make_observation(env, task)
        state_tensor = torch.tensor(state, dtype=torch.float32).unsqueeze(0)
        
        if random.random() < self.epsilon:
            action = random.randrange(self.num_actions)
        else:
            with torch.no_grad():
                q_values = self.model(state_tensor)
                action = torch.argmax(q_values, dim=1).item()

        # Return both the chosen action and the current state.
        return action, state

    def store_transition(self, state, action, reward, next_state, done):
        """
        Stores a transition in the replay buffer.
        """
        self.replay_buffer.append((state, action, reward, next_state, done))
        
    def update(self):
        """
        Performs an update over all stored transitions and clears the buffer.
        """
        if not self.replay_buffer:
            return 0.0
        
        loss_total = 0.0
        self.optimizer.zero_grad()
        for state, action, reward, next_state, done in self.replay_buffer:
            state_tensor = torch.tensor(state, dtype=torch.float32).unsqueeze(0)
            next_state_tensor = torch.tensor(next_state, dtype=torch.float32).unsqueeze(0)
            reward_tensor = torch.tensor(reward, dtype=torch.float32)
            done_tensor = torch.tensor(done, dtype=torch.float32)
            
            q_values = self.model(state_tensor)
            predicted_q = q_values[0, action]
            with torch.no_grad():
                next_q_values = self.model(next_state_tensor)
                max_next_q = torch.max(next_q_values)
                target_q = reward_tensor + (1 - done_tensor) * self.gamma * max_next_q
            loss = self.criterion(predicted_q, target_q)
            loss_total += loss
        loss_total.backward()
        self.optimizer.step()
        self.replay_buffer.clear()
        return loss_total.item()
