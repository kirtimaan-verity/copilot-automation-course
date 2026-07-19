# Prompt: Analyse a CI / Test Failure
# When to use: when a test fails and the cause is unclear
# Open first: the failing test file AND the source file it tests

---

Analyse this test failure using the four-question framework:

Failure output:
  [PASTE THE ERROR / LOG OUTPUT]

Answer each:
1. WHAT failed? (which test, which assertion)
2. WHERE did it fail? (file + line)
3. WHY did it fail? Classify as ONE of:
     - Test bug (wrong locator/assertion/data)
     - Application bug (real defect)
     - Environment issue (service down, env var missing)
     - Flaky (timing / order / race)
4. HOW do I reproduce it independently? (give a curl or SQL command if possible)

Then recommend the fix. If it's a test bug, show the corrected code.
If it's an application bug, draft a short bug report with repro steps.
