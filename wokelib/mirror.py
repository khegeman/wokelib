from typing import Callable, Any, Tuple, TypeVar, List, Hashable, Dict

K = TypeVar('K', bound=Hashable)

class Mirror(Dict[K, Any]):
    """
    A class to mirror data of a remote contract exposed via a public mapping or array.
    Note: This implementation does not support nested mappings.

    Attributes:
        _method: The remote lookup method used to fetch data from the contract.
        K: The type of keys used in the mapping or array.

    Methods:
        bind(LookupMethod: Callable[..., Any])
            Binds the mirror to a remote lookup method with type hints.
        update()
            Updates local keys with remote values using the bound method.
        assert_eq()
            Verifies that local mirror matches remote data for all tracked keys.
        filter(f: Callable[[Tuple[K, Any]], bool]) -> List[Tuple[K, Any]]
            Filters and returns a list of key-value pairs using the given filter function.
    """

    def bind(self, LookupMethod: Callable[..., Any]):
        """
        Bind the mirror to a remote lookup method.

        Args:
            LookupMethod: The remote lookup method.
        """
        self._method = LookupMethod


    def update(self):
        """
        Update local keys with remote values using the bound method.
        """
        for k in self:
            self[k] = self._method(k)

    def assert_eq(self):
        """
        Verify that local mirror matches remote data for all tracked keys.

        Raises:
            AssertionError: If any local value does not match its remote counterpart.
        """
        for k in self:
            local = self[k]
            remote = self._method(k)
            assert local == remote

    def filter(self, f: Callable[[Tuple[K, Any]], bool]) -> List[Tuple[K, Any]]:
        """
        Filter and return a list of key-value pairs using the given filter function.

        Args:
            f (Callable[[Tuple[K, Any]], bool]): The filter function.

        Returns:
            List[Tuple[K, Any]]: Filtered key-value pairs.
        """
        return [(k, self[k]) for k in self if f((k, self[k]))]
