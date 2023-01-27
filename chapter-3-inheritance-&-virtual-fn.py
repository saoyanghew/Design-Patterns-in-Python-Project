import numpy as np

# define the base payoff class

class PayOff:
    def __init__(self):
        pass

    def calculate_payoff(self, spot):
        return 0

## define the inherited Vanilla options classes (call and put)

class PayOffCall(PayOff):
    def __init__(self, strike):
        self._strike = strike
    
    def get_strike(self):
        return self._strike
    
    def calculate_payoff(self, spot):
        return max(self._strike - spot, 0)

class PayOffPut(PayOff):
    def __init__(self, strike):
        self._strike = strike
    
    def get_strike(self):
        return self._strike
    
    def calculate_payoff(self, spot):
        return max(spot - self._strike, 0)

# define inherited class using case when
def option_matching(option, strike):
    match option:
        case "call":
            return PayOffCall(strike)
        case "put":
            return PayOffPut(strike)
        case _:
            raise ValueError("Unknown option type found!")

def simple_mc_main_3(strike, option, expiry, spot, vol, r, paths):

    # define required variables
    variance = expiry * vol ** 2
    std_dev = np.sqrt(variance)
    ito_correct = -0.5 * variance
    moved_spot = spot * np.exp(r * expiry + ito_correct)
    running_sum = 0

    # define inherited class using case when
    payoff = option_matching(option, strike)

    # perform required computation
    for i in range(paths):
        this_spot = moved_spot * np.exp(std_dev * np.random.normal(0, 1, 1))
        running_sum += payoff.calculate_payoff(this_spot)

    # return price of the option
    mean = running_sum / paths
    mean *= np.exp(-r*expiry)
    return print(mean)

# test
simple_mc_main_3(7, "call", 10, 1, 2, 0.01, 5)

## adding a more complex option type as an inherited class
## strike is now a list

class PayOffDoubleDigital(PayOff):
    def __init__(self, strike):
        self._lower = strike[0]
        self._upper = strike[1]
    
    def calculate_payoff(self, spot):
        if (self._lower <= spot <= self._upper): 
            return 0
        else:
            return 1

## redefine option_matching
def option_matching(option, strike):
    match option:
        case "call":
            return PayOffCall(strike)
        case "put":
            return PayOffPut(strike)
        case "double_digital":
            return PayOffDoubleDigital(strike)
        case _:
            raise ValueError("Unknown option type found!")

## test
simple_mc_main_3((2, 5), "double_digital", 10, 1, 2, 0.01, 5)
