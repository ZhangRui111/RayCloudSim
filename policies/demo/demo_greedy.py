
class GreedyPolicy:
    """A simple greedy policy that selects the node with the minimal 
    predicted total time (transmission + computation)."""

    def act(self, env, task):
        """
        Greedily choose the node that yields the lowest estimated total latency.

        Args:
            env (Env): The environment (for accessing node data, if needed).
            task (Task): The current task to be scheduled/offloaded.

        Returns:
            int: The selected action (index of the chosen node).
        """
        best_node = None
        best_latency = float('inf')

        # Iterate through all possible node IDs in the environment
        for node_id in range(len(env.scenario.node_id2name)):
            node_name = env.scenario.node_id2name[node_id]

            cpu_speed = env.scenario.get_node(node_name).free_cpu_freq
            transmission_time = task.task_size / task.trans_bit_rate  # seconds
            computation_time = (task.task_size * task.cycles_per_bit) /( cpu_speed + 1)
            
            total_time = transmission_time + computation_time

            # Greedy choice: pick the node with the lowest total_time
            if total_time < best_latency:
                best_latency = total_time
                best_node = node_id

        return best_node
