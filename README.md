#### Installation instructions

Download the file:
```git clone https://www.github.com/dtzibell/cell-size-analysis```

Edit ```config.ini```:
- ```ResultsDirectory``` is the location where post-processed single cell data is saved.
- ```OutputDirectory``` is the location where the data from all experiments is saved. Keep as is if ```ResultsDirectory``` is okay.

If you do not have uv, install via ```pip install uv```.

- Run the following commands in the command line:
    - ```uv sync``` $\Rightarrow$ sets up the project environment.
    - ```uv run main.py``` $\Rightarrow$ runs the script.
