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
    files = utils.select_files()
    # files = ["20250819_PM021_PM024_Stat_to_Glc_s02_acdc_output_cells_WT.csv"]

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
                id, partitioned_df[(id,)], FILE_DIR
            )
            if cg.has_g1():
                cg.graph_cell_size()
                cg.graph_cycles()
                cell_cycler = cg.save_csv()
        dfs.append(utils.save_final_CSV(cg.cycles_dir))

    concat_df = pl.DataFrame()
    for df in dfs:
        concat_df = pl.concat([concat_df, df])

    concatPath = Path(input("Enter name of concatenated file: ") + ".xlsx")
    concat_df.write_excel(Path(config["PATHS"]["OutputDirectory"]) / concatPath,
        freeze_panes=(1, 0),
        autofit=True,
        autofilter=True,
        float_precision=5,
        header_format={"bold": True},
                          )
