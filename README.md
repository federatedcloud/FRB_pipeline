# FRB_pipeline
A customizable scientific software pipeline written in python3 for detecting, categorizing, and viewing single pulse candidates that may be Fast Radio Burst (FRB) sources in Radio Astronomy data.

------------------

# Quick-Start Guide

## How To Use The Pipeline

### Running
You can run the pipeline either by issuing `./pipeline.py` or with `python pipeline.py`.  Either method requires including the [configuration file](#configuration-files) as a positional argument and running from the [Pipeline directory](https://github.com/federatedcloud/FRB_pipeline/tree/master/Pipeline) (or including the path to it).  Here's a simple example:

`$ ./pipeline.py Templates/hello_world.cfg`

If no configuration file is included, then the [`default.cfg`](https://github.com/federatedcloud/FRB_pipeline/tree/master/Pipeline/Templates#defaultcfg) template will be used.  To get help, use `-h`.

### Basic Structure
#### Methods
A **[method](https://github.com/federatedcloud/FRB_pipeline/tree/master/Pipeline/Methods#methods)** is essentially a task for the pipeline to perform.  Each method consists of a single python file that is named to reflect what it does, followed by `_method.py`, and is stored in the [Methods directory](https://github.com/federatedcloud/FRB_pipeline/tree/master/Pipeline/Methods).  For example, the "Hello World!" method file is named [`hello_world_method.py`](https://github.com/federatedcloud/FRB_pipeline/blob/master/Pipeline/Methods/hello_world_method.py).  

In order to run a method, it must be specified in the cofiguration file you choose when you run the pipeline.  Simple methods are self-contained, but larger or more complex methods use supporting [modules](#modules).  There are several [existing methods](https://github.com/federatedcloud/FRB_pipeline/blob/master/Pipeline/Methods/README.md#included-methods) to choose from, some of which call functions from underlying modules.

#### Configuration Files
A configuration file (`.cfg`) is all that is needed to run the pipeline with existing methods.  This file specifies which methods you would like to perform *and* all of the necessary or desired parameters, inputs, directory locations, etc. for those methods.  A method is specified by name as a section key without the `_method` part of the name.  For example, to run the "Hello World!" method, your configuration file must include `[hello_world]`.

Configuration files support comments following the `;` or `#` characters.  When the configuration file is read by the pipeline, these comments and any trailing spaces (on the left or right side) will be removed before key-value pairs are stored in a dictionary.

#### Modules


#### Data and Results


## How To Add Your Own Code/Methods


---
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

