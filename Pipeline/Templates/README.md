### Table of Contents
* [Templates](#templates)
    * [default.cfg](https://github.com/federatedcloud/FRB_pipeline/tree/master/Pipeline/Templates#defaultcfg)
    * [simpleFOF.cfg](https://github.com/federatedcloud/FRB_pipeline/tree/master/Pipeline/Templates#simplefofcfg)
    * [spitler.cfg](https://github.com/federatedcloud/FRB_pipeline/tree/master/Pipeline/Templates#spitlercfg)
* [How to Create a New Configuration File](https://github.com/federatedcloud/FRB_pipeline/tree/master/Pipeline/Templates#how-to-create-a-new-configuration-file)

# Templates

These template configuration files are intended to give examples for running the FRB pipeline with various [methods](https://github.com/federatedcloud/FRB_pipeline/tree/master/Pipeline/Methods) and parameter settings.  The following template configuration files are provided:
## default.cfg
If no configuration file is provided as an input when the pipeline is called, the pipeline will run this file.  It is **recommended** that this file *never be edited*, but kept as a reference.  Regardless of which processing steps you choose, this configuration file includes all of the basic components of the pipeline that you will likely need in order to process your data and search for Fast Radio Bursts.

The following methods are called using this configuration file:
* [combine_mocks](https://github.com/federatedcloud/FRB_pipeline/tree/master/Pipeline/Methods#included-methods)
* [fits2npz](https://github.com/federatedcloud/FRB_pipeline/tree/master/Pipeline/Methods#included-methods)

When you look at the file, it should be immediately apparent to you that there is a `[data]` section that is not a "method" and that there is no `[fits2npz]` method.  Please see [How to Create a New Configuration File](https://github.com/federatedcloud/FRB_pipeline/tree/master/Pipeline/Templates#how-to-create-a-new-configuration-file) for a full explanation.

## simpleFOF.cfg


## spitler.cfg


# How to Create a New Configuration File

The configuration file format is a `.cfg` and follows the supported INI file structure as defined in the [python documentation](https://docs.python.org/3.7/library/configparser.html#supported-ini-file-structure).  Some other resources that may be helpful to you as you create your configuration file are the [python ConfigParser documentation](https://docs.python.org/3.7/library/configparser.html) (which is the parser used in the pipeline), and a few [ConfigParser Examples](https://wiki.python.org/moin/ConfigParserExamples).  Understanding how ConfigParser works may be useful to you as well if you intend to [create a new module]() or [create a new method]().  In particular, [interpolation of values](https://docs.python.org/3.7/library/configparser.html#interpolation-of-values) is a useful feature. 

## The `[data]` Section

[PSRFITS documentation](https://www.atnf.csiro.au/research/pulsar/psrfits_definition/Psrfits.html)
