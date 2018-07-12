# FRB_pipeline
Pipeline to search for FRBs

------------------

# Pipeline Components

## Previous Pipeline(s)

Code for the recreation of previous pipelines has been included in order to easily reproduce and compare results.

* **[rsw_pipeline](https://github.com/federatedcloud/FRB_pipeline/tree/master/rsw_pipeline#rsw_pipeline)** - Robert Wharton's pipeline as adapted from the [PALFA2 pipeline](https://github.com/federatedcloud/transients_pipeline2#transients_pipeline2) streamlined to search for single pulses.

* **[spitler_pipeline](https://github.com/federatedcloud/FRB_pipeline/blob/master/spitler_pipeline/README.md#spitler_pipeline)** - A complete re-production plus automation of the [PALFA2 pipeline as adapted by Laura Spitler](https://github.com/federatedcloud/transients_pipeline2#transients_pipeline2), but based on the condensed [rsw_pipeline](https://github.com/federatedcloud/FRB_pipeline/tree/master/rsw_pipeline#rsw_pipeline). This is including the adaptations made by Laura Spitler to calculate [modulation index](https://github.com/federatedcloud/modulation_index#modulation_index).

## Modulation_Index

A python 3 re-write of the [modulation index](https://github.com/federatedcloud/modulation_index#modulation_index) functionality from the [PALFA2 pipeline](https://github.com/federatedcloud/transients_pipeline2#transients_pipeline2) modified by Laura Spitler.
