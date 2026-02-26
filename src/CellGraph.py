from collections import defaultdict
from matplotlib import axes
import matplotlib.pyplot as plt
import numpy as np
import polars as pl


class CellGraph:
    def __init__(
        self, id, cell_df, FILE_DIR, IMAGING_RATE, EXPERIMENT_LENGTH, MEDIUM_SWITCH
    ):
        self.id = id
        self.cell_df = cell_df
        self.FILE_DIR = FILE_DIR
        self.IMAGING_RATE = IMAGING_RATE
        self.EXPERIMENT_LENGTH = EXPERIMENT_LENGTH
        self.MEDIUM_SWITCH = MEDIUM_SWITCH
        self.setup_dir()

    def setup_dir(self):
        self.figure_dir = self.FILE_DIR / "Figures"
        self.cycles_dir = self.FILE_DIR / "Cycles"
        for i in [self.figure_dir, self.cycles_dir]:
            i.mkdir(parents=True, exist_ok=True)

    def initialize_graph(self):
        TICK_INTERVAL = 40
        self.EXPERIMENT_DURATION = self.EXPERIMENT_LENGTH * self.IMAGING_RATE
        self.fig, self.ax = plt.subplots()
        self.fig.supylabel("cell volume [fl]")
        self.fig.supxlabel("time [min]")
        self.fig.suptitle("Cell volume from 2D cell mask")
        self.ax.set_xlim(0, self.EXPERIMENT_DURATION)
        self.ax.set_ylim(0, 700)
        plt.xticks(
            np.arange(0, self.EXPERIMENT_DURATION, TICK_INTERVAL),
            rotation=90,
        )

    def graph_cell_size(self):
        self.x = self.get_x()
        self.y = self.get_y()
        # self.ax.plot(self.x, self.y, "k")

    def get_x(self):
        x = self.cell_df["time_minutes"].to_numpy()
        return x

    def get_y(self):
        y = self.cell_df["cell_vol_fl"].to_numpy()
        return y

    def size_at_(self, frames: int | np.ndarray) -> float | np.ndarray:
        return self.y[frames]

    def time_at_(self, frames: int | np.ndarray) -> float | np.ndarray:
        return frames * self.IMAGING_RATE

    def graph_medium_switch(self):
        self.ax.vlines(
            x=self.time_at_(self.MEDIUM_SWITCH),
            ymax=self.ax.get_ylim()[1],
            ymin=0,
            color="r",
        )
        pass

    def graph_cycles(self):
        self.cycle_stages = self.get_cycle_stages()
        self.cycles = self.get_cycles()
        self.cycle_lengths: np.ndarray = (
            self.get_cycle_lengths() if self.cycles.size > 1 else np.array([0])
        )
        self.average_cycle_length = self.get_average_cycle_length()

        # self.ax.vlines(
        #     x=self.time_at_(self.cycles),
        #     ymin=0,
        #     ymax=self.ax.get_ylim()[1],
        #     color="b",
        # )

        # self.text(
        #     ax=self.ax,
        #     x=self.time_at_(self.cycles + 1.5),
        #     y=self.ax.get_ylim()[1] - 40,
        #     txt=self.time_at_(np.append(np.array([0]), self.cycle_lengths)),
        # )

    def text(self, ax: axes.Axes, x: np.ndarray, y: float, txt):
        # wrapper for array-like x and s inputs
        for idx, v in enumerate(x):
            ax.text(
                x=v,
                y=y,
                s=str(txt[idx]),
                rotation=90,
            )

    def save_data(self):
        # should be refactored with time_at_ functions
        cycler = defaultdict(list)
        self.lineage = self.get_lineage()
        self.size_at_first_g1 = (
            self.size_at_(self.get_first_G1_frame())
            if self.lineage == "bud"
            else np.float32(-1)
        )
        self.sizes_at_buds: np.ndarray = self.size_at_(self.cycles)
        for idx in range(len(self.cycles)):
            cycler["ID"].append(self.id)
            cycler["Cycles at (min)"].append(self.cycles[idx] * self.IMAGING_RATE)
            cycler["Cycle lengths (min)"].append(
                self.cycle_lengths[idx - 1] * self.IMAGING_RATE
                if idx != 0
                else np.float32(-1)
            )
            cycler["Average cycle length (min)"].append(
                self.average_cycle_length * self.IMAGING_RATE
            )
            cycler["Cell size at first g1 (min)"].append(self.size_at_first_g1)
            cycler["Sizes at bud (fl)"].append(
                self.sizes_at_buds[idx-1] if idx != 0 else np.float32(-1)
            )
            cycler["Lineage"].append(self.lineage)
        cycle_data = pl.DataFrame(
            cycler,
        ).cast({
                "ID": pl.Int16,
                "Cycles at (min)": pl.Int16,
                "Cycle lengths (min)": pl.Float32,
                "Average cycle length (min)": pl.Float32,
                "Cell size at first g1 (min)": pl.Float32,
                "Sizes at bud (fl)": pl.Float32,
                "Lineage": pl.String,
            })
        return cycle_data

    def get_cycle_stages(self):
        cc = self.cell_df["cell_cycle_stage"].to_numpy()
        # convert S phase to 1 and G1 to 0
        cc = np.where(cc == "S", 1, 0)
        return cc

    def get_cycles(self):
        # entrances are 1 where G1 goes to S phase
        # caveat: if the experiment starts with S phase, but finished with G1, it will yield a cell cycle start. Wanted behaviour for all cells or rather remove completely?
        entrances = np.where(self.cycle_stages[:-1] > self.cycle_stages[1:], 1, 0)
        # nonzero returns a tuple (multidimensional arrays)
        cycles = np.nonzero(entrances)[0]
        return cycles

    def get_cycle_lengths(self):
        return np.diff(self.cycles)

    def get_average_cycle_length(self):
        return np.average(self.cycle_lengths)

    def get_lineage(self):
        return self.cell_df["relationship"].to_numpy()[0]

    def get_first_G1_frame(self):
        for i in self.cycles:
            if i > 0:
                return i
        return -1

    def save_csv(self):
        if self.cycles.size > 0:
            self.cycle_data = self.save_data()
            self.cycle_data.write_csv(self.cycles_dir / f"Cell_{self.id}.csv")

    def save_fig(self):
        self.fig.tight_layout()
        self.fig.savefig(self.figure_dir / f"Cell_{self.id}.png")
        plt.close()


if __name__ == "__main__":
    cell_df = pl.DataFrame(
        {
            "wow": ["wow" for _ in range(6)],
            "cell_cycle_stage": ["S", "G1", "S", "S", "G1", "G1"],
        }
    )
