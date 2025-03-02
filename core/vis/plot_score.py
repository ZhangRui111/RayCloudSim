import numpy as np
import matplotlib.pyplot as plt


class PlotScore:
    """Plot the training and testing scores."""
    def __init__(self, metrics, modes, save_dir=None, display=False):    
        self.metrics = metrics 
        self.modes = modes
        self.score = {mode: {metric: [] for metric in metrics} for mode in modes}
        self.save_dir = save_dir
        self.display = display
        
        
    def append(self, mode, metric, value):
        self.score[mode][metric].append(value)
        
        
    def plot(self, num_epoch):
        
        len_metrics = len(self.metrics)
        len_modes = len(self.modes)
        
        fig, ax = plt.subplots(len_modes,  len_metrics , figsize=(15 * len_metrics, 5*len_modes))
        
        for i, mode in enumerate(self.modes):
            for j, metric in enumerate(self.metrics):
                ax[i, j].plot(np.arange(num_epoch), self.score[mode][metric])
                ax[i, j].set_title(f"{mode} - {metric}")
                ax[i, j].set_xlabel("Epoch")
                ax[i, j].set_ylabel(metric)
                
        if self.save_dir is not None:
            fig.savefig(f"{self.save_dir}/score_plot.png")

        if self.display:
            plt.show()

        

