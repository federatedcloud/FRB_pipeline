# Methods


## Included Methods
* **`basic_plot`** - plots masked dynamic spectra at locations of interest.
* **`combine_mocks`** - combines 2 `.fits` files from Arecibo data.
* **`decimate`** - decimation and smoothing.
* **`fil2npz`** - converts a `.fil` file to a `.npz` file and optionally stores it to disk.
* **`fits2npz`** - converts a `.fits` file to a `.npz` file and optionally stores it to disk.
* **`FOF`** - performs the Friends-Of-Friends algorithm.
* **`hello_world`** - prints "Hello World!" as an ***example*** of how to set up a method file; optionally change `print_count` in `Templates/hello_world.cfg` and then run pipeline with that configuration file.
* **`prepsubband`** - performs `prepsubband` from [PRESTO](https://www.cv.nrao.edu/~sransom/presto/).
* **`results`** - organizes output files into whichever location is specified with `output_directory` in config file for the specified filetypes (i.e. `move_txt_files` with move all `.txt` files output from the pipeline).
* **`rfifind`** - performs `rfifind` from [PRESTO](https://www.cv.nrao.edu/~sransom/presto/).
* **`sps`** - performs `single_pulse_search` from PRESTO.
* **`modulation_index`** - (*coming soon*) performs the [modulation index](https://github.com/federatedcloud/modulation_index#modulation_index) functionality from the [PALFA2 pipeline](https://github.com/federatedcloud/transients_pipeline2#transients_pipeline2) as modified by Laura Spitler.



## How to Create a New Method

There are three major steps in order to create a new method that can be run in the pipeline:
1. [Create a module](https://github.com/federatedcloud/FRB_pipeline/tree/master/Pipeline/Modules#how-to-create-a-new-module)
2. [Create a configruation file](https://github.com/federatedcloud/FRB_pipeline/tree/master/Pipeline/Templates#how-to-create-a-new-configuration-file)
3. [Create a method file](#the-method-file)

### The Method File


### Running the New Method

