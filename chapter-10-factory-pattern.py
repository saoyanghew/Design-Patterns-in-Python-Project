# 1. the problem

## conversion routine to go from strings, strikes to pay-offs. 
## factory pattern - ensures open-closed principle is not violated

# 2. the basic idea

## global variables
## auxiliary variables help with registering pay-off class to the factory

# 3. the singleton pattern - creating the factory

class PayOffFactory:
    def __init__(self):
        self._the_creator_functions = {}

    def register_payoff(self, payoff, creator_function):
        self._the_creator_functions[payoff] = creator_function
    
    def create_payoff(self, payoff, strike):
        if payoff not in self._the_creator_functions.keys():
            print(f'{payoff} is unknown!')
            return None
        else:
            return self._the_creator_functions[payoff](strike)

# 5. automatic registration

class PayOffHelper:
    def __init__(self, payoff_id, payoff):
        self._payoff = payoff
        payoff_factory.register_payoff(payoff_id, self.create)
    
    def create(self, strike):
        return self._payoff(strike)

# 6. using the factory

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

global payoff_factory

payoff_factory = PayOffFactory()

register_call = PayOffHelper("call", PayOffCall)

call_payoff = payoff_factory.create_payoff("call", 5)

if call_payoff != None:
    print(f'the payoff is {call_payoff(3)}')

    del call_payoff
