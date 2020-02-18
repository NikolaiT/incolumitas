import numpy as np
import matplotlib.pyplot as plt

def uniform_and_normal():
	# plot uniform distribution
	X = np.random.uniform(low=0, high=1.0, size=1000)
	plt.subplot(1, 2, 1)
	count, bins, ignored = plt.hist(X, 20, facecolor='green') 
	plt.xlabel('X~U[0,1]')
	plt.ylabel('Count')
	plt.title("Uniform Distribution Histogram (20 Bins)")
	plt.axis([0, 1, 0, 100]) # x_start, x_end, y_start, y_end
	plt.grid(True)

	# plot normal distribution
	plt.subplot(1, 2, 2)
	X = np.random.normal(loc=0, scale=1, size=1000)
	count, bins, ignored = plt.hist(X, 20, facecolor='green') 
	plt.xlabel('X~N[0,1]')
	plt.ylabel('Count')
	plt.title("Normal Distribution Histogram (20 Bins)")
	plt.grid(True)

	# show both plots
	plt.show(block=True)

uniform_and_normal()