import pathlib
import polars as pl
from polars import col as c
import matplotlib as mpl
from CellGraph import CellGraph
import utils

if __name__ == "__main__":
    mpl.rcParams["figure.figsize"] = (10, 5)
    mpl.rcParams["figure.dpi"] = 300
    results_directory = pathlib.Path(r"/home/tauras/Desktop/Results")

    IMAGING_RATE, EXPERIMENT_LENGTH, MEDIUM_SWITCH = utils.gather_input()

    # necessary to be able to start any qtwidget.
    files = utils.select_files()

    for file in files:
        # set up saving directories and create a cell id array to iterate over
        figure_dir, cycles_dir = utils.setup_dir(results_directory, file)
        concat_dir = figure_dir.parent
        full_df = pl.read_csv(file, infer_schema_length=50000)
        cell_IDs = (
            full_df.unique(subset=["Cell_ID"]).select(c("Cell_ID")).sort(c("Cell_ID")).to_numpy().flatten()
        )
        total_cells = cell_IDs.shape[0]
        bud_size_at_first_g1 = []
        ind = 0
        for id in cell_IDs:
            ind += 1
            #print(f"Proceeding with cell {ind}/{total_cells}")
            cell_df = full_df.filter(c("Cell_ID") == id)
            cellgraph = CellGraph(id, cell_df, IMAGING_RATE, EXPERIMENT_LENGTH, MEDIUM_SWITCH)
            cellgraph.initialize_graph()
            cellgraph.graph_cell_size()
            cellgraph.graph_medium_switch()
            cellgraph.graph_cycles()
            lineage = cellgraph.get_lineage()
            first_g1_frame = cellgraph.get_first_G1_frame()
            print(lineage)
            if lineage == "bud":
                print(cellgraph.cycles)
            if lineage == "bud" and first_g1_frame > -1:
                bud_size_at_first_g1.append(cellgraph.get_size_at_(first_g1_frame))
                print(bud_size_at_first_g1)
            utils.save_csv(cellgraph, cycles_dir)
            utils.save_fig(cellgraph, figure_dir)
        utils.save_final_CSV(concat_dir, cycles_dir)
