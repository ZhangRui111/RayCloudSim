import torch
import torch.nn as nn
import torch.optim as optim
import random
from torch.distributions import Categorical  # (optional for epsilon random selection)

class DQRLPolicy:
    def __init__(self, env, lr=1e-3, hidden_size=128, gamma=0.99, epsilon=0.1):
        """
        A simple deep Q-learning policy.

        Args:
            env: The simulation environment.
            lr: Learning rate.
            hidden_size: Size of hidden layers.
            gamma: Discount factor.
            epsilon: For ε-greedy exploration.
        """
        self.env = env
        # Use observation dimension based on node info. For instance, we use free CPU frequency per node.
        self.n_observations = 3*len(env.scenario.get_nodes())-2
        self.num_actions = len(env.scenario.node_id2name)
        self.gamma = gamma
        self.epsilon = epsilon

        self.model = nn.Sequential(
            nn.Linear(self.n_observations, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, self.num_actions)
        )
        self.optimizer = optim.Adam(self.model.parameters(), lr=lr)
        self.criterion = nn.MSELoss()

        # Replay buffer for transitions
        self.replay_buffer = []
        
    def _make_observation(self, env, task):
        """
        Returns a flat observation vector.
        For instance, we return the free CPU frequency for each node.
        """
        cpu_obs = [env.scenario.get_node(node_name).free_cpu_freq 
               for node_name in env.scenario.get_nodes()]
        # print(env.scenario.get_links())
        bw_obs = [env.scenario.get_link(link_name[0], link_name[1]).free_bandwidth
              for link_name in env.scenario.get_links()]
        
        # print(cpu_obs)
        # print(bw_obs)
        
        obs = cpu_obs + bw_obs
        return obs

    def act(self, env, task):
        """
        Chooses an action using ε-greedy strategy and records the current state.
        """
        state = self._make_observation(env, task)
        state_tensor = torch.tensor(state, dtype=torch.float32).unsqueeze(0)
        
        if random.random() < self.epsilon:
            action = random.randrange(self.num_actions)
        else:
            with torch.no_grad():
                q_values = self.model(state_tensor)
                
                action = torch.argmax(q_values, dim=1).item()

        # Return both the action and the state (to form the transition later).
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
            reward_tensor = torch.tensor([reward], dtype=torch.float32)
            done_tensor = torch.tensor([done], dtype=torch.float32)
            
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
