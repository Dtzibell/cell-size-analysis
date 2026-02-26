from PyQt6.QtWidgets import QApplication, QFileDialog
import sys
import pathlib
import polars as pl


def save_final_CSV(cycles_dir: pathlib.Path):
    # Files with the min-max indeces in the columns
    all_files = pathlib.Path(cycles_dir).glob("*.csv")
    # Concatenate all csv with index values for Whi5 min and max
    csvs = []
    for f in all_files:
        try:
            df = pl.read_csv(
                f,
                schema={
                    "ID": pl.Int16,
                    "Cycles at (min)": pl.Int16,
                    "Cycle lengths (min)": pl.Float32,
                    "Average cycle length (min)": pl.Float32,
                    "Cell size at first g1 (min)": pl.Float32,
                    "Sizes at bud (fl)": pl.Float32,
                    "Lineage": pl.String,
                },
            )
            csvs.append(df)
        except pl.exceptions.NoDataError:
            pass
    # TODO: applies to cell 24 of the WT dataset - the dataframe is correct, however
    # when concatenated inserts values that should not exist there. 
    df_index = pl.concat(csvs)

    df_sorted = df_index.sort(["ID", "Cycles at (min)"])
    df_sorted.write_csv(
        cycles_dir.parent / "All.csv", separator=","
    )  # index=False gives same results as line 14 (reset index)
    return df_sorted

def select_files():
    default_dir = pathlib.Path().cwd()
    app = QApplication(sys.argv)
    # output: [0] list of paths as strings, [1] type of files as string (ex. "*.csv")
    selected_files, _ = QFileDialog.getOpenFileNames(
        None,
        "Select your data (.csv's)",
        str(
            default_dir
        ),  # replace this line with string of your desired default directory
        "CSV files (*.csv)",
        options=QFileDialog.Option.DontUseNativeDialog,
    )

    # for path in file_dialog[0]:
    #     selected_files.append(pathlib.Path(path)) # creates a list of pathlib.Paths with selected files
    # for visual representation of selection (GUI)
    # if len(file_dialog[0])>1:
    #     file_names = ""
    #     for i in range(len(file_dialog[0])):
    #         if i == 0:
    #             parent_path = f"{pathlib.Path(file_dialog[0][i]).parents[0]}"
    #             file_path = f"{pathlib.Path(file_dialog[0][i]).name}"
    #             file_names += f"{parent_path} \n {file_path}"
    #         else:
    #             file_path = f"{pathlib.Path(file_dialog[0][i]).name}"
    #             file_names += f"\n {file_path}"
    #     file_path = file_names
    # else:
    #     path_to_file = pathlib.Path(file_dialog[0][0])
    #     file_path = f"{str(path_to_file)}"
    return selected_files


def setup_dir(saving_dir: pathlib.Path, file_path: str):
    file_dir = saving_dir / pathlib.Path(file_path).stem
    file_dir.mkdir(parents=True, exist_ok=True)
    return file_dir


def gather_input():
    # IMAGING_RATE = float(input("Imaging frequency (min): ").strip())
    # EXPERIMENT_LENGTH = float(input("Experiment length: ").strip())
    # MEDIUM_SWITCH = int(input("Medium switch at frame: ").strip())

    IMAGING_RATE = 3.0
    EXPERIMENT_LENGTH = 139
    MEDIUM_SWITCH = 20
    return IMAGING_RATE, EXPERIMENT_LENGTH, MEDIUM_SWITCH
