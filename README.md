# FRB_pipeline
Pipeline to search for FRBs

------------------

# Pipeline Components

## Modulation_Index

A re-write of the `palfa_calc_mi.c` functionality from the PALFA2 pipeline in python 3.

## Previous Pipeline(s)

Code for the recreation of previous pipelines has been included in order to easily reproduce and compare results.

### rsw_pipeline

Robert Wharton's pipeline as adapted from the PALFA2 pipeline.  This includes the ability to turn on/off various pieces of functionality via the `pipe_params.py` file.

#### This pipeline includes the ability to run the `PRESTO` commands:
* `rfifind`
* `prepsubband`
* `accelsearch`
* `single_pulse_search`

There is also a modified version of `single_pulse_search` in the form of `mod_sp.py`, which outputs 8 values (instead of 5) to the output file. These are needed for modulation index calculation, but this pipeline does not currently do the calculation.

### spitler_pipeline

A complete re-production of the PALFA2 pipeline as adapted by Laura Spitler, but based on the **rsw_pipeline**.  The `params.py` file is modified to turn on/off functionality, including the new features.

#### Added functionality:
* `mod_sp.py` - utilizes the modified `single_pulse_search`
* `maskdata` - this is based on the `PRESTO` version called `prepdata,` but with a modification in `backend_common.c` to write the masked dynamic spectra.
* `mod_index` - does the setup and running of the `palfa_calc_mi.c` modulation index calculation

#### To Be Added Soon
* Plots - at the end of a run to show candidates for human inspection
* `combine_mocks` - combines the upper and lower subbands into one `.fits` file


