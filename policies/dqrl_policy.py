import torch
import torch.nn as nn
import torch.optim as optim
import random
from torch.distributions import Categorical  # (optional for epsilon random selection)

from core.env import Env
from core.task import Task

device = torch.device("cuda" if torch.cuda.is_available() else "cpu") 

# Define the seed value
seed = 42

# Set seed for PyTorch
torch.manual_seed(seed)

# Set seed for CUDA (if using GPUs)
torch.cuda.manual_seed(seed)
torch.cuda.manual_seed_all(seed)

# Set seed for Python's random module
random.seed(seed)

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
        
        self.obs_type = config["model"]["obs_type"]
        
        self.n_observations = len(self._make_observation(env, None, self.obs_type))
        
        self.num_actions = len(env.scenario.node_id2name)

        # Retrieve configuration parameters.
        self.gamma = config["training"]["gamma"]
        self.epsilon = config["training"]["epsilon"]
        lr = config["training"]["lr"]
        hidden_size = config["model"]["d_model"]
        n_layers = config["model"]["n_layers"]
        
        # Build the neural network model.
        if n_layers > 1:
            self.model = nn.Sequential(
            nn.Linear(self.n_observations, hidden_size),
            nn.ReLU(),
            *[nn.Linear(hidden_size, hidden_size), nn.ReLU()] * (n_layers - 2),
            nn.Linear(hidden_size, self.num_actions),
        ).to(device)
        elif n_layers == 1:
            self.model = nn.Sequential(
            nn.Linear(self.n_observations, self.num_actions),
        ).to(device)
        else:
            raise ValueError("Invalid number of layers.")
        
        self.model.apply(lambda m: nn.init.xavier_uniform_(m.weight) if isinstance(m, nn.Linear) else None)
        
        self.optimizer = optim.Adam(self.model.parameters(), lr=lr)
        self.criterion = nn.MSELoss()

        # Replay buffer for transitions.
        self.replay_buffer = []

    def _make_observation(self, env: Env, task: Task, obs_type=["cpu", "buffer", "bw"]):
        """
        Returns a flat observation vector.
        For instance, returns free CPU frequency for each node combined with free bandwidth per link.
        """
        
        
        obs = []
        
        if "cpu" in obs_type:
            cpu_obs = [env.scenario.get_node(node_name).free_cpu_freq 
                       for node_name in env.scenario.get_nodes()]
            obs += cpu_obs
            
        if "buffer" in obs_type:
            buffer_obs = [env.scenario.get_node(node_name).buffer_free_size()
                          for node_name in env.scenario.get_nodes()]
            obs += buffer_obs
            
        if "bw" in obs_type:
            bw_obs = [env.scenario.get_link(link_name[0], link_name[1]).free_bandwidth
                      for link_name in env.scenario.get_links()]
            obs += bw_obs

        return obs

    def act(self, env, task, train=True):
        """
        Chooses an action using an ε-greedy strategy and records the current state.
        """
        state = self._make_observation(env, task, self.obs_type)
        state_tensor = torch.tensor(state, dtype=torch.float32).unsqueeze(0).to(device)
        
        if random.random() < self.epsilon and train:
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
        Performs an update over all stored transitions using batched operations
        and clears the replay buffer.
        """
        if not self.replay_buffer:
            return 0.0

        # Unpack transitions and convert to batched tensors.
        states, actions, rewards, next_states, dones = zip(*self.replay_buffer)
        states = torch.tensor(states, dtype=torch.float32).to(device)
        rewards = torch.tensor(rewards, dtype=torch.float32).to(device)
        next_states = torch.tensor(next_states, dtype=torch.float32).to(device)
        dones = torch.tensor(dones, dtype=torch.float32).to(device)
        
        actions_tensor = torch.tensor(actions, dtype=torch.int64).to(device).unsqueeze(1)

        self.optimizer.zero_grad()

        # Compute Q-values for current states and gather the Q-value for the taken action.
        q_values = self.model(states)
        predicted_q = q_values.gather(1, actions_tensor).squeeze()

        # Compute target Q-values using next states.
        with torch.no_grad():
            next_q_values = self.model(next_states)
            max_next_q, _ = torch.max(next_q_values, dim=1)
            # If gamma is zero, the target is just the immediate reward.
            target_q = rewards if self.gamma == 0 else rewards + (1 - dones) * self.gamma * max_next_q

        # Compute loss and perform backpropagation.
        loss = self.criterion(predicted_q, target_q)
        loss.backward()
        self.optimizer.step()
        
        self.replay_buffer.clear()
        return loss.item()
    
    def epsilon_decay(self, decay_rate=0.9):
        """
        Decays the epsilon value for exploration-exploitation trade-off.
        """
        self.epsilon = self.epsilon * decay_rate
        
    def lr_decay(self, decay_rate=0.9):
        """
        Decays the learning rate.
        """
        for param_group in self.optimizer.param_groups:
            param_group['lr'] *= decay_rate
