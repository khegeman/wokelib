"""

Quick test of a different method for generating random data.  Could be integrated into woke proper

"""

from __future__ import annotations

import random
from collections import defaultdict
from typing import Callable, DefaultDict, List, Optional

from typing_extensions import get_type_hints
from woke.testing.fuzzing.generators import generate


from woke.testing.core import get_connected_chains
from woke.testing import fuzzing


class FuzzTest(fuzzing.FuzzTest):
    def run(
        self,
        sequences_count: int,
        flows_count: int,
        *,
        dry_run: bool = False,
    ):
        chains = get_connected_chains()

        flows: List[Callable] = self.__get_methods("flow")
        invariants: List[Callable] = self.__get_methods("invariant")

        for i in range(sequences_count):
            flows_counter: DefaultDict[Callable, int] = defaultdict(int)
            invariant_periods: DefaultDict[Callable[[None], None], int] = defaultdict(
                int
            )

            snapshots = [chain.snapshot() for chain in chains]
            self._flow_num = 0
            self._sequence_num = i
            self.pre_sequence()

            for j in range(flows_count):
                valid_flows = [
                    f
                    for f in flows
                    if (
                        not hasattr(f, "max_times")
                        or flows_counter[f] < getattr(f, "max_times")
                    )
                    and (
                        not hasattr(f, "precondition")
                        or getattr(f, "precondition")(self)
                    )
                ]
                weights = [getattr(f, "weight") for f in valid_flows]
                if len(valid_flows) == 0:
                    max_times_flows = [
                        f
                        for f in flows
                        if hasattr(f, "max_times")
                        and flows_counter[f] >= getattr(f, "max_times")
                    ]
                    precondition_flows = [
                        f
                        for f in flows
                        if hasattr(f, "precondition")
                        and not getattr(f, "precondition")(self)
                    ]
                    raise Exception(
                        f"Could not find a valid flow to run.\nFlows that have reached their max_times: {max_times_flows}\nFlows that do not satisfy their precondition: {precondition_flows}"
                    )
                flow = random.choices(valid_flows, weights=weights)[0]
                fp = {
                    k: getattr(type(self), k, None)()
                    if callable(getattr(type(self), k, None))
                    else generate(v)
                    for k, v in get_type_hints(flow, include_extras=True).items()
                    if k != "return"
                }

                flow_params = fp.values()

                self._flow_num = j
                self.pre_flow(flow)

                collector = getattr(self, "_collector", None)
                if collector is not None:
                    collector.collect(self, flow, **fp)

                flow(self, *flow_params)
                flows_counter[flow] += 1
                self.post_flow(flow)

                if not dry_run:
                    self.pre_invariants()
                    for inv in invariants:
                        if invariant_periods[inv] == 0:
                            isnapshots = []
                            # if changes that occur during checking the invariant are not to be committed take a snapshot
                            if hasattr(inv, "commit_changes") == False:
                                isnapshots = [chain.snapshot() for chain in chains]
                            self.pre_invariant(inv)
                            inv(self)
                            self.post_invariant(inv)

                            # restore any snapshots saved before the invariant
                            for snapshot, chain in zip(isnapshots, chains):
                                chain.revert(snapshot)

                        invariant_periods[inv] += 1
                        if invariant_periods[inv] == getattr(inv, "period"):
                            invariant_periods[inv] = 0
                    self.post_invariants()

            self.post_sequence()

            for snapshot, chain in zip(snapshots, chains):
                chain.revert(snapshot)
