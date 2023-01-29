import numpy as np
import copy as cp
from dataclasses import dataclass


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

# 1. introduction

# similar to using MC - approximate on a risk-neutral expectation
# trees can be used to price American options better

# algorithm to price American options

# 1. create an array of spot values from -N to N
# 2. for each spot value create and store a pay-off
# 3. at the previous time slice, compute possible values of spots
# 4. for each spot, compute pay-off and take the maximum of the discounted value
# 5. repeat 3-4 until time 0.

# other pricing possibilities - barrier option that can be exercised at certain time periods

# 2. designing a tree

# concepts to think about - discretising, final payoff, rule for deciding option value

# 3. the TreeProduct class - base class of a product that uses a binomial tree


class TreeProduct:

    def __init__(self, final_time):
        self._final_time = final_time

    def deepcopy(self):
        return cp.deepcopy(self)

    def final_payoff(self, spot):
        # base class
        pass

    def pre_final_value(self, spot, time, discounted_future_value):
        # base class
        pass

    def get_final_time(self):
        return self._final_time

    def __del__(self):
        del self

# further definition of an american option tree or european option tree is required
# we have an American and a European tree


class TreeAmerican(TreeProduct):

    def __init__(self, final_time, payoff):
        super().__init__(final_time)

        self._final_time = final_time
        self._payoff = payoff

    def final_payoff(self, spot):
        return self._payoff(spot)

    def pre_final_value(self, spot, time, discounted_fv):
        return max(self._payoff(spot), discounted_fv)


class TreeEuropean(TreeProduct):

    def __init__(self, final_time, payoff):
        super().__init__(final_time)

        self._final_time = final_time
        self._payoff = payoff

    def final_payoff(self, spot):
        return self._payoff(spot)

    def pre_final_value(self, spot, time, discounted_fv):
        return discounted_fv

# 4. a tree class

# from Anguita, we need to define a pair class to mimic the tree:


@dataclass
class pair:
    first: float
    second: float


class SimpleBinomialTree:

    def __init__(self, spot, r, d, vol, steps, time):
        self._spot = spot
        self._r = Parameters(r)
        self._d = Parameters(d)
        self._vol = Parameters(vol)
        self._steps = steps
        self._time = time
        self._tree_built = False
        self._tree = []
        self._discounts = [0 for i in range(self._steps)]

    def build_tree(self):
        self._tree_built = True
        self._tree = [[] for i in range(self._steps + 1)]

        initial_log_spot = np.log(self._spot)

        for i in range(self._steps + 1):
            self._tree[i] = [pair(0, 0) for i in range(i + 1)]
            this_time = i * self._time / self._steps
            moved_log_spot = initial_log_spot + self._r.integral(0, this_time) - self._d.integral(0, this_time)
            moved_log_spot -= 0.5 * this_time * vol * vol
            std_dev = vol * np.sqrt(self._time / self._steps)

            k = 0
            for j in range(-i, i + 2, 2):
                self._tree[i][k].first = np.exp(moved_log_spot + j * std_dev)

        for l in range(self._steps):
            self._discounts[l] = np.exp(-self._r.integral(l * self._time / self._steps, (l + 1) * self._time / self._steps))

    def get_price(self, tree_product):
        if not self._tree_built:
            self.build_tree()

        if tree_product.get_final_time() != self._time:
            raise ValueError("mismatched product in simple binomial tree!")

        k = 0
        for j in range(-self._steps, self._steps + 2, 2):
            self._tree[self._steps][k].second = tree_product.final_payoff(self._tree[self._steps][k].first)
            k += 1

        for i in range(1, self._steps + 1, 1):
            index = self._steps - i
            this_time = index * self._time / self._steps

            k = 0
            for j in range(-index, index + 2, 2):
                spot = self._tree[index][k].first
                discounted_fv = 0.5 * self._discounts[index] * (self._tree[index + 1][k].second + self._tree[index + 1][k + 1].second)
                self._tree[index][k].second = tree_product.pre_final_value(spot, this_time, discounted_fv)

                k += 1

        return self._tree[0][0].second

# putting everything together


expiry = 0.5
strike = 7
spot = 5
vol = 2
r = 0.1
d = 1
steps = 400

payoff = PayOffCall(strike)

european_option = TreeEuropean(expiry, payoff)
american_option = TreeAmerican(expiry, payoff)

tree_used = SimpleBinomialTree(spot, r, d, vol, steps, expiry)

european_option_price = tree_used.get_price(european_option)
american_option_price = tree_used.get_price(american_option)

print(f'European option price = {european_option_price}')
print(f'American option price = {american_option_price}')
