import os
from core.env import Env
import pandas as pd
import matplotlib.pyplot as plt

SUCCESS = 0

class VisStats:
    def __init__(self, save_path: str):
        """
        Initialize with a path where figures will be saved.
        
        Parameters:
            save_path (str): Directory where plots will be saved.
        """
        self.save_path = save_path
        # Create the directory if it doesn't exist.
        os.makedirs(self.save_path, exist_ok=True)
        self.task_info = {}
        self.node_info = {}

    def get_stats(self, env: Env):
        """Extract task and node statistics from the environment."""
        # Process task information.
        task_list = []
        for task_id, val in env.logger.task_info.items():
            src_name, dst_name = val[2]
            if val[0] == SUCCESS:
                total_time = sum(val[1])  # Sum of task transmission, wait, and execution times.
                status = 'SUCCESS'
            else:
                total_time = 0
                status = val[1][0]  # Error code.
            task_list.append([task_id, f'{src_name}-->{dst_name}', total_time, status])
        self.task_info = pd.DataFrame(task_list, columns=['Task ID', 'Link', 'Time', 'Status'])

        # Process node information.
        node_list = []
        for node_id, val in env.logger.node_info.items():
            node_name = env.scenario.node_id2name[node_id]
            energy, cpu_freq = val
            max_cpu_freq = env.scenario.get_node(node_name).max_cpu_freq
            node_list.append([node_name, energy, cpu_freq, max_cpu_freq])
        self.node_info = pd.DataFrame(node_list, columns=['Node Name', 'Energy', 'CPU Freq', 'Max CPU Freq'])

    def vis(self, env: Env):
        """Generate and save several visualizations based on the current environment stats."""
        self.get_stats(env)

        # 1. Bar chart: Total tasks vs. successful tasks per link.
        task_counts = pd.DataFrame()
        task_counts['Success'] = self.task_info[self.task_info['Status'] == 'SUCCESS'].groupby('Link').size()
        task_counts['Total'] = self.task_info.groupby('Link').size()
        fig, ax = plt.subplots()
        p_total = ax.bar(task_counts.index, task_counts['Total'], width=0.6, label='Total')
        ax.bar_label(p_total, label_type='center')
        p_success = ax.bar(task_counts.index, task_counts['Success'], width=0.6, label='Success')
        ax.bar_label(p_success, label_type='center')
        ax.set_title('Task Offloading Statistics')
        ax.legend()
        fig.savefig(os.path.join(self.save_path, 'task_offloading_statistics.png'))
        plt.close(fig)

        # 2. Pie chart: Distribution of error types.
        errors = self.task_info[self.task_info['Status'] != 'SUCCESS']
        error_counts = errors.groupby('Status').size()
        fig, ax = plt.subplots()
        ax.pie(error_counts, labels=error_counts.index, autopct='%1.1f%%')
        ax.set_title('Type of Errors')
        fig.savefig(os.path.join(self.save_path, 'error_distribution.png'))
        plt.close(fig)

        # 3. Bar chart: Average latency per link (for successful tasks).
        node_latencies = self.task_info[self.task_info['Status'] == 'SUCCESS'].groupby('Link')['Time'].mean()
        fig, ax = plt.subplots()
        ax.bar(node_latencies.index, node_latencies)
        ax.set_title('Average Latency per Link')
        fig.savefig(os.path.join(self.save_path, 'avg_latency_per_link.png'))
        plt.close(fig)

        # 4. Bar chart: Energy consumption per node.
        fig, ax = plt.subplots()
        ax.bar(self.node_info['Node Name'], self.node_info['Energy'])
        ax.set_title('Energy Consumption per Node')
        fig.savefig(os.path.join(self.save_path, 'energy_consumption_per_node.png'))
        plt.close(fig)

        # 5. Bar chart: CPU frequency per node.
        fig, ax = plt.subplots()
        p1 = ax.bar(self.node_info['Node Name'], self.node_info['Max CPU Freq'], label='Max CPU Freq')
        ax.bar_label(p1, label_type='center')
        p2 = ax.bar(self.node_info['Node Name'], self.node_info['CPU Freq'], label='CPU Freq')
        ax.bar_label(p2, label_type='center')
        ax.set_title('CPU Frequency per Node')
        ax.legend()
        fig.savefig(os.path.join(self.save_path, 'cpu_frequency_per_node.png'))
        plt.close(fig)

        # 6. Bar chart: Percent CPU frequency per node.
        self.node_info['Percent CPU Freq'] = (self.node_info['CPU Freq'] / self.node_info['Max CPU Freq']) * 100
        fig, ax = plt.subplots()
        ax.bar(self.node_info['Node Name'], self.node_info['Percent CPU Freq'])
        ax.set_title('Percent CPU Frequency per Node')
        fig.savefig(os.path.join(self.save_path, 'percent_cpu_frequency_per_node.png'))
        plt.close(fig)

        print(f"Figures saved in {self.save_path}")
