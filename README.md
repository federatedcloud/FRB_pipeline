# FRB_pipeline
A customizable scientific software pipeline for detecting, categorizing, and viewing single pulse candidates that may be Fast Radio Burst (FRB) sources in Radio Astronomy data.

------------------

## Pipeline Components

### Configuration Files (Including [Templates](https://github.com/federatedcloud/FRB_pipeline/tree/master/Pipeline/Templates#templates))

### [Methods](https://github.com/federatedcloud/FRB_pipeline/tree/master/Pipeline/Methods#methods)

Method files are typically short python 3 files that take in a dictionary from the pipeline and return a dictionary to the pipeline when completed.  In-between, they perform any necessary setup of variables, parameters, etc. to be able to run the module file, and then call the module file.  If any dictionary values are changed during the execution of the module, and you want the pipeline to use these changes going forward, you will need to return the values to the dictionary before passing it back.

### [Modules](https://github.com/federatedcloud/FRB_pipeline/tree/master/Pipeline/Modules#modules)

### Pipeline Setup
`pipeline.py`, parser, and other components for setting up and running the pipeline.

---

### [Modulation_Index](https://github.com/federatedcloud/FRB_pipeline/tree/master/Modulation_Index)

A ~python 3~ python 2 re-write (needs to be written for python 3) of the [modulation index](https://github.com/federatedcloud/modulation_index#modulation_index) functionality from the [PALFA2 pipeline](https://github.com/federatedcloud/transients_pipeline2#transients_pipeline2) as modified by Laura Spitler.

