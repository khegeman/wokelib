"""

Replacement for woke fuzz test that drives a corpus replay. 

The fundamental difference is that flows are not randomized but instead are run in sequence based on data loaded from json.

"""

from __future__ import annotations

import random
from collections import defaultdict
from typing import Callable, DefaultDict, List, Optional

from typing_extensions import get_type_hints

from .st import sequences

from woke.testing.core import get_connected_chains
from woke.testing import fuzzing


class FuzzTest(fuzzing.FuzzTest):
    def __get_methods_dict(self, attr: str) -> Dict[Callable]:
        ret = {}
        for x in dir(self):
            if hasattr(self.__class__, x):
                m = getattr(self.__class__, x)
                if hasattr(m, attr) and getattr(m, attr):
                    ret[x] = m
        return ret

    def run(
        self,
        sequences_count: int,
        flows_count: int,
        *,
        dry_run: bool = False,
    ):
        chains = get_connected_chains()

        flows: Dict[Callable] = self.__get_methods_dict("flow")
        invariants: List[Callable] = self.__get_methods("invariant")

        sequences_count = len(list(sequences))

        for i in range(sequences_count):
            flows_counter: DefaultDict[Callable, int] = defaultdict(int)
            invariant_periods: DefaultDict[Callable[[None], None], int] = defaultdict(
                int
            )

            snapshots = [chain.snapshot() for chain in chains]
            self._flow_num = 0
            self._sequence_num = i
            self.pre_sequence()

            flows_count = len(list(sequences.get(str(i))))

            for j in range(flows_count):
                flow_name = sequences.get(str(i)).get(str(j)).get("name")
                flow = flows.get(flow_name)
                self._flow_num = j
                self.pre_flow(flow)
                flow(self, {})
                flows_counter[flow] += 1
                self.post_flow(flow)

                if not dry_run:
                    self.pre_invariants()
                    for inv in invariants:
                        if invariant_periods[inv] == 0:
                            self.pre_invariant(inv)
                            inv(self)
                            self.post_invariant(inv)

                        invariant_periods[inv] += 1
                        if invariant_periods[inv] == getattr(inv, "period"):
                            invariant_periods[inv] = 0
                    self.post_invariants()

            self.post_sequence()

            for snapshot, chain in zip(snapshots, chains):
                chain.revert(snapshot)
