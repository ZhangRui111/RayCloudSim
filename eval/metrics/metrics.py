class SuccessRate:
    """Calculates the success rate of tasks.

    The success rate is defined as the ratio of successfully completed tasks
    to the total number of tasks.

    Success Rate = (Number of Successfully Completed Tasks) / (Total Number of Tasks)

    Note:
        This metric is currently designed for non-divisible tasks. Its applicability
        to divisible tasks may require further consideration or modification.
    """
    def __init__(self) -> None:
        pass

    def eval(self, info: dict) -> float:
        """
        Evaluates the success rate based on task information.

        Args:
            info: A dictionary containing task information. The expected format
                  is {task_id: (status_code, info_list, (src_name, dst_name))},
                  where status_code is 0 for success and 1 for failure.

        Returns:
            The calculated success rate as a float. Returns 0.0 if there are no tasks.
        """
        n = 0  # Counter for successfully completed tasks
        m = len(info)  # Total number of tasks

        # Iterate through the task information
        for _, val in info.items():
            # Check if the task status code indicates success (status_code == 0)
            if val[0] == 0:
                n += 1  # Increment the success counter

        # Calculate and return the success rate. Handle division by zero if no tasks exist.
        return n / m if m > 0 else 0.0


class AvgLatency:
    """Calculates the average latency per task.

    Latency for a task is defined as the sum of its transmission time,
    waiting time in the buffer, and execution time.

    Average Latency = (Sum of Latencies of Successfully Completed Tasks) / (Number of Successfully Completed Tasks)

    Note:
        This metric is currently designed for non-divisible tasks. Its applicability
        to divisible tasks may require further consideration or modification.
    """
    def __init__(self) -> None:
        pass

    def eval(self, info: dict) -> float:
        """
        Evaluates the average latency based on task information.

        Args:
            info: A dictionary containing task information. The expected format
                  is {task_id: (status_code, info_list, (src_name, dst_name))},
                  where status_code is 0 for success and info_list[0], info_list[1],
                  and info_list[2] are transmission time, waiting time, and
                  execution time, respectively.

        Returns:
            The calculated average latency as a float. Returns 0.0 if there are no
            successfully completed tasks.
        """
        latencies = [] # List to store latencies of successfully completed tasks

        # Iterate through the task information
        for _, val in info.items():
            # Check if the task status code indicates success (status_code == 0)
            if val[0] == 0:
                # Extract task times and calculate latency
                task_trans_time, task_wait_time, task_exe_time = val[1][0], val[1][1], val[1][2]
                latencies.append(task_wait_time + task_exe_time + task_trans_time)

        # Calculate and return the average latency. Handle division by zero if no successful tasks.
        if len(latencies) == 0:
            return 0.0 # Return 0.0 if no successfully completed tasks

        return sum(latencies) / len(latencies)


class AvgEnergy:
    """Calculates the average energy consumption per task.

    Average Energy Consumption = (Total Energy Consumption of Nodes) / (Number of Successfully Completed Tasks)

    Note:
        This metric is currently designed for non-divisible tasks. Its applicability
        to divisible tasks may require further consideration or modification.
    """
    def __init__(self) -> None:
        pass

    def eval(self, info: dict) -> float:
        """
        Evaluates the average energy consumption based on node and task information.

        Args:
            info: A dictionary containing simulation information, including
                  'task_info' and 'node_info'.
                  'task_info' format: {task_id: (status_code, info_list, (src_name, dst_name))}
                  'node_info' format: {node_id: [avg_energy_per_cycle, avg_cpu_freq]}

        Returns:
            The calculated average energy consumption per task as a float. Returns 0.0
            if there are no successfully completed tasks.
        """
        task_info = info.get('task_info', {})
        node_info = info.get('node_info', {})

        total_energy_consumption = sum(
            metrics[0] for metrics in node_info.values()
        ) # Assuming metrics[0] is average energy per cycle

        n_successful_tasks = sum(1 for val in task_info.values() if val[0] == 0)

        # Calculate and return the average energy consumption per task. Handle division by zero.
        return total_energy_consumption / n_successful_tasks if n_successful_tasks > 0 else 0.0
