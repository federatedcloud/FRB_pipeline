### Table of Contents
* [Templates](#templates)
    * [default.cfg](https://github.com/federatedcloud/FRB_pipeline/tree/master/Pipeline/Templates#defaultcfg)
    * [simpleFOF.cfg](https://github.com/federatedcloud/FRB_pipeline/tree/master/Pipeline/Templates#simplefofcfg)
    * [floodfill.cfg](https://github.com/federatedcloud/FRB_pipeline/tree/master/Pipeline/Templates#floodfillcfg)
    * [spitler.cfg](https://github.com/federatedcloud/FRB_pipeline/tree/master/Pipeline/Templates#spitlercfg)
* [How to Create a New Configuration File](https://github.com/federatedcloud/FRB_pipeline/tree/master/Pipeline/Templates#how-to-create-a-new-configuration-file)

# Templates

These template configuration files are intended to give examples for running the FRB pipeline with various [methods](https://github.com/federatedcloud/FRB_pipeline/tree/master/Pipeline/Methods) and parameter settings.  The following template configuration files are provided:
## default.cfg
If no configuration file is provided as an input when the pipeline is called, the pipeline will run this file.  It is **recommended** that this file *never be edited*, but kept as a reference.  Regardless of which processing steps you choose, this configuration file includes all of the basic components of the pipeline that you will likely need in order to process your data and search for Fast Radio Bursts.

The following methods are called using this configuration file:
* [combine_mocks](https://github.com/federatedcloud/FRB_pipeline/tree/master/Pipeline/Methods#included-methods)
* [fits2npz](https://github.com/federatedcloud/FRB_pipeline/tree/master/Pipeline/Methods#included-methods)

When you look at the file, it should be immediately apparent to you that there is a `[data]` section that is not a "method" and that there is no `[fits2npz]` method.  This is because...


## simpleFOF.cfg


## floodfill.cfg


## spitler.cfg


# How to Create a New Configuration File



