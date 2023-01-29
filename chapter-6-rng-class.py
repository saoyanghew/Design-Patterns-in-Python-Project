# numpy already provides a lot of good reproducible tools that allow for:

import numpy as np
# setting seeds, using same and different random numbers based on purpose,
##

# we define an rng class for use in the subsequent chapters
# this allows for easy-to-use, reusable and adaptable code if the user intends
# to expand the rng class


class RandomNumberGenerator:
    def __init__(self, dimensions):
        self._dimensions = dimensions

    def reset_dimensions(self, new_dimensions):
        self._dimensions = new_dimensions


class GaussianRandomNumberGenerator(RandomNumberGenerator):
    def __init__(self, dimensions):
        super().__init__(dimensions)

    def get_gaussian(self):
        variates = np.random.normal(size=self._dimensions)
        return variates
