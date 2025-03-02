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

    def eval(self, info) -> float:
        n = 0
        m = len(info)
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

    def eval(self, info) -> float:
        
        latencies = []
        for _, val in info.items():
            
            if val[0] == 0:
                task_trans_time, task_wait_time, task_exe_time = val[1][0], val[1][1], val[1][2]
                latencies.append(task_wait_time + task_exe_time + task_trans_time)
                
                
                
        if len(latencies) == 0:
            return 1

        return sum(latencies) / len(latencies)


class AvgEnergy(object):
    """The average energy consumption per task.
    
    Note:
        Currently not applicable for evaluating divisible tasks.
    """
    def __init__(self) -> None:
        pass

    def eval(self, info) -> float:
        pass
