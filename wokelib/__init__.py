from woke.development.core import Address, Account


def get_address(a: Account | Address | str) -> Address:
    """if a has an address property, that value is returned
        if not, a is returned.
    Args:
        a (Account | Address | str):

    Returns:
        _type_: _description_
    """
    addr = getattr(a, "address", None)
    if addr is not None:
        return addr
    if isinstance(a, Address):
        return a 
    return Address(a)


MAX_UINT = 2**256 - 1


from .collector import JsonCollector
from .mirror import Mirror
