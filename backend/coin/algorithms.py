from typing import List, Tuple

from coin.domain import InputInfo


def select_outputs_greedy(unspent: List[InputInfo], min_value) -> Tuple[List[InputInfo], float]:
    """
    Select optimal outputs for a send from unspent outputs list.
    Returns output list and remaining change to be sent to a change address.
    """
    # Partition into 2 lists.
    lessers = [utxo for utxo in unspent if utxo.amount < min_value]
    greaters = [utxo for utxo in unspent if utxo.amount >= min_value]
    key_func = lambda utxo: utxo.value
    if greaters:
        # Not-empty. Find the smallest greater.
        min_greater = min(greaters)
        change = min_greater.amount - min_value
        return [min_greater], change
    # Not found in greaters. Try several lessers instead.
    # Rearrange them from biggest to smallest. We want to use the least
    # amount of inputs as possible.
    lessers.sort(key=key_func, reverse=True)
    result = []
    accum = 0
    for utxo in lessers:
        result.append(utxo)
        accum += utxo.amount
        if accum >= min_value:
            change = accum - min_value
            return result, change
    # No results found.
    return [], 0
