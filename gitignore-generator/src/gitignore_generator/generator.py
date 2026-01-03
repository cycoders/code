from typing import List, Tuple
from .rules import COMMON_RULES, LANG_RULES, FRAMEWORK_RULES


def generate_gitignore_rules(
    languages: dict, frameworks: set, existing_content: str = ""
) -> List[Tuple[str, str]]:
    """Generate deduplicated rules categorized by source."""
    rule_sources: dict[str, str] = {}

    # Common
    for rule in COMMON_RULES:
        rule_sources[rule] = "common"

    # Languages
    for lang in languages:
        for rule in LANG_RULES.get(lang, []):
            rule_sources[rule] = f"lang/{lang}"

    # Frameworks
    for fw in frameworks:
        for rule in FRAMEWORK_RULES.get(fw, []):
            rule_sources[rule] = f"fw/{fw}"

    # Dedupe: keep first source
    rules_list = sorted([(cat, rule) for rule, cat in rule_sources.items()])

    # Filter new for updates (simple substring check)
    if existing_content:
        existing_lower = existing_content.lower()
        rules_list = [(cat, rule) for cat, rule in rules_list if rule.lower() not in existing_lower]

    return rules_list