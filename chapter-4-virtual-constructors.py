import numpy as np

# redefine base class

class PayOff:
    def __init__(self, strike):
        self._strike = strike

    def calculate_payoff(self, spot):
        return spot - spot

# redefine the inherited Vanilla options classes (call and put)

class PayOffCall(PayOff):
    def __init__(self, strike):
        self._strike = strike

    def get_strike(self):
        return self._strike

    def calculate_payoff(self, spot):
        return max(self._strike - spot, 0)

# problem

## an option specification encompasses both the payoff and the expiry
## adding expiry into previous code - reusability breaks down
## store reference to a pay-off object rather than a pay-off  object

# solution 1

## define a VanillaOption class to be used in a new function specification

class VanillaOption:
    def __init__(self, expiry, payoff):
        self._expiry = expiry
        self._payoff = payoff
    
    def get_expiry(self):
        return self._expiry
    
    def get_payoff(self):
        return self._payoff
    
    def calculate_payoff(self, spot):
        return self._payoff.calculate_payoff(spot)


## new function specification does not require expiry

def simple_mc_main_3(option, spot, vol, r, paths):
    
    # define required variables
    expiry = option.get_expiry()
    variance = expiry * vol ** 2
    std_dev = np.sqrt(variance)
    ito_correct = -0.5 * variance
    moved_spot = spot * np.exp(r * expiry + ito_correct)
    running_sum = 0

    for i in range(paths):
        this_spot = moved_spot * np.exp(std_dev * np.random.normal(0, 1, 1))
        running_sum += option.calculate_payoff(this_spot)
    
    # return price of the option
    mean = running_sum / paths
    mean *= np.exp(-r * expiry)
    return print(mean)

# test
simple_mc_main_3(VanillaOption(20, PayOffCall(7)), 2, 2, 0.1, 30)

# the bridge

## get around the need to assign, construct, destruct
## workaround 1: use a wrapper class as a template
## workaround 2: use the bridge pattern - reduce clunkiness of VanillaOption

import copy as cp

## define PayOffBridge class to introduce memory management

class PayOffBridge:
    def __init__(self, payoff):
        self._payoff = payoff

    ## memory management functions
    def __del__(self):
        del self._payoff
    
    def deepcopy(self, inner_payoff):
        self._payoff = cp.deepcopy(inner_payoff)

    ## linking back to payoff calculations
    def calculate_payoff(self, spot):
        return self._payoff.calculate_payoff(spot)

simple_mc_main_3(VanillaOption(5, PayOffBridge(PayOffCall(7))), 5, 2, 0.1, 10)

# caveat - the bridge is slow
## compiler uses heaps to identify memory that is used and not used

# parameters class

## variable parameters so no need to specify volatility or interest in the
## mc function

### base class to be expanded upon by inherited subclasses of parameters
class ParametersInner:
    def __init__(self):
        # base class
        pass

    def integral(self, t1, t2):
        # base class
        pass

    def integral_square(self, t1, t2):
        # base class
        pass

class ParametersConstant(ParametersInner):
    def __init__(self, constant):
        self._constant = constant
        self._constant_square = constant * constant
    
    def integral(self, t1, t2):
        return (t2 - t1) * self._constant
    
    def integral_square(self, t1, t2):
        return (t2 - t1) * self._constant_square

class Parameters(ParametersConstant):
    def __init__(self, constant):
        super().__init__(constant)

    # new functions
    def root_mean_squared(self, t1, t2):
        total = self.integral_square(t1, t2)
        return total / (t2 - t1)

    def mean(self, t1, t2):
        total = self.integral(t1, t2)
        return total / (t2 - t1)

    def deepcopy(self, inner_parameters):
        cp.deepcopy(inner_parameters)

    def __del__(self):
        del self

## new function specification does not require parameters specification

def simple_mc_main_4(option, spot, parameters, paths):

    # define required variables
    vol = Parameters(parameters[0])
    r = Parameters(parameters[1])
    expiry = option.get_expiry()
    variance = vol.integral_square(0, expiry)
    std_dev = np.sqrt(variance)
    ito_correct = -0.5 * variance
    moved_spot = spot * np.exp(r.integral(0, expiry) + ito_correct)
    running_sum = 0

    for i in range(paths):
        this_spot = moved_spot * np.exp(std_dev * np.random.normal(0, 1, 1))
        running_sum += option.calculate_payoff(this_spot)
    
    mean = running_sum / paths
    mean *= np.exp(- r.integral(0, expiry))
    return print(mean)

# test
simple_mc_main_4(VanillaOption(5, PayOffCall(7)), 5, [2, 0.1], 10)
