class SuccessRate(object):
    """The success rate of all tasks.
        
    success rate = n/m, where,
        - n: successfully completed tasks
        - m: all tasks
    
    Note:
        Currently not applicable for evaluating divisible tasks.
    """
    def __init__(self) -> None:
        pass

    def eval(self, logger) -> float:
        
        info = logger.task_info
        
        n = 0
        m = len(info)
        
        if m == 0:
            return 0.0
        
        for _, val in info.items():
            if val[0] == 0:
                n += 1
        return n / m


class AvgLatency(object):
    """The average latency per task.
    
    Note:
        Currently not applicable for evaluating divisible tasks.
    """
    def __init__(self) -> None:
        pass

    def eval(self, logger, eps=1e-6) -> float:
        
        latencies = []
        info = logger.task_info
        
        statue_code_idx = logger.get_value_idx("status_code")
        time_list_idx = logger.get_value_idx("time_list")
        
        for _, val in info.items():
            
            if val[statue_code_idx] == 0:
                task_trans_time, task_wait_time, task_exe_time = val[time_list_idx][0], val[time_list_idx][1], val[time_list_idx][2]
                latencies.append(task_wait_time + task_exe_time + task_trans_time)
  
        if len(latencies) == 0:
            return 0

        return sum(latencies) / len(latencies)


class AvgEnergy(object):
    """The average energy consumption per task.
    
    Note:
        Currently not applicable for evaluating divisible tasks.
    """
    def __init__(self) -> None:
        pass

    def eval(self, logger, eps=1e-6) -> float:
        
        energy = []
        info = logger.task_info

        energy_list_idx = logger.get_value_idx("time_list")
        
        for _, val in info.items():

            task_trans_energy, task_exe_energy = val[energy_list_idx][0], val[energy_list_idx][1]
            energy.append(task_trans_energy + task_exe_energy)
  
        if len(energy) == 0:
            return 0

        return sum(energy) / len(energy)
