import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import csv

class Logger:
    """
    Logger creates a unique log directory and writes log messages immediately to a log.txt file.
    It stores logged data (rows with Epoch, Mode, Metric, Value) internally, prints each update,
    and provides methods to plot the results and save them to a CSV.
    """
    def __init__(self, config):
        """
        Initializes the Logger with the given configuration.

        Args:
            config (dict): The configuration dictionary. Must contain:
                - env: with keys "dataset" and "flag"
                - policy: the policy name (string)
                - training: training parameters (e.g., num_epoch, batch_size, lr, gamma, epsilon, etc.)
        """
        self.config = config
        self.dataset = config["env"]["dataset"]
        self.flag = config["env"]["flag"]
        self.policy = config["policy"]
        self.training_config = config.get("training", {})
        
        # Create log directory in the form: logs/<dataset>/<flag>/<policy>/<params>_<i>
        self.log_dir = self.create_log_dir(self.dataset, self.flag, self.policy, **self.training_config)
        self.log_file_path = os.path.join(self.log_dir, "log.txt")
        self.csv_file_path = os.path.join(self.log_dir, "result.csv")
        
        # Open the log file for writing.
        self.log_file = open(self.log_file_path, "w")
        self._write_header()
        
        # Use rows as the sole storage for logged data.
        # Each row is a dictionary with keys: "Epoch", "Mode", "Metric", "Value".
        self.rows = []
        self.current_epoch = None
        self.current_mode = None

    @staticmethod
    def create_log_dir(dataset, flag, policy, **params):
        """
        Creates a unique log directory with the format:
            logs/<dataset>/<flag>/<policy>/<params>_<i>

        Args:
            dataset (str): Dataset name.
            flag (str): Flag name.
            policy (str): The policy name.
            **params: Additional training parameters to include in the directory name.

        Returns:
            str: The created log directory path.
        """
        base_dir = os.path.join("logs", dataset, flag, policy)
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)
            
        params_str = ""
        j = 0
        for key, value in params.items():
            params_str += f"{key}_{value}_"
            j += 1
            if j > 2:
                break
        index = 0
        log_dir = os.path.join(base_dir, f"{params_str}{index}")
        while os.path.exists(log_dir):
            index += 1
            log_dir = os.path.join(base_dir, f"{params_str}{index}")
        os.makedirs(log_dir, exist_ok=True)
        return log_dir

    def _write_header(self):
        """
        Writes header information (configuration details) to the log file.
        """
        header = "====================\n"
        header += f"Policy: {self.policy}\n\n"
        header += f"Dataset: {self.dataset}\nFlag: {self.flag}\n\n"
        
        for key, value in self.config.items():
            if key not in ["env", "policy"]:
                if isinstance(value, dict):
                    header += f"{key}:\n"
                    for k, v in value.items():
                        header += f"    {k}: {v}\n"
                else:   
                    header += f"{key}: {value}\n"
        header += "\n"
        
        for key, value in self.training_config.items():
            header += f"{key}: {value}\n"
        header += "====================\n\n"
        self.log_file.write(header)
        self.log_file.flush()
        print(header)

    def update_epoch(self, epoch):
        """
        Updates the current epoch and writes a header line to the log file.

        Args:
            epoch (int): The current epoch (0-indexed; will be logged as 1-indexed).
        """
        self.current_epoch = epoch + 1
        line = f"\n====================\nEpoch {self.current_epoch}/{self.training_config['num_epochs']}\n"
        print(line, end="")
        self.log_file.write(line)
        self.log_file.flush()

    def update_mode(self, mode):
        """
        Updates the current mode (e.g., "Training" or "Testing") and writes it to the log file.

        Args:
            mode (str): The current mode.
        """
        self.current_mode = mode
        line = f"   Mode: {mode}\n"
        print(line, end="")
        self.log_file.write(line)
        self.log_file.flush()

    def update_metric(self, metric, value):
        """
        Logs a metric value under the current epoch and mode. If current_epoch or current_mode
        is None, an empty string is stored instead. The logged value is stored internally,
        written to the log file, printed, and appended as a row for CSV export (immediately).

        Args:
            metric (str): The metric name.
            value (float): The metric value.
        """
        # Use empty string if current_epoch or current_mode is not set.
        epoch_val = self.current_epoch if self.current_epoch is not None else ""
        mode_val = self.current_mode if self.current_mode is not None else ""
        
        row = {
            "Epoch": epoch_val,
            "Mode": mode_val,
            "Metric": metric,
            "Value": value
        }
        self.rows.append(row)
        line = f"       {metric}: {value:.4f}\n"
        print(line, end="")
        self.log_file.write(line) 
        self.log_file.flush()
        # Write this row immediately to CSV.
        self._append_to_csv(row)

    def _append_to_csv(self, row):
        """
        Appends a single row to the CSV file. If the CSV file is empty, writes the header first.
        """
        file_exists = os.path.exists(self.csv_file_path) and os.path.getsize(self.csv_file_path) > 0
        with open(self.csv_file_path, "a", newline="") as csvfile:
            fieldnames = ["Epoch", "Mode", "Metric", "Value"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow(row)

    def plot(self):
        """
        Plots the logged metrics over epochs for each mode and metric. If the Epoch values
        are not numeric, the x-axis is set as the order of appearance.
        """
        # Convert stored rows to a DataFrame.
        df = pd.DataFrame(self.rows)
        
        # For plotting, if 'Epoch' cannot be converted to a number, use row order.
        try:
            df['Epoch_num'] = pd.to_numeric(df['Epoch'], errors='raise')
        except Exception:
            # If conversion fails (e.g., empty string), use the row index.
            df['Epoch_num'] = df.groupby(["Mode", "Metric"]).cumcount() + 1
        
        modes = df['Mode'].unique()
        metrics = df['Metric'].unique()
        num_modes = len(modes)
        num_metrics = len(metrics)
        
        fig, axes = plt.subplots(num_modes, num_metrics, figsize=(6 * num_metrics, 4 * num_modes))
        # Ensure axes is a 2D array.
        if num_modes == 1 and num_metrics == 1:
            axes = np.array([[axes]])
        elif num_modes == 1:
            axes = np.array([axes])
        elif num_metrics == 1:
            axes = np.array([[ax] for ax in axes])
        
        for i, mode in enumerate(modes):
            for j, metric in enumerate(metrics):
                subset = df[(df['Mode'] == mode) & (df['Metric'] == metric)]
                if subset.empty:
                    continue
                x = subset['Epoch_num']
                y = subset['Value']
                axes[i, j].plot(x, y, marker='o')
                title_mode = mode if mode != "" else "Unknown"
                axes[i, j].set_title(f"{title_mode} - {metric}")
                axes[i, j].set_xlabel("Epoch")
                axes[i, j].set_ylabel(metric)
        plt.tight_layout()
        plot_path = os.path.join(self.log_dir, "score_plot.png")
        plt.savefig(plot_path)
        plt.show()

    def save_csv(self):
        """
        Saves the logged results to a CSV file in the log directory.
        """
        df = pd.DataFrame(self.rows)
        df.to_csv(self.csv_file_path, index=False)

    def close(self):
        """
        Closes the log file.
        """
        if self.log_file:
            self.log_file.close()
