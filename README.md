#### Installation instructions

Download the file:
```git clone https://www.github.com/dtzibell/cell-size-analysis```

Edit ```config.ini```:
- ```ResultsDirectory``` is the location where post-processed single cell data is saved.
- ```OutputDirectory``` is the location where the data from all experiments is saved. Keep as is if ```ResultsDirectory``` is okay.

If you do not have uv, install via ```pip install uv```. \
Run ```uv run main.py``` $\Rightarrow$ runs the script.

#### CSV schema
The output file contains the following columns:
- "ID": ID of the cell
- "Cycles at (min)": The minute values at which the cell has begun its S phase.
- "Cycle lengths (min)": The length of each cycle. It is calculated as first order difference of rows (row2-row1, row3-row2, etc.). This means that the first row has no value, because the history is not known. The first row is thus set to -1.
- "Average cycle length (min)". The value is identical for each row of the cell.
- "Cell size at first g1 (fl)": The cell size of the cell at the first g1 after finishing budding. Mother cells do not have this information, so the value is set to -1. The value is identical for each row of the cell.
- "Sizes at bud (fl)": The cell size at the beginning of S phase. The first S phase of bud cells is their birth, so the size is very small, and most likely should be disregarded.
