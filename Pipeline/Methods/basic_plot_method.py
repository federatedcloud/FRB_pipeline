from method import *
from basic_plot import *


def main(hotpotato):
    print("Running basic plotter.")
    
    arr = get_value(hotpotato, 'fof_plot')
    basic_plot_go(arr)
    return hotpotato


