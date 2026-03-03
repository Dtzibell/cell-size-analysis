from collections import defaultdict
import polars as pl
from polars import col as c
from src.CellGraph import CellGraph
from src import utils
import configparser
from pathlib import Path

if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read("config.ini")
    results_directory = Path(config["PATHS"]["ResultsDirectory"])
    # results_directory = pathlib.Path(r"/home/tauras/Desktop/Results") # <--- change this (for Windows ex.: C://xxxx/xxxx)
    # files = utils.select_files()
    files = ["20250819_PM021_PM024_Stat_to_Glc_s02_acdc_output_cells_WT.csv"]

    dfs = []
    for file in files:
        # set up saving directories and create a cell id array to iterate over
        FILE_DIR = utils.setup_dir(results_directory, file)
        full_df = (pl
                   .scan_csv(file, infer_schema_length=50000)
                   .select([
                       "time_minutes",
                       "frame_i",
                       "Cell_ID",
                       "cell_vol_fl",
                       "cell_cycle_stage",
                       "relationship",
                       "generation_num"
                       ])
                    .collect()
                   )
        

        experiment_length = full_df[full_df.height - 1, "frame_i"]

        minutes = full_df.unique(c("time_minutes")).sort(c("time_minutes"))
        imaging_rate = minutes[1, "time_minutes"] - minutes[0, "time_minutes"]

        # MEDIUM_SWITCH = (
        #     float(input(
        #         f"Enter the time point of of the medium switch for file {FILE_DIR.name} (min): "
        #         ))
        #     / imaging_rate
        # )
        MEDIUM_SWITCH = 20

        cell_IDs = (
            full_df
            .unique(c("Cell_ID"))
            .get_column("Cell_ID")
            .sort()
        )

        partitioned_df = full_df.partition_by("Cell_ID", as_dict=True)


        total_cells = cell_IDs.shape[0]
        bud_sizes = defaultdict(list)
        ind = 0
        for id in cell_IDs:
            ind += 1
            if ind % 100 == 0:
                print(f"Proceeding with cell {ind}/{total_cells}")
            cg = CellGraph(
                id, partitioned_df[(id,)], FILE_DIR, imaging_rate, experiment_length, MEDIUM_SWITCH
            )
            cg.graph_cell_size()
            cg.graph_cycles()
            cell_cycler = cg.save_csv()
        dfs.append(utils.save_final_CSV(cg.cycles_dir))

    concat_df = pl.DataFrame()
    for df in dfs:
        concat_df = pl.concat([concat_df, df])

    concatPath = Path(input("Enter name of concatenated file: ") + ".csv")
    concat_df.write_csv(Path(config["PATHS"]["OutputDirectory"]) / concatPath)
