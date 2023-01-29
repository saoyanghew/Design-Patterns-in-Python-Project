import numpy as np
import copy as cp

# include required classes - improvement, using __call__ in place of
# calculate_payoff


class RandomNumberGenerator:
    def __init__(self, dimensions):
        self._dimensions = dimensions

    def reset_dimensions(self, new_dimensions):
        self._dimensions = new_dimensions


class GaussianRandomNumberGenerator(RandomNumberGenerator):
    def __init__(self, dimensions):
        super().__init__(dimensions)

    def get_gaussian(self, variates):
        variates = np.random.normal(size=self._dimensions)
        return variates


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

    def __call__(self, spot):
        return spot - spot


class PayOffCall(PayOff):
    def __init__(self, strike):
        self._strike = strike

    def get_strike(self):
        return self._strike

    def __call__(self, spot):
        return max(self._strike - spot, 0)


class VanillaOption:
    def __init__(self, expiry, payoff):
        self._expiry = expiry
        self._payoff = payoff

    def get_expiry(self):
        return self._expiry

    def get_payoff(self):
        return self._payoff

    def __call__(self, spot):
        return self._payoff(spot)


class PayOffBridge:
    def __init__(self, payoff):
        self._payoff = payoff

    # memory management functions
    def __del__(self):
        del self._payoff

    def deepcopy(self, inner_payoff):
        self._payoff = cp.deepcopy(inner_payoff)

    # linking back to payoff calculations
    def __call__(self, spot):
        return self._payoff(spot)


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


class mc_convergence(mc_statistics):
    def __init__(self, inner):
        self._inner = inner
        self._results_so_far = []
        self._stopping_point = 2
        self._current_paths = 0

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


# 1. introduction

# investigate putting all components together
# price path-dependent exotic options

# 2. identify components

# generation of the stock price path
# generation of the cash flows given a stock price path - path-dependent exotic options class
# discounting and summing of cash flows
# average of prices over all paths - statistics gatherer

# 3. communication between components

# path generator - input time, output array of spot values
# accounting - input CFs time, generate vector, output array of cashflow
# discounted appropriately and summed - as an input of the statistics gatherer
# final results are obtained from the statistics gatherer after all required looping

# 4. base classes

# cash-flow and path-dependent classes to calculate and arrange CFs
# generic exotic engine class - to fit exotic asset classes and obtain paths

class CashFlow:
    def __init__(self, amount=0, time_index=0):
        self.amount = amount
        self.time_index = time_index


class PathDependent:
    def __init__(self, look_at_times):
        self._look_at_times = look_at_times

    def get_look_at_times(self):
        return self._look_at_times

    def max_cashflow_number(self):
        # base class
        pass

    def possible_cashflow_times(self):
        # base class
        pass

    def cash_flows(self, spot_values, generated_flows):
        # base class
        pass

    def deepcopy(self):
        return cp.deepcopy(self)

    def __del__(self):
        del self


class ExoticEngine:
    def __init__(self, product, r):
        self._product = product
        self._r = Parameters(r)
        self._discounts = self._product.possible_cashflow_times()

        for i in range(len(self._discounts)):
            self._discounts[i] = np.exp(-self._r.integral(0, self._discounts[i]))

        self._these_cash_flows = []
        for i in range(self._product.max_cashflow_number()):
            self._these_cash_flows.append(CashFlow())

    def get_one_path(self, spot_values):
        # base class
        pass

    def do_simulation(self, gatherer, paths):
        spot_values = self._product.get_look_at_times()

        self._these_cash_flows = []
        for i in range(self._product.max_cashflow_number()):
            self._these_cash_flows.append(CashFlow())

        for i in range(paths):
            self.get_one_path(spot_values)
            this_value = self.do_one_path(spot_values)
            gatherer.dump_one_result(this_value)

    def do_one_path(self, spot_values):
        number_flows = self._product.cash_flows(spot_values, self._these_cash_flows)
        value = 0

        for i in range(number_flows):
            value += self._these_cash_flows[i].amount * self._discounts[self._these_cash_flows[i].time_index]

        return value

    def __del__(self):
        del self


