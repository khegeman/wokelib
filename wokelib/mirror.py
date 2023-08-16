from typing import Hashable
from typing import get_type_hints


class Mirror:
    # mirrors data of a remote contract that is exposed via a public mapping or array
    # currently doesn't support nested mappings

    def bind(self, LookupMethod):
        # must have type hints - all pytypes bindings do
        hints = list(get_type_hints(LookupMethod).items())
        assert len(hints) > 0
        self._method = LookupMethod
        self._key_type = hints[0][1]
        self._keys = []
        self._values = {}

    def __len__(self):
        return len(self._keys)

    def keys(self):
        return self._keys

    def insert_key(self, key):
        if not key in self._keys:
            self._keys.append(key)

    def delete_key(self, key):
        self._keys.remove(key)
        self._values.__delitem__(key)

    def items(self):
        # returns key in the correct type
        return [(k, self.__getitem__(k)) for k in self._keys]

    def update(self):
        # update all local keys with remote values
        for k in self._keys:
            self.__setitem__(k, self._method(k))

    def assert_eq(self):
        # verify that local mirror matches remote data for all tracked keys
        for k in self._keys:
            local = self.__getitem__(k)
            remote = self._method(k)
            assert local == remote

    def __getitem__(self, key):
        # bytes32 and some other types aren't hashable.  convert non hashable to hex
        assert isinstance(key, self._key_type)
        hkey = key if isinstance(key, Hashable) else hex(key)
        return self._values.__getitem__(hkey)

    def __setitem__(self, key, val):
        # bytes32 and some other types aren't hashable.  convert non hashable to hex
        assert isinstance(key, self._key_type)
        hkey = key if isinstance(key, Hashable) else hex(key)
        self._values.__setitem__(hkey, val)

    def filter(self, f):
        return list(filter(f, self.items()))
