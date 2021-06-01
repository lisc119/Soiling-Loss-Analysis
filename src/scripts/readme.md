# Pipeline scripts

## Usage 
The majority of the functions used for the analyses showcased in the notebooks are available here are separate scripts.

The `run_pipeline` notebook demonstrates how to use these scripts for a single-function workflow or for running parts separately.

## The main pipeline

#### `run_pipeline.py` runs through:
- ##### Pre-processing the data via `process_data.py`
- ##### Filtering the data via `apply_filters.py`
- ##### And finally, estimating soiling via `estimate_soiling.py`

## Pipeline components

The first 2 steps can be further decomposed by their function.
*e.g. `apply_filters.py` implements `filter_strings.py` and `filter_times.py`.*

## Other

*`js_helper/` contains JavaScript script(s) used for the UMAP clustering interactive plot.*
