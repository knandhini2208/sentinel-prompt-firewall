import re

# Fast, crude first-pass filter. Each hit adds to the heuristic score (0-1 capped).
PATTERNS = [
    (r"\bignore\b[\w\s]{0,25}\binstructions\b", "instruction_override"),
    (r"\bdisregard (your|the) (system prompt|instructions|rules)\b", "instruction_override"),
    (r"\bforget (everything|what) you (were|are) told\b", "instruction_override"),
    (r"\bdeveloper mode\b", "roleplay_jailbreak"),
    (r"\bno (content policy|restrictions|filters)\b", "roleplay_jailbreak"),
    (r"\bact as an? (unfiltered|unrestricted)\b", "roleplay_jailbreak"),
    (r"\brepeat everything above\b", "system_prompt_leak"),
    (r"\byour (original|initial) instructions\b", "system_prompt_leak"),
    (r"\bprint your system prompt\b", "system_prompt_leak"),
    (r"\bbase ?64\b", "encoding_obfuscation"),
    (r"\brot ?13\b", "encoding_obfuscation"),
    (r"\bapi key|credentials|secret token\b", "data_exfiltration"),
]

COMPILED = [(re.compile(p, re.IGNORECASE), cat) for p, cat in PATTERNS]


def heuristic_score(text: str):
    hits = [cat for pattern, cat in COMPILED if pattern.search(text)]
    if not hits:
        return 0.0, None
    score = min(1.0, 0.4 + 0.2 * len(hits))
    return score, hits[0]
