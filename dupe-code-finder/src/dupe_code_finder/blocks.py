from typing import List

from .models import CodeBlock
from .tokenizer import TokenPos


def extract_blocks(
    path: "Path",
    norm_tokens: List[TokenPos],
    lines: List[str],
    min_size: int,
    step: int,
) -> List[CodeBlock]:
    """
    Extract overlapping token blocks from normalized tokens.
    """
    blocks = []
    for start_idx in range(0, len(norm_tokens) - min_size + 1, step):
        end_idx = start_idx + min_size
        block_tokens = [tok[0] for tok in norm_tokens[start_idx:end_idx]]
        token_str = " ".join(block_tokens)
        start_line = norm_tokens[start_idx][1]
        end_line = norm_tokens[end_idx - 1][1]
        snippet = "".join(lines[start_line - 1 : end_line])
        blocks.append(
            CodeBlock(
                path=path.as_posix(),
                start_line=start_line,
                end_line=end_line,
                token_str=token_str,
                snippet=snippet,
            )
        )
    return blocks
