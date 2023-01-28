import numpy as np
import copy as cp

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

class PayOff:
    def __init__(self, strike):
        self._strike = strike

    def calculate_payoff(self, spot):
        return spot - spot

class PayOffCall(PayOff):
    def __init__(self, strike):
        self._strike = strike

    def get_strike(self):
        return self._strike

    def calculate_payoff(self, spot):
        return max(self._strike - spot, 0)

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

class PayOffBridge:
    def __init__(self, payoff):
        self._payoff = payoff

    # memory management functions
    def __del__(self):
        del self._payoff

    def deepcopy(self, inner_payoff):
        self._payoff = cp.deepcopy(inner_payoff)

    # linking back to payoff calculations
    def calculate_payoff(self, spot):
        return self._payoff.calculate_payoff(spot)

# 1. differing outputs

# MC functions up to now
# no indication of simulation's convergence

# develop OO routine - takes in statistics specification and outputs statistics
# strategy pattern - using a class to decide how an algorithm is implemented

# 2. designing a statistics gatherer

# routine should include 2 items - data, output

# ABC - null statistic gatherer

# a. null result
# b. actual results - object of output, en route/only once?

# create base class mc_statistics

class mc_statistics:
    def __init__(self):
        # base class
        pass

    def dump_one_result(self):
        return 0

    def get_results_so_far(self):
        return 0

    def deepcopy(self):
        # base class
        pass

    def __del__(self):
        # base class
        pass

# create mean class that calculates the mean

class mc_mean(mc_statistics):
    def __init__(self):
        self._running_sum = 0
        self._current_paths = 0

    def get_results_so_far(self):
        results = [[0]]
        results[0][0] = self._running_sum / self._current_paths
        return results

    def dump_one_result(self, result):
        self._current_paths += 1
        self._running_sum += result

    def deepcopy(self):
        return cp.deepcopy(self)

    def __del__(self):
        del self

# 3. using the statistics gatherer

## define a new mc function with gatherer check
def simple_mc_main_5(option, spot, parameters, paths, stats_gather):

    # define required variables
    vol = Parameters(parameters[0])
    r = Parameters(parameters[1])
    expiry = option.get_expiry()
    variance = vol.integral_square(0, expiry)
    std_dev = np.sqrt(variance)
    ito_correct = -0.5 * variance
    moved_spot = spot * np.exp(r.integral(0, expiry) + ito_correct)
    discounting = np.exp(-r.integral(0, expiry))

    for i in range(paths):
        this_spot = moved_spot * np.exp(std_dev * np.random.normal(0, 1, 1))
        stats_gather.dump_one_result(discounting * option.calculate_payoff(this_spot))

# call and print the results - mean in this case
gatherer = mc_mean()
simple_mc_main_5(VanillaOption(30, PayOffCall(7)), 5, [2, 0.1], 10000, gatherer)

results = gatherer.get_results_so_far()

for i in range(len(results)):
    for j in range(len(results[i])):
        print(results[i][j])

# 4. templates and wrappers

## not too important in Python - as it does not have pointers

# 5. convergence table

## summary statistics can be provided just using simple_mc_main_5

class mc_convergence(mc_statistics):
    def __init__(self, inner):
        self._inner = inner
        self._results_so_far = []
        self._stopping_point = 2
        self._current_paths  = 0

    def deepcopy(self):
        return cp.deepcopy(self)
    
    def dump_one_result(self, result):
        self._inner.dump_one_result(result)
        self._current_paths += 1

        if self._current_paths == self._stopping_point:
            self._stopping_point *= 2
            current_result = self._inner.get_results_so_far()

            for i in range(len(current_result)):
                current_result[i].append(self._current_paths)
                self._results_so_far.append(current_result[i])

    def get_results_so_far(self):

        temp = self._results_so_far

        if self._current_paths * 2 != self._stopping_point:
            current_result = self._inner.get_results_so_far()

            for i in range(len(current_result)):
                current_result[i].append(self._current_paths)
                temp.append(current_result[i])
        
            return temp

gatherer = mc_mean()
gatherer_v2 = mc_convergence(gatherer)

simple_mc_main_5(VanillaOption(30, PayOffCall(7)), 5, [2, 0.1], 10000, gatherer_v2)

results = gatherer_v2.get_results_so_far()

for i in range(len(results)):
    for j in range(len(results[i])):
        print(results[i][j])

# 6. decorations

## add functionality to a class without changing its interface - decorator
