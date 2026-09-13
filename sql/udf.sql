OPEN SCHEMA SENTINEL;

CREATE OR REPLACE PYTHON3 SET SCRIPT SENTINEL.SCORE_SIMILARITY (
    PROMPT_ID         VARCHAR(100),
    PROMPT_EMBEDDING  VARCHAR(20000),
    FP_CATEGORY       VARCHAR(100),
    FP_EMBEDDING      VARCHAR(20000)
) EMITS (
    PROMPT_ID     VARCHAR(100),
    BEST_CATEGORY VARCHAR(100),
    BEST_SCORE    DOUBLE
) AS

import json

def run(ctx):
    prompt_id = ctx.PROMPT_ID
    prompt_vec = json.loads(ctx.PROMPT_EMBEDDING)

    best_score = -1.0
    best_category = None

    while True:
        fp_vec = json.loads(ctx.FP_EMBEDDING)
        score = sum(a * b for a, b in zip(prompt_vec, fp_vec))
        if score > best_score:
            best_score = score
            best_category = ctx.FP_CATEGORY

        if not ctx.next():
            break

    ctx.emit(prompt_id, best_category, best_score)
/