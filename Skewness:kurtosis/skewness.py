from scipy.stats import skewnorm
from scipy.stats import kurtosis
import matplotlib.pyplot as plt
import numpy as np
import pylab as p
import scipy.stats as stats
import matplotlib.mlab as mlab


numValues = 10000
maxValue = 6
skewness = -2  # Negative values are left skewed, positive values are right skewed.
kurtosis_value = 0

random = skewnorm.rvs(a=skewness, loc=maxValue, size=numValues)  # Skewnorm function
#random = skewnorm.stats(k=kurtosis_value, axis=0, fisher=True, bias=True, nan_policy='propagate')

random = random - min(random)  # Shift the set so the minimum value is equal to zero.
random = random / max(random)  # Standadize all the vlues between 0 and 1.
random = random * maxValue  # Multiply the standardized values by the maximum value.

# Plot histogram to check skewness
plt.hist(random, 30, density=True, edgecolor='#8C2D19', facecolor='pink',  linewidth=2, alpha=1)
plt.xlabel('Week Day')
plt.ylabel('Probability')
plt.title('Skewness = -2 - Ticket Creation by week day')
plt.text(60, .025, r'$\mu=100,\ \sigma=15$')
plt.show()