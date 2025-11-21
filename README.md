Download the .zip from the **<> code** interface

#### Before running the script:
- Open the file ```utils.py```. Go to the end of the file and adjust the variable IMAGING_RATE, EXPERIMENT_LENGTH and MEDIUM_SWITCH. I think their meaning is clear. If these parameters are changing from experiment to experiment, comment the variable definitions and uncomment the input lines.
- Open the file ```main.py``` and adjust the directory where you want the results to be saved. (```pathlib.Path(r"<>")``` on line 20)
- Run the following commands in the command line:
    - ```pip install uv```  -> installs https://docs.astral.sh/uv/, a modern python project manager.
    - ```uv sync``` -> sets up the project environment.
    - ```uv run main.py``` -> runs the programme.

Always run ```main.py``` via ```uv run main.py```.
