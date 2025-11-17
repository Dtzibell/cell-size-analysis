from PyQt6.QtWidgets import QApplication, QFileDialog
import sys
import pathlib
import matplotlib.pyplot as plt
from CellGraph import CellGraph

def save_fig(cg: CellGraph, saving_dir: pathlib.Path):
    cg.fig.tight_layout()
    cg.fig.savefig(saving_dir / f"Cell_{cg.id}.png")
    plt.close()

def select_files():
    default_dir = pathlib.Path().cwd()
    app = QApplication(sys.argv)
    # output: [0] list of paths as strings, [1] type of files as string (ex. "*.csv")
    selected_files, _ = QFileDialog.getOpenFileNames(
        None,
        "Select your data's .csv",
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
    saving_dir = saving_dir / pathlib.Path(file_path).stem / "Figures"
    saving_dir.mkdir(parents=True, exist_ok=True)
    return saving_dir

def gather_input():
    IMAGING_RATE = float(input("Imaging rate: ").strip())
    EXPERIMENT_LENGTH = float(input("Experiment length: ").strip())
    return IMAGING_RATE, EXPERIMENT_LENGTH
