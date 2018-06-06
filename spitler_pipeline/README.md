# spitler_pipeline

A complete re-production of the [PALFA2 pipeline as adapted by Laura Spitler](https://github.com/federatedcloud/transients_pipeline2#transients_pipeline2), but based on the condensed [rsw_pipeline](https://github.com/federatedcloud/FRB_pipeline/tree/master/rsw_pipeline#rsw_pipeline).  The `params.py` file is modified to turn on/off functionality, including the new features.  The `dspec.py` file is now called `make_plots.py` with added features.

#### Added functionality:
* `mod_sp.py` - utilizes the modified `single_pulse_search`
* `maskdata` - this is based on the `PRESTO` version called `prepdata,` but with a modification in `backend_common.c` to write the masked dynamic spectra.
* `mod_index` - does the setup and running of the `palfa_calc_mi.c` modulation index calculation
* `make_plots.py` - adds ability to plot a few types of graphs for singlepulse candidates, including color, greyscale, and reverse greyscale.

#### To Be Added Soon
* `combine_mocks` - combines the upper and lower subbands into one `.fits` file
* Plots - at the end of a run to show each candidate that meets a certain criteria (such as below modulation index threshold) for human inspection
