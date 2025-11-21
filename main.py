from collections import defaultdict
import pathlib
import polars as pl
from polars import col as c
import matplotlib as mpl
from CellGraph import CellGraph
import utils

if __name__ == "__main__":
    mpl.rcParams["figure.figsize"] = (10, 5)
    mpl.rcParams["figure.dpi"] = 300
    results_directory = pathlib.Path(r"/home/tauras/Desktop/Results") # <--- change this (for Windows ex.: C://xxxx/xxxx)

    IMAGING_RATE, EXPERIMENT_LENGTH, MEDIUM_SWITCH = utils.gather_input()

    # necessary to be able to start any qtwidget.
    files = utils.select_files()

    for file in files:
        # set up saving directories and create a cell id array to iterate over
        FILE_DIR = utils.setup_dir(results_directory, file)
        full_df = pl.read_csv(file, infer_schema_length=50000)
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
            print(f"Proceeding with cell {ind}/{total_cells}")
            cell_df = full_df.filter(c("Cell_ID") == id)
            cg = CellGraph(
                id, cell_df, FILE_DIR, IMAGING_RATE, EXPERIMENT_LENGTH, MEDIUM_SWITCH
            )
            cg.initialize_graph()
            cg.graph_cell_size()
            cg.graph_medium_switch()
            cg.graph_cycles()
            lineage = cg.get_lineage()
            first_g1_frame = cg.get_first_G1_frame()
            cg.save_csv()
            cg.save_fig()
        cycles_dir = cg.cycles_dir
        utils.save_final_CSV(cycles_dir)
