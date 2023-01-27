import numpy as np

def simple_mc_main_1(expiry, strike, spot, vol, r, paths):

    # define required variables
    variance = expiry * vol ** 2
    std_dev = np.sqrt(variance)
    ito_correct = -0.5 * variance
    moved_spot = spot * np.exp(r * expiry + ito_correct)
    this_spot = 0
    running_sum = 0

    # perform computation of running_sum
    for i in range(paths):
        this_gaussian = np.random.normal(0, 1, 1)
        this_spot = moved_spot * np.exp(std_dev * this_gaussian)
        this_payoff = np.max(this_spot - strike, 0)
        running_sum += this_payoff

    # calculate the price of the call option
    mean = running_sum / paths
    mean *= np.exp(-r * expiry)
    return print(mean)


simple_mc_main_1(5, 11, 100, 0.5, 0.1, 11)

# critique of the simple Monte Carlo

# simple straightforward procedural program
# not reusable
# not adaptable
# hard to extend this simple design
# extension requires some level of overhead - not ideal for maintenance

# identifying possible classes

# pay-off class
# statistics class
# terminator class
# rng class
# option property class
# variable parameter class

# benefits of using classes

# classes can encapsulate natural finance concepts
# reduces bugs
# clearer code
# separate interface from implementation
