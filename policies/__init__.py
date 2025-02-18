import torch
import torch.nn as nn
import torch.optim as optim
import random

class DQRLPolicy:
    def __init__(self, env, lr=1e-3, hidden_size=128*2, gamma=0.99, epsilon=0.1):
        """
        A simple Deep Q-Learning policy.

        Args:
            env (Env): The simulation environment containing scenario and metadata.
            lr (float): Learning rate.
            hidden_size (int): Hidden layer size.
            gamma (float): Discount factor.
            epsilon (float): Epsilon for epsilon-greedy action selection.
        """
        self.env = env
        # Observation dimension: we use the node information (e.g., free_cpu_freq for each node).
        # (Optionally, you can combine task-specific info with node information.)
        self.n_observations = len(env.scenario.get_nodes())
        # Assume each node is a valid action choice.
        self.num_actions = len(env.scenario.node_id2name)
        self.gamma = gamma
        self.epsilon = epsilon

        # Define a Q-network: Input -> Hidden -> Hidden -> Output (Q-values for each action)
        self.model = nn.Sequential(
            nn.Linear(self.n_observations, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, self.num_actions)
        )
        self.optimizer = optim.Adam(self.model.parameters(), lr=lr)
        self.criterion = nn.MSELoss()

    def _make_observation(self, env, task):
        """
        Extract observation features as a flat vector.

        Here we extract the free CPU frequency for each node.
        (You can modify this to also include task attributes if desired.)
        """
        # For example, we use free_cpu_freq of each node as observation.
        node_obs = [env.scenario.get_node(node_name).free_cpu_freq for node_name in env.scenario.get_nodes()]
        return node_obs

    def act(self, env, task):
        """
        Choose an action (i.e. select a node) using an ε-greedy strategy based on Q-values.

        Args:
            env (Env): The simulation environment.
            task (Task): The current task (used to build the observation).

        Returns:
            int: The selected action index.
        """
        # Build the observation vector and convert to a torch tensor.
        obs = self._make_observation(env, task)
        obs_tensor = torch.tensor(obs, dtype=torch.float32).unsqueeze(0)  # shape: [1, n_observations]

        # ε-greedy action selection
        if random.random() < self.epsilon:
            action = random.randrange(self.num_actions)
        else:
            with torch.no_grad():
                q_values = self.model(obs_tensor)  # shape: [1, num_actions]
                action = torch.argmax(q_values, dim=1).item()

        return action

    def update(self, state, action, reward, next_state, done):
        """
        Perform one-step Q-learning update using the temporal difference error.

        Args:
            state (list[float]): The observation vector at time t.
            action (int): The action taken.
            reward (float): The immediate reward received.
            next_state (list[float]): The observation vector at time t+1.
            done (bool): Whether the episode ended at t+1.
        
        Returns:
            float: The computed loss value.
        """
        # Convert to torch tensors.
        state_tensor = torch.tensor(state, dtype=torch.float32).unsqueeze(0)      # shape: [1, n_observations]
        next_state_tensor = torch.tensor(next_state, dtype=torch.float32).unsqueeze(0)
        reward_tensor = torch.tensor([reward], dtype=torch.float32)                # shape: [1]
        done_tensor = torch.tensor([done], dtype=torch.float32)                    # shape: [1]

        # Compute predicted Q-value for the taken action.
        q_values = self.model(state_tensor)  # shape: [1, num_actions]
        predicted_q = q_values[0, action]

        # Compute target Q-value: if done, target is reward; else reward + gamma * max(Q(next_state)).
        with torch.no_grad():
            next_q_values = self.model(next_state_tensor)
            max_next_q = torch.max(next_q_values)
            target_q = reward_tensor + (1 - done_tensor) * self.gamma * max_next_q

        loss = self.criterion(predicted_q, target_q)

        # Backpropagation and parameter update.
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        return loss.item()
