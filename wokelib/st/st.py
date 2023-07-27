#Strategies for generating random data for flows

from typing import List, Any

import random
from woke.development.primitive_types import uint
from woke.testing.fuzzing import generators

from . import MAX_UINT


class Data():

    values = [] 

    def set(self, v):
        self.values = v
    def get(self):
        return self.values
    

def random_ints(len : int, min_val : uint=0, max_val : uint=MAX_UINT): 
    def f():
        return [generators.random_int(min_val, max_val) for i in range(0,len) ]
    return f


def random_addresses(len : int):
    def f():
        return [generators.random_address() for i in range(0,len) ]
    return f

def random_int(min : uint=0,max : uint=MAX_UINT,**kwargs):
    def f():
        return generators.random_int(min=min,max=max,**kwargs)
    return f

def random_float(min : float, max : float):
    def f():
        return random.uniform(min, max)
    return f

def choose(values : Data):
    def f():        
        return random.choice(values.get())
    return f
    
def random_bool(true_prob):
    def f():
        return generators.random_bool(true_prob=true_prob)
    return f

def choose_n(values, min_k, max_k):
    def f():
        
        return random.choices(values.get(),k=generators.random_int(min_k,max_k))
    return f
    
def random_bytes(min, max):
    def f():
        return generators.random_bytes(min,max)
    return f


