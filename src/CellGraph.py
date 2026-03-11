from collections import defaultdict
import polars as pl
from polars import col as c

class CellGraph:
    def __init__(
        self, id, cell_df, FILE_DIR, MEDIUM_SWITCH
    ):
        self.id = id
        self.cell_df = cell_df
        self.FILE_DIR = FILE_DIR
        self.MEDIUM_SWITCH = MEDIUM_SWITCH

        self.setup_dir()
        self.cell_df.write_csv(self.df_dir/ f"Cell_{self.id}.csv")

    def has_g1(self) -> bool:
        return self.cell_df.filter(c("cell_cycle_stage")=="G1").height > 0

    def setup_dir(self):
        self.cycles_dir = self.FILE_DIR / "Cell_cycles"
        self.df_dir = self.FILE_DIR / "Cell_frames"
        for d in [self.cycles_dir, self.df_dir]:
            d.mkdir(parents=True, exist_ok=True)

    def graph_cell_size(self):
        self.x = self.get_x()
        self.y = self.get_y()

    def get_x(self):
        x = self.cell_df.get_column("time_minutes")
        return x

    def get_y(self):
        y = self.cell_df.get_column("cell_vol_fl")
        return y

    def size_at_(self, frames: int | pl.Series) -> float | pl.Series:
        match frames:
            case pl.Series():
                return (self.cell_df.lazy()
                        .with_columns(is_in=c("frame_i").is_in(frames))
                        .select(["is_in", "cell_vol_fl"])
                        .filter(c("is_in") == True)
                        .collect()
                        .get_column("cell_vol_fl")
                        )
            case int(): 
                return (self.cell_df
                        .filter(c("frame_i") == frames)
                        )

    def time_at_(self, frames: int | pl.Series) -> float | pl.Series:
        match frames:
            case pl.Series():
                return (self.cell_df.lazy()
                        .with_columns(is_in=c("frame_i").is_in(frames))
                        .select(["is_in", "time_minutes"])
                        .filter(c("is_in") == True)
                        .collect()
                        .get_column("time_minutes")
                        )
            case int(): 
                return (self.cell_df
                        .filter(c("frame_i") == frames)
                        )

    def graph_cycles(self):
        self.cycles = self.get_cycles()
        self.cycle_lengths = self.get_cycle_lengths() 
        self.average_cycle_length = self.get_average_cycle_length()

    def save_data(self):
        cycler = defaultdict(list)
        self.lineage = self.get_lineage()
        self.size_at_first_g1 = self.get_size_at_first_G1()
        self.sizes_at_buds = self.size_at_(
                self.cycles.get_column("frame_i"))
        for row in range(self.cycles.height):
            cycler["ID"].append(self.id)
            cycler["Cycles at (min)"].append(
                    self.cycles[row, "time_minutes"])
            cycler["Cycle lengths (min)"].append(
                    self.cycle_lengths[row-1] if row > 0 else -1)
            cycler["Average cycle length (min)"].append(
                    self.average_cycle_length if self.average_cycle_length is not None else 0)
            cycler["Cell size at first g1 (fl)"].append(
                    self.size_at_first_g1)
            cycler["Sizes at bud (fl)"].append(self.sizes_at_buds[row])
            cycler["Lineage"].append(self.lineage)
        cycle_data = pl.DataFrame(cycler, 
                                  schema = {
                                      "ID": pl.Int16,
                                      "Cycles at (min)": pl.Float64,
                                      "Cycle lengths (min)": pl.Float64,
                                      "Average cycle length (min)": pl.Float64,
                                      "Cell size at first g1 (fl)": pl.Float64,
                                      "Sizes at bud (fl)": pl.Float64,
                                      "Lineage": pl.String
                                      })
        return cycle_data

    def get_cycles(self):
        return (self.cell_df.lazy()
                .unique(subset=["generation_num", "cell_cycle_stage"])
                .filter(c("cell_cycle_stage") == "S")
                .sort(c("frame_i"))
                .collect()
                )

    def get_cycle_lengths(self):
        return (self.cycles.lazy()
                .with_columns(cycle_length=c("time_minutes").diff())
                .drop_nulls()
                .collect()
                .get_column("cycle_length")
                )

    def get_average_cycle_length(self):
        return self.cycle_lengths.mean()

    def get_lineage(self):
        return self.cell_df.get_column("relationship")[0]

    def get_size_at_first_G1(self):
        # may throw a value error if the cell has not finished budding.
        if self.get_lineage() == "bud":
            return (self.cell_df.lazy()
                    .unique("cell_cycle_stage")
                    .filter(c("cell_cycle_stage") == "G1")
                    .collect()
                    .get_column("cell_vol_fl").item()
                    )
        else: 
            return -1

    def save_csv(self):
        if self.cycles.shape[0] > 0:
            self.cycle_data = self.save_data()
            self.cycle_data.write_csv(self.cycles_dir / f"Cell_{self.id}.csv")

