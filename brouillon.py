import numpy as np

l1 = np.arange(120).reshape((2,3,4,5))
l2 = np.linspace(0, 1, 120).reshape((2,3,4,5))

np.round(l1, 2)

np.add(l1, l2, out=l2)

print(l2)