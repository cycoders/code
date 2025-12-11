import pandas as pd
import hashlib
from typing import Optional
from faker import Faker

from .patterns import PII_TYPE_FAKER_MAP
from .types import AnonymizeMode


class Anonymizer:
    def __init__(self, mode: AnonymizeMode, salt: Optional[str] = None, faker_seed: Optional[int] = None):
        self.mode = mode
        self.salt = salt
        self.faker = Faker()
        if faker_seed:
            self.faker.seed_instance(faker_seed)

    def anonymize_series(self, series: pd.Series, mask: pd.Series, pii_types: pd.Series) -> pd.Series:
        result = series.copy()

        if self.mode == AnonymizeMode.REDACT:
            result[mask] = "***" * (len(result[mask].str[0]) // 3 + 1)[:len(result[mask].str[0])]
            return result

        for idx in mask[mask].index:
            ptype = pii_types[idx]
            if self.mode == AnonymizeMode.FAKE:
                faker_method = PII_TYPE_FAKER_MAP.get(ptype, "name")
                result[idx] = getattr(self.faker, faker_method)()
            elif self.mode == AnonymizeMode.HASH:
                h = hashlib.sha256()
                h.update((str(series[idx]) + (self.salt or '')).encode())
                result[idx] = h.hexdigest()[:len(str(series[idx]))]

        return result
