import matplotlib.pyplot as plt
import numpy as np

class CellGraph:

    def __init__(self, id, cell_df, IMAGING_RATE, EXPERIMENT_LENGTH):
        self.id = id
        self.cell_df = cell_df
        self.IMAGING_RATE = IMAGING_RATE
        self.EXPERIMENT_LENGTH = EXPERIMENT_LENGTH

    def initialize_graph(self):
        TICK_INTERVAL = 40
        self.EXPERIMENT_DURATION = self.EXPERIMENT_LENGTH * self.IMAGING_RATE
        self.fig, self.ax = plt.subplots()
        self.fig.supylabel("cell volume [fl]")
        self.fig.supxlabel("time [min]")
        self.fig.suptitle("Cell volume from 2D cell mask")
        self.ax.set_xlim(0, self.EXPERIMENT_DURATION + self.IMAGING_RATE)
        self.ax.set_ylim(0, 700)
        plt.xticks(
            np.arange(0, self.EXPERIMENT_DURATION, TICK_INTERVAL),
            rotation=90,
        )

    def graph_cell_size(self):
        self.x = self.get_x()
        self.y = self.get_y()
        self.ax.plot(self.x, self.y, "k")

    def get_x(self):
        x = self.cell_df["time_minutes"]
        return x

    def get_y(self):
        y = self.cell_df["cell_vol_fl"]
        return y



