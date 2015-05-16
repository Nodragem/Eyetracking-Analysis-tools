__author__ = 'c1248317'

from cleaning import ProgressBar
import matplotlib.pyplot as plt
#plt.show(block=False)

pr = ProgressBar("Bonjour",value_max=1600, pos=(0, 200))
for i in range(1600):
    pr.step(1)


