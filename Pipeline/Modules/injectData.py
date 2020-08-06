import numpy as np
from plotnpz import plot_ds

'''
Quick method for injecting data into either existing an existing dataset or 
a generated one
'''

'Uncomment and replace the filename with the desired .npz file to inject data into'
#data = np.load('presentpreInject.npz')['arr_0'] 

'Generate a 2D numpy array of random numbers [0, 1] to represent noise'
data = np.random.rand(920, 15000)


data = data*9

'''
You can edit the ranges (which determine the frequency channels that each loop covers),
the slope of the pulse you create (the number multiplying i), the signal width (determined by 
the number of points you are reassigning in the second axis), and the signal value (the number 
you are assigning to the data point). Useful for testing FOF outputs such as DM, slope, SNR, etc.
'''

for i in range(700,800):
    data[i, 10000-10*i:10050-10*i]=8
for i in range(600,700):
    data[i, 10700-11*i:10750-11*i]=8
for i in range(500,600):
    data[i, 11300-12*i:11350-12*i]=8
for i in range(400,500):
    data[i, 11800-13*i:11850-13*i]=8
for i in range(300,400):
    data[i, 12200-14*i:12250-14*i]=8

np.savez('presentpostInject3.npz', data)
