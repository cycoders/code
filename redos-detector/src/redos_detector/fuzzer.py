import re
import time
import random
import string
from typing import Dict, List
from concurrent.futures import ThreadPoolExecutor, TimeoutError


class Fuzzer:
    """
    Genetic fuzzer for ReDoS detection.

    Evolves strings to maximize Python `re.fullmatch` time under timeout.
    """

    def __init__(self, pattern: str, timeout: float = 0.1) -> None:
        self.pattern = pattern
        self.compiled = re.compile(pattern)
        self.timeout = timeout
        self.charset = string.ascii_letters + string.digits + r"(){}[]|?*+.-^$\"

    def match_time(self, s: str) -> float:
        """Measure fullmatch time with timeout. Returns >timeout on timeout."""
        def target() -> None:
            self.compiled.fullmatch(s)

        start_time = time.time()
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(target)
            try:
                future.result(timeout=self.timeout)
                return time.time() - start_time
            except TimeoutError:
                return self.timeout + 1.0

    def generate_initial(self, length: int) -> str:
        """Generate repeat-heavy initial string (e.g., aaaabbbb)."""
        s = []
        while len(s) < length:
            char = random.choice(self.charset)
            reps = random.randint(3, 15)
            s.append(char * reps)
        return "".join(s)[:length]

    def mutate(self, s: str) -> str:
        """Mutate: repeat sub, insert repeats, flip/append."""
        if random.random() < 0.4:
            # Repeat random sub
            if len(s) < 2:
                return s
            i = random.randint(0, len(s) // 2)
            j = random.randint(i + 1, len(s))
            sub = s[i:j]
            pos = random.randint(0, len(s))
            return s[:pos] + sub * random.randint(2, 6) + s[pos:]
        elif random.random() < 0.7:
            # Insert repeat char
            pos = random.randint(0, len(s))
            char = s[pos - 1] if pos > 0 else random.choice(self.charset)
            reps = random.randint(3, 12)
            return s[:pos] + char * reps + s[pos:]
        else:
            # Append or change
            if random.random() < 0.5 and len(s) > 0:
                pos = random.randint(0, len(s) - 1)
                return s[:pos] + random.choice(self.charset) + s[pos + 1 :]
            else:
                return s + random.choice(self.charset) * random.randint(2, 8)

    def crossover(self, s1: str, s2: str) -> str:
        """Simple split crossover."""
        min_len = min(len(s1), len(s2))
        if min_len < 2:
            return s1
        split = random.randint(1, min_len - 1)
        return s1[:split] + s2[split:]

    def fuzz(self, max_generations: int = 50, population_size: int = 100) -> Dict:
        """
        Run GA fuzzer.

        Returns {'vulnerable': bool, 'max_time': float, 'worst_input': str, 'gens': int}
        """
        max_len = 10000
        population: List[str] = []

        # Initial population: repeat-biased, varying lengths
        for _ in range(population_size):
            length = random.randint(20, 200)
            population.append(self.generate_initial(length))

        best_score = 0.0
        best_input = ""

        for gen in range(max_generations):
            # Evaluate
            scores = [self.match_time(s) for s in population]
            max_score_idx = scores.index(max(scores))
            if scores[max_score_idx] > best_score:
                best_score = scores[max_score_idx]
                best_input = population[max_score_idx]

            if best_score > self.timeout * 10:
                return {
                    "vulnerable": True,
                    "max_time": best_score,
                    "worst_input": best_input,
                    "gens": gen,
                }

            # Evolve
            paired = list(zip(scores, population))
            paired.sort(reverse=True)
            survivors = [p[1] for p in paired[: population_size // 2]]

            new_population = survivors[:]
            while len(new_population) < population_size:
                p1 = random.choice(survivors)
                p2 = random.choice(survivors)
                child = self.crossover(p1, p2)
                child = self.mutate(child)
                if len(child) > max_len:
                    child = child[-max_len:]
                new_population.append(child)

            population = new_population

        vuln = best_score > self.timeout * 5
        return {
            "vulnerable": vuln,
            "max_time": best_score,
            "worst_input": best_input,
            "gens": max_generations,
        }
