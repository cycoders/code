from typing import Any, Dict, Tuple

ListStrat = str  # append|prepend|union|replace
DictStrat = str  # merge|replace
Strategy = Tuple[DictStrat, ListStrat]


def parse_strategy(strategy_str: str) -> Strategy:
    """Parse 'lists=append,dicts=merge' → ('merge', 'append')."""
    dicts_strat: DictStrat = 'merge'
    lists_strat: ListStrat = 'append'
    for part in strategy_str.split(','):
        if '=' not in part:
            raise ValueError(f"Invalid strategy part: {part!r}")
        key, val = part.split('=', 1)
        if key == 'dicts':
            if val not in ('merge', 'replace'):
                raise ValueError(f"Invalid dicts strat: {val!r}")
            dicts_strat = val
        elif key == 'lists':
            if val not in ('append', 'prepend', 'union', 'replace'):
                raise ValueError(f"Invalid lists strat: {val!r}")
            lists_strat = val
        else:
            raise ValueError(f"Unknown key: {key!r}")
    return (dicts_strat, lists_strat)


def deep_merge(target: Dict[str, Any], source: Dict[str, Any], strategy: Strategy) -> Dict[str, Any]:
    """Deep merge source into target (in-place). Preserves order."""
    dicts_strat, lists_strat = strategy

    for key, src_val in source.items():
        tgt_val = target.get(key)

        if tgt_val is not None:
            if (
                isinstance(tgt_val, dict)
                and isinstance(src_val, dict)
                and dicts_strat == 'merge'
            ):
                deep_merge(tgt_val, src_val, strategy)
                continue
            if (
                isinstance(tgt_val, list)
                and isinstance(src_val, list)
                and lists_strat != 'replace'
            ):
                if lists_strat == 'append':
                    tgt_val.extend(src_val)
                elif lists_strat == 'prepend':
                    tgt_val[0:0] = src_val
                elif lists_strat == 'union':
                    seen = set(tgt_val)
                    for item in src_val:
                        if item not in seen:
                            seen.add(item)
                            tgt_val.append(item)
                continue  # skip override

        target[key] = src_val

    return target