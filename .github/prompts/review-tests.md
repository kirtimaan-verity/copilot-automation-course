# Prompt: Review Test Quality
# When to use: before approving a PR that adds or changes tests
# Open first: the test files changed in the PR

---

Review the open test file(s) for quality. For each issue found, show the
problematic code and the corrected version. Check specifically for:

1. FALSE POSITIVES — would this test pass even if the feature were broken?
   (e.g. asserting only status_code, or `assert x is not None`)
2. Test independence — does it assume state from another test?
3. Missing teardown — does it create data it doesn't clean up?
4. Flakiness — any waitForTimeout(), fixed sleeps, or race conditions?
5. Assertion quality — does every assert/expect have a message?
6. Hardcoded values — any localhost, credentials, or inline test data?
7. Naming — do test names follow test_<action>_<condition>_<expected_result>?

Summarise with a short list of the highest-priority fixes.
