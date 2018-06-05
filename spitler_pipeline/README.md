# spitler_pipeline

A complete re-production of the PALFA2 pipeline as adapted by Laura Spitler, but based on the **rsw_pipeline**.  The `params.py` file is modified to turn on/off functionality, including the new features.

#### Added functionality:
* `mod_sp.py` - utilizes the modified `single_pulse_search`
* `maskdata` - this is based on the `PRESTO` version called `prepdata,` but with a modification in `backend_common.c` to write the masked dynamic spectra.
* `mod_index` - does the setup and running of the `palfa_calc_mi.c` modulation index calculation

#### To Be Added Soon
* Plots - at the end of a run to show candidates for human inspection
* `combine_mocks` - combines the upper and lower subbands into one `.fits` file

CHANGE
