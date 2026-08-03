---
name: diagnosing-bugs
description: Diagnose bugs and performance regressions through a tight reproducible feedback loop before fixing them.
---

# Diagnosing Bugs

1. Build one fast, deterministic, Agent-runnable command that detects the user's exact symptom.
2. Reproduce and minimise until every remaining input or step is load-bearing.
3. Generate three to five falsifiable, ranked hypotheses.
4. Instrument only to distinguish those hypotheses; change one variable at a time.
5. Convert the minimal repro into a failing regression test at the correct public Seam.
6. Apply the smallest fix, make the regression test green and rerun the original repro.
7. Remove temporary instrumentation and record the root cause and prevention insight.
8. Store the repro command, evidence and regression result in the active Bug Change.
9. Do not hypothesise from code inspection before a red-capable feedback loop exists.
