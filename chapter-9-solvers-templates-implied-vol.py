import numpy as np
import scipy.stats as stats
import copy as cp

# 1. introduction

## goal - find the value of the volatility such that BS = quoted price
## robust - bisection 
## fast - Newton-Raphson

# 2. function objects

## implement a reusable function object is better than a solver base class

class BSCall:

    def __init__(self, r, d, T, spot, strike):
        self._r = r
        self._d = d
        self._T = T
        self._spot = spot
        self._strike = strike
    
    def __call__(self, vol):

        d1 = (np.log(self._spot / self._strike) + (self._r + 0.5 * vol ** 2) * self._T) / (vol * np.sqrt(self._T))
        d2 = (np.log(self._spot / self._strike) + (self._r - 0.5 * vol ** 2) * self._T) / (vol * np.sqrt(self._T))

        return (self._spot * np.exp(-self._d * self._T) * stats.norm.cdf(d1, 0, 1) - 
                self._strike * np.exp(-self._r * self._T) * stats.norm.cdf(d2, 0, 1))

black_scholes_call = BSCall(0.1, 0.01, 100, 50, 10)
black_scholes_call(5)

# 3. bisecting with a template

## create the bisection function

def bisection(target, low, high, tolerance, function):
    
    x = 0.5 * (low + high)
    y = function(x)

    while abs(y - target) > tolerance:
        if y < target:
            low = x

        elif y > target:
            high = x
        
        x = 0.5 * (low + high)
        y = function(x)
    
    return x

## example of an implied-volatility function

black_scholes_call = BSCall(0.1, 0.01, 100, 50, 10)
bisection(black_scholes_call(5), 0.1, 10, 1e-6, black_scholes_call)

# 4. Newton-Raphson and function template arguments

def NewtonRaphson(target, start, tolerance, value, derivative):
    y = value(start)
    x = start

    while abs(y - target) > tolerance:
        d = derivative(x)
        x += (target - y) / d
        y = value(x)

    return x

## this requires a new BS function to be called

class BSCallv2(BSCall):
    
    def __init__(self, r, d, T, spot, strike):
        super().__init__(r, d, T, spot, strike)
        self._r = r
        self._d = d
        self._T = T
        self._spot = spot
        self._strike = strike
    
    def vega(self, vol):
        d1 = (np.log(self._spot / self._strike) + (self._r + 0.5 * vol ** 2) * self._T) / (vol * np.sqrt(self._T))

        return self._spot * np.exp(-0.5 * d1 ** 2) * np.sqrt(self._T) / np.sqrt(2 * np.pi)

# 5. using Newton-Raphson to do implied volatilities

black_scholes_call = BSCallv2(0.1, 0.01, 100, 50, 10)

NewtonRaphson(black_scholes_call(5), 0.5, 1e-20, black_scholes_call, black_scholes_call.vega)
