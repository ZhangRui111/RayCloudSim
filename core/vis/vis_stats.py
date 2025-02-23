from core.env import Env
import pandas as pd
import matplotlib.pyplot as plt

SUCCESS = 0


class VisStats:
    def __init__(self):
        self.task_info = {}
        self.node_info = {}
        
        
    def get_stats(self, env: Env):
        task_info = env.logger.task_info

        task_list = []
        

        for task_id, val in task_info.items():
            src_name = val[2][0]
            dst_name = val[2][1]
            
            if val[0] == SUCCESS:
                              
                task_list.append([task_id, f'{src_name}-->{dst_name}', val[1][0] + val[1][1] + val[1][2], 'SUCCESS'])

                
            else:
                
                task_list.append([task_id, f'{src_name}-->{dst_name}', 0, val[1][0]])
                
            
        self.task_info = pd.DataFrame(task_list, columns=['Task ID', 'Link', 'Time', 'Status'])
        
        node_info = env.logger.node_info
        
        node_list = []
        
        for node_id, val in node_info.items():
            node_name = env.scenario.node_id2name[node_id]
            node_list.append([node_name, val[0], val[1], env.scenario.get_node(node_name).max_cpu_freq])
            
        self.node_info = pd.DataFrame(node_list, columns=['Node Name', 'Energy', 'CPU Freq', 'Max CPU Freq'])
        
            

        
    def vis(self, env: Env):
        
        # Get the stats
        self.get_stats(env)
        
        # Visualization: number of tasks and number of tasks successfully completed
        links = self.task_info['Link'].unique()
        
        print(links)
        

        task_counts = pd.DataFrame()
        
        task_counts['Success'] = self.task_info[self.task_info['Status'] == 'SUCCESS'].groupby('Link').size()
        task_counts['Total'] = self.task_info.groupby('Link').size()

        fig, ax = plt.subplots()
        
        p = ax.bar(task_counts.index, task_counts['Total'], width=0.6, label='Total')

        ax.bar_label(p, label_type='center')

        p = ax.bar(task_counts.index, task_counts['Success'], width=0.6, label='Success')

        ax.bar_label(p, label_type='center')
        
        


        ax.set_title('Task offloading statistics')
        ax.legend()

        plt.show()
        
