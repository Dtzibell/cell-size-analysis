from PyQt6.QtWidgets import QApplication, QFileDialog
import sys
import pathlib
import polars as pl
from polars import col as c
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np

mpl.rcParams["figure.figsize"] = (10, 5)
mpl.rcParams["figure.dpi"] = 300


def select_files():
    default_dir = pathlib.Path().cwd()
    file_dialog = QFileDialog.getOpenFileNames(
        None,
        "Select your data's .csv",
        str(
            default_dir
        ),  # replace this line with string of your desired default directory
        "*.csv",
    )
    # print(file_dialog) # output: list: [0] list of paths as strings, [1] type of files as string (ex. "*.csv")
    selected_files = file_dialog[0]
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
    saving_dir = saving_dir / pathlib.Path(file_path).stem / "Figures"
    saving_dir.mkdir(parents=True, exist_ok=True)
    return saving_dir


if __name__ == "__main__":
    results_directory = pathlib.Path(r"/home/dtzi/Desktop/Results")
    IMAGING_RATE = 3
    EXPERIMENT_LENGTH = 139
    EXPERIMENT_DURATION = 139 * 3
    TICK_INTERVAL = 40
    app = QApplication(sys.argv)
    files = select_files()
    for file in files:
        saving_dir = setup_dir(results_directory, file)
        full_df = pl.read_csv(file, infer_schema_length=50000)
        cell_IDs = (
            full_df.unique(subset=["Cell_ID"]).select(c("Cell_ID")).to_numpy().flatten()
        )
        for id in cell_IDs:
            print(id)
            cell_df = full_df.filter(c("Cell_ID") == id)
            time_x = cell_df["time_minutes"]
            cell_size_vox = cell_df["cell_vol_fl"]
            fig, ax = plt.subplots()
            ax.plot(time_x, cell_size_vox, "k")
            fig.supylabel("cell volume [fl]")
            fig.supxlabel("time [min]")
            plt.xticks(
                np.arange(0, EXPERIMENT_DURATION, TICK_INTERVAL),
                rotation=90,
            )
            plt.tight_layout()
            plt.savefig(saving_dir / f"Cell_{id}.png")
            plt.close()
