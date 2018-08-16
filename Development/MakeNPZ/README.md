# Converting FITS files to NPZ file

  Our goal here is to manipulate data and convert into a more manageable format, so we can do more rigirous analysis later on
  in the pipeline. 
  
  Specifically, this script takes in 2 FITS files **(specifically from the Arecibo Telescope)**, combines them, unpacks the data
  from 8 bit to 4 bit data, manipulates the data array correctly by time vs frequency, and then saves the resulting data array into 
  an npz file along with headers(subint and primary headers). The resulting npz file is **ALWAYS** written to disc as **combined_dynamic_spectra.npz**
  
  ### Some Notes
  
  We have to combine Arecibo data files because their split their telescope into 2 subbands, A upper and lower band, each covering a different frequency range. 
  They record data for each subband as a seperate file, so if we want to look at dynamic spectra for all of the frequencies Arecibo covers, we need to combine both files
  into one coherent file. 
  
  The data is packed to save space by storing 2 4 bit numbers as one 8 bit number, so to get to the real data we need to unpack it.
  
  # How to Use the NPZ file
  The resulting npz file has three variables: "dynamic_spectra", "primary_header", "subint_header". 
  The "dynamic_spectra" variable contains the numpy array with the full resolution data. 
  The other two contain a dictionary of information about the data. 
  In order to load these, You can use these following steps:
  
      npzfile = np.load("combined_dynamic_spectra.npz") #loads the npz file
      variable = npzfile[<varible_name>] #where the <varible_name> is one of the three listed above
 
 ### How to Access Header Information
 
 I put header information into a dictionary and then put that into an array, so that we can work with only an npz file.
 You can access it by:
 
    npzfile = np.load("combined_dynamic_spectra.npz")
    #if you want the primary header
    variable = npzfile["primary_header"][0] (need to just access the only element in the array to access the dictionary)
    
    #if you want the subint header
    variable = npzfile["subint_header"][0] (need to just access the only element in the array to access the dictionary)
  
  -**Shiva Lakshmanan**  
   **May 2018**
  
