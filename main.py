from collections import defaultdict
import polars as pl
from polars import col as c
import matplotlib as mpl
from src.CellGraph import CellGraph
from src import utils
import configparser
from pathlib import Path

if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read("config.ini")
    results_directory = Path(config["PATHS"]["ResultsDirectory"])
    mpl.rcParams["figure.figsize"] = (10, 5)
    mpl.rcParams["figure.dpi"] = 300
    # results_directory = pathlib.Path(r"/home/tauras/Desktop/Results") # <--- change this (for Windows ex.: C://xxxx/xxxx)
    files = utils.select_files()

    dfs = []
    for file in files:
        # set up saving directories and create a cell id array to iterate over
        FILE_DIR = utils.setup_dir(results_directory, file)
        full_df = pl.read_csv(file, infer_schema_length=50000)

        experiment_length = full_df[full_df.height-1, "frame_i"]
        minutes = full_df.unique(c("time_minutes")).sort(c("time_minutes"))
        imaging_rate = minutes[1, "time_minutes"] - minutes[0, "time_minutes"]
        MEDIUM_SWITCH = float(input(f"Enter the time point of of the medium switch for file {FILE_DIR.name} (min): ")) / imaging_rate

        cell_IDs = (
            full_df.unique(subset=["Cell_ID"])
            .select(c("Cell_ID"))
            # .sort(c("Cell_ID")) # uncomment if want sorted looping
            .to_numpy()
            .flatten()
        )

        total_cells = cell_IDs.shape[0]
        bud_sizes = defaultdict(list)
        ind = 0
        for id in cell_IDs:
            ind += 1
            if ind%10 == 0:
                print(f"Proceeding with cell {ind}/{total_cells}")
            cell_df = full_df.filter(c("Cell_ID") == id)
            cg = CellGraph(
                id, cell_df, FILE_DIR, imaging_rate, experiment_length, MEDIUM_SWITCH
            )
            # cg.initialize_graph()
            cg.graph_cell_size()
            # cg.graph_medium_switch()
            cg.graph_cycles()
            lineage = cg.get_lineage()
            first_g1_frame = cg.get_first_G1_frame()
            cg.save_csv()
            # cg.save_fig()
        dfs.append(utils.save_final_CSV(cg.cycles_dir))

    concat_df = pl.DataFrame()
    for df in dfs:
        concat_df = pl.concat([concat_df, df])
    
    concatPath = Path(input("Enter name of concatenated file: ") + ".csv")
    concat_df.write_csv(Path(config["PATHS"]["OutputDirectory"]) / concatPath)
