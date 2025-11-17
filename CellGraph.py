from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np
import polars as pl


class CellGraph:

    def __init__(self, id, cell_df, IMAGING_RATE, EXPERIMENT_LENGTH, MEDIUM_SWITCH):
        self.id = id
        self.cell_df = cell_df
        self.IMAGING_RATE = IMAGING_RATE
        self.EXPERIMENT_LENGTH = EXPERIMENT_LENGTH
        self.MEDIUM_SWITCH = MEDIUM_SWITCH

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
        x = self.cell_df["time_minutes"].to_numpy()
        return x

    def get_y(self):
        y = self.cell_df["cell_vol_fl"].to_numpy()
        return y

    def graph_medium_switch(self):
        self.ax.vlines(
            x=self.MEDIUM_SWITCH * self.IMAGING_RATE,
            ymax=self.ax.get_ylim()[1],
            ymin=0,
            color="r",
        )
        pass

    def graph_cycles(self):
        self.cycle_stages = self.get_cycle_stages()
        self.cycles = self.get_cycles()
        self.cycle_lengths = self.get_cycle_lengths() if self.cycles.size > 1 else np.array([0])
        self.average_cycle_length = self.get_average_cycle_length()

        self.cycle_data = self.save_cycles()

        self.ax.vlines(
            x=self.cycles * self.IMAGING_RATE,
            ymin=0,
            ymax=self.ax.get_ylim()[1],
            color="b",
        )

        for idx, l in enumerate(self.cycle_lengths):
            self.ax.text(
                x=self.cycle_lengths[idx] * self.IMAGING_RATE,
                y=self.ax.get_ylim()[1]-40,
                s=str(l),
                rotation=90,
            )

    def save_cycles(self):
        cycler = defaultdict(list)
        for idx in range(len(self.cycles)):
            cycler["ID"].append(self.id)
            cycler["cycles"].append(self.cycles[idx] * self.IMAGING_RATE)
            cycler["cycle_lengths"].append(self.cycle_lengths[idx-1] * self.IMAGING_RATE if idx != 0 else 0)
            cycler["average_cycle_length"].append(self.average_cycle_length * self.IMAGING_RATE)
        return pl.DataFrame(cycler)

    def get_cycle_stages(self):
        cc = self.cell_df["cell_cycle_stage"].to_numpy()
        # convert S phase to 1 and G1 to 0
        cc = np.where(cc == "S", 1, 0)
        return cc

    def get_cycles(self):
        # entrances are 1 where G1 goes to S phase
        # caveat: if the experiment starts with S phase, but finished with G1, it will yield a cell cycle start. Wanted behaviour for all cells or rather remove completely?
        shifted_by_1 = np.append(self.cycle_stages[-1:], self.cycle_stages[:-1])
        entrances = np.where(self.cycle_stages > shifted_by_1, 1, 0)
        # the 0 is added as a dummy value for the first (incomplete) cycle
        cycles = np.append(np.array([0]), np.nonzero(entrances))
        return cycles

    def get_cycle_lengths(self):
        return np.diff(self.cycles)

    def get_average_cycle_length(self):
        return np.average(self.cycle_lengths)

    def get_size_at_(self, time_point):
        return self.y[time_point]

    def get_lineage(self):
        return self.cell_df["relationship"].to_numpy()[0]

    def get_first_G1_frame(self):
        for i in self.cycles:
            if i > 0:
                return i 
        return -1

if __name__ == "__main__":
    cell_df = pl.DataFrame(
        {
            "wow": ["wow" for _ in range(6)],
            "cell_cycle_stage": ["S", "G1", "S", "S", "G1", "G1"],
        }
    )
