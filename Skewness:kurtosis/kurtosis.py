import numpy as np
from scipy.stats import kurtosis
import matplotlib.pyplot as plt


min_range = 0
max_range = 6
midpoint = (max_range + min_range)/2
samples = 10000

x = np.linspace(min_range, max_range, samples)
ax = plt.subplot()

def filter_tails(x):
    return x[(x >= min_range) & (x <= max_range)]

runif = np.random.uniform(min_range, max_range, samples)
value = kurtosis(runif, fisher=False)
plt.title('Random Uniform')
#density = kurtosis.gaussian_kde(runif)
plt.hist(runif, 30, density=True, edgecolor='#8C2D19', facecolor='pink', linewidth=2, alpha=1)
#plt.plot(x, density(x))
plt.show()
print(f"uniform kurtosis = {value}")

sigma = 0.1
runif = np.random.normal(midpoint, sigma, samples)
value = kurtosis(runif, fisher=False)
plt.title('Normal Distribution')
plt.hist(runif, 30, density=True, edgecolor='#8C2D19', facecolor='pink', linewidth=2, alpha=1)
plt.show()
print(f"gaussian kurtosis = {value}")

exponential_decay = 0.001
runif = np.random.laplace(midpoint, exponential_decay, samples)
value = kurtosis(runif, fisher=False)
plt.title('Laplace')
plt.hist(runif, 30, density=True, edgecolor='#8C2D19', facecolor='pink', linewidth=2, alpha=1)
plt.show()
print(f"laplace kurtosis = {value}")
