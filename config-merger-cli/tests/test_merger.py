import pytest
from config_merger_cli.merger import parse_strategy, deep_merge


class TestMerger:
    @pytest.mark.parametrize(
        "strat_str, dicts, lists",
        [
            ("lists=append,dicts=merge", "merge", "append"),
            ("dicts=replace,lists=union", "replace", "union"),
            ("lists=prepend", "merge", "prepend"),
            ("lists=replace,dicts=replace", "replace", "replace"),
        ],
    )
    def test_parse_strategy(self, strat_str: str, dicts: str, lists: str):
        assert parse_strategy(strat_str) == (dicts, lists)

    def test_parse_strategy_invalid(self):
        with pytest.raises(ValueError, match="Invalid dicts strat"):
            parse_strategy("dicts=invalid")
        with pytest.raises(ValueError, match="Unknown key"):
            parse_strategy("foo=bar")

    def test_deep_merge_lists_append(self):
        target = {'l': [1, 2]}
        source = {'l': [3, 4]}
        deep_merge(target, source, ('merge', 'append'))
        assert target['l'] == [1, 2, 3, 4]

    def test_deep_merge_lists_prepend(self):
        target = {'l': [2, 3]}
        source = {'l': [0, 1]}
        deep_merge(target, source, ('merge', 'prepend'))
        assert target['l'] == [0, 1, 2, 3]

    def test_deep_merge_lists_union(self):
        target = {'l': [1, 2, 2]}
        source = {'l': [2, 3, 4]}
        deep_merge(target, source, ('merge', 'union'))
        assert target['l'] == [1, 2, 3, 4]

    def test_deep_merge_lists_replace(self):
        target = {'l': [1, 2]}
        source = {'l': [3, 4]}
        deep_merge(target, source, ('merge', 'replace'))
        assert target['l'] == [3, 4]

    def test_deep_merge_dicts(self):
        target = {'d': {'a': 1, 'b': 2}}
        source = {'d': {'b': 3, 'c': 4}}
        deep_merge(target, source, ('merge', 'append'))
        assert target['d'] == {'a': 1, 'b': 3, 'c': 4}

    def test_deep_merge_nested(self):
        target = {'app': {'db': {'host': 'loc'}}}
        source = {'app': {'debug': True, 'db': {'port': 5432}}}
        deep_merge(target, source, ('merge', 'append'))
        assert target == {'app': {'db': {'host': 'loc', 'port': 5432}, 'debug': True}}

    def test_deep_merge_dicts_replace(self):
        target = {'d': {'a': 1}}
        source = {'d': {'b': 2}}
        deep_merge(target, source, ('replace', 'append'))
        assert target['d'] == {'b': 2}

    def test_merge_type_mismatch_override(self):
        target = {'key': [1]}
        source = {'key': {'new': 2}}
        deep_merge(target, source, ('merge', 'append'))
        assert target['key'] == {'new': 2}