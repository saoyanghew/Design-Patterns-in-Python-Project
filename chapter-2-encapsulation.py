import numpy as np

# creating the payoff class

class PayOff:
    def __init__(self, strike, option = "call"):
        """Create an instance of the payoff class"""
        self._strike = strike
        self._option = option
    
    def get_strike(self):
        return self._strike

    def get_option(self):
        return self._option
    
    def calculate_payoff(self, spot):
        match self._option:
            case "call":
                return max(self._strike - spot, 0)
            case "put":
                return max(spot - self._strike, 0)
            case _:
                raise ValueError("Unknown option type found!")

# creating the simple Monte Carlo model using the PayOff class

def simple_mc_main_2(payoff, expiry, spot, vol, r, paths):

    # define required variables
    variance = expiry * vol ** 2
    std_dev = np.sqrt(variance)
    ito_correct = -0.5 * variance
    moved_spot = spot * np.exp(r * expiry + ito_correct)
    running_sum = 0

    # perform required computation
    for i in range(paths):
        this_spot = moved_spot * np.exp(std_dev * np.random.normal(0, 1, 1))
        running_sum += payoff.calculate_payoff(this_spot)

    # return price of the option
    mean = running_sum / paths
    mean *= np.exp(-r*expiry)
    return print(mean)

# test
callpayoff = PayOff(7, "call")
simple_mc_main_2(callpayoff, 10, 1, 2, 0.01, 5)

putpayoff = PayOff(7, "put")
simple_mc_main_2(putpayoff, 10, 1, 2, 0.01, 5)

# further extensibility defects

## cannot add new features without needing to recompile related files

# explaining the open-closed principle

## code should always be open for extension, but closed for modification
## the above PayOff class does not allow for many complexities
## e.g. double digital options with 2 strike prices are not allowed
## inheritance and virtual functions solve this problem