# 5. a Black-Scholes path generation engine - a specific exotic engine

# Black-Scholes engine - requires N(0,1) path and related transformations
# operator overload of what is initiated, and what getting one path means

class ExoticBSEngine(ExoticEngine):

    def __init__(self, product, vol, d, r, generator, spot):
        super().__init__(product, r)
        self._product = product
        self._vol = Parameters(vol)
        self._d = Parameters(d)
        self._r = Parameters(r)
        self._generator = generator
        times = self._product.get_look_at_times()
        self._number_of_times = len(times)
        self._discounts = self._product.possible_cashflow_times()

        for i in range(len(self._discounts)):
            self._discounts[i] = np.exp(-self._r.integral(0, self._discounts[i]))

        self._these_cash_flows = []
        for i in range(self._product.max_cashflow_number()):
            self._these_cash_flows.append(CashFlow())

        self._generator.reset_dimensions(self._number_of_times)
        self._drifts = np.zeros(self._number_of_times, float)
        self._std_dev = np.zeros(self._number_of_times, float)

        self._variance = self._vol.integral_square(0, times[0])
        self._drifts[0] = self._r.integral(0, times[0]) - self._d.integral(0, times[0]) - 0.5 * self._variance
        self._std_dev[0] = np.sqrt(self._variance)

        for i in range(1, self._number_of_times, 1):
            this_variance = self._vol.integral_square(times[i - 1], times[i])
            self._drifts[i] = self._r.integral(times[i - 1], times[i]) - self._d.integral(times[i - 1], times[i]) - 0.5 * this_variance
            self._std_dev[i] = np.sqrt(this_variance)

        self._log_spot = np.log(spot)
        self._variates = np.zeros(self._number_of_times, float)

    def get_one_path(self, spot_values):
        self._variates = self._generator.get_gaussian(self._variates)
        current_log_spot = self._log_spot

        for i in range(self._number_of_times):
            current_log_spot += self._drifts[i] + self._std_dev[i] * self._variates[i]
            spot_values[i] = np.exp(current_log_spot)

# 6. an arithmetic Asian option - a specific dependent path (PathDependent)


class PathDependentAsian(PathDependent):
    def __init__(self, look_at_times, delivery_time, payoff):
        super().__init__(look_at_times)
        self._delivery_time = delivery_time
        self._payoff = payoff
        self._number_of_times = len(look_at_times)

    def max_cashflow_number(self):
        return 1

    def possible_cashflow_times(self):
        temp = np.zeros(1)
        temp[0] = self._delivery_time
        return temp

    def cash_flows(self, spot_values, generated_flows):
        sum_ = np.sum(spot_values)
        mean_ = sum_ / self._number_of_times
        generated_flows[0].time_index = 0
        generated_flows[0].amount = self._payoff(mean_)
        return 1

# 7. putting them altogether

# since this is a rather complicated process of jumbling items together
# let's set the parameters *prior*


expiry = 10
strike = 7
spot = 5
vol = 2
r = 0.1
d = 1
paths = 100
dates = 10
payoff = PayOffCall(strike)
times = np.zeros(dates)

for i in range(len(times)):
    times[i] = (i + 1) * expiry / dates

option = PathDependentAsian(times, expiry, payoff)
gatherer = mc_mean()
gatherer_v2 = mc_convergence(gatherer)
generator = GaussianRandomNumberGenerator(dates)

engine = ExoticBSEngine(option, vol, d, r, generator, spot)

engine.do_simulation(gatherer_v2, paths)

results = gatherer_v2.get_results_so_far()

for i in range(len(results)):
    for j in range(len(results[i])):
        print(results[i][j])

## and this returns - the Asian option price using an exotic BS engine!
