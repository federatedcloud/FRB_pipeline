# rsw_pipeline

Robert Wharton's pipeline as adapted from the [PALFA2 pipeline](https://github.com/federatedcloud/transients_pipeline2#transients_pipeline2) streamlined to search for single pulses.  This includes the ability to turn on/off various pieces of functionality via the `pipe_params.py` file.

#### This pipeline includes the ability to run the `PRESTO` commands:
* `rfifind`
* `prepsubband`
* `accelsearch`
* `single_pulse_search`

There is also a modified version of `single_pulse_search` in the form of `mod_sp.py`, which outputs 8 values (instead of 5) to the output file. These are needed for modulation index calculation, but this pipeline does not currently do the calculation.
