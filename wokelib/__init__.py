def getAddress(u):
    addr = getattr(u, "address", None)
    if addr is not None:
        return addr

    return u


from .collector import collector
from .printer import print_steps
from .given import given
