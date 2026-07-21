# Workflow Architecture

| Role | What the role does in this repository | Copilot prompting approach | Copilot features that support it | Input received | Artefact produced | Output handed to next role |
|---|---|---|---|---|---|---|
| Planner | Turns a testing goal into a concrete approach for the task-manager app: decide whether coverage belongs in the API, database, web UI, mobile, or performance layers; map user stories such as task creation and filtering to test scenarios; identify setup, test data, risks, and validation scope. | Copilot Chat with file context is the primary mode because the planner needs repository-aware reasoning across docs, existing tests, routes, and components. Inline chat can refine a specific file once the target area is known. | Copilot Chat for requirement breakdown, workspace context awareness, repository instructions, semantic/code search, and agent-style exploration of existing tests, routes, UI components, and docs. | User story or test objective, relevant docs, existing test inventory, app layer under test, known issues, and repository conventions. | A test plan: scoped scenarios, priorities, assumptions, environments, and target files or suites. | A structured plan for the Writer, including target layer, scenario list, acceptance criteria, data/setup needs, and suggested files to create or update. |
| Writer | Implements or updates the actual tests and supporting test code. In this repo that means writing pytest tests for `tests/api/` or `tests/db/`, Playwright tests for `tests/web/`, and any page objects or fixtures needed while following repo conventions. | Edit mode is the primary mode for multi-file generation and revision. Inline chat helps with local code transformations inside a specific test file or page object. Copilot Chat with file context is used when the writer needs to compare implementation files with test code. | Inline completions, chat-driven code generation, multi-file editing, awareness of repository instructions, and nearby-code grounding from existing tests/components/routes. | The Planner's scenario plan, target files, existing test patterns, implementation files, repository test rules, and any required fixtures or environment assumptions. | Test code: new or updated spec files, fixtures, page objects, helper utilities, and small supporting assertions. | Executable test assets for the Execution role, plus the intended commands or scope to run and any setup/teardown expectations needed to execute them correctly. |
| Execution | Runs the tests or focused checks against the right layer, such as a single Playwright spec, a pytest file, or a narrow validation after a change. It is responsible for turning written tests into observable pass/fail evidence. | Copilot Chat with file context and terminal context is the main mode because execution is driven by commands, environment awareness, and narrow scope selection. Inline chat is useful for adjusting a single failing command in place. | Integrated terminal assistance, targeted test execution, command generation, environment-aware suggestions, and test-running support in the editor. | Test files from the Writer, environment configuration, run commands, setup instructions, and the intended validation scope. | Raw execution evidence: test run output, pass/fail status, stack traces, logs, and reproduction commands. | A result package for the Verifier containing command output, failing assertions, logs, rerun steps, and the exact slice of code or test that produced the result. |
| Verifier | Interprets the execution results and checks whether the tests actually validate the intended behavior. It distinguishes real product defects from flaky tests, bad assumptions, environment issues, or weak assertions, and identifies missing negative paths or cleanup gaps. | Copilot Chat with file context is the primary mode because verification depends on reading failing output alongside implementation and test code. Edit mode may be used for a small corrective patch once the defect is localized. | Copilot Chat over terminal output, diagnostics, code navigation, error inspection, symbol/reference lookup, and comparison of test intent with implementation in the API, DB schema, and React UI. | Execution logs, failing tests, relevant implementation files, original test intent, expected behavior, and any known constraints from the Planner or Writer. | Verification notes: defect hypotheses, assertion gaps, likely root cause, needed test fixes, and confidence in the result. | A decision-ready assessment for Reporting: what failed, why it likely failed, whether the issue is product code or test code, confidence level, and any required follow-up. |
| Reporting | Packages the outcome for humans: summarize what was tested, what passed or failed, where the risk remains, and what should happen next. For this repo, that often means reporting by layer: API, DB, web, mobile, or performance. | Copilot Chat with file context is the primary mode because reporting synthesizes the plan, changed tests, and execution results into one concise narrative. Inline chat is only useful for polishing a specific summary section. | Copilot Chat summarization, context from changed files and test output, and structured drafting for concise status reporting or handoff notes. | Planner scope, Writer changes, Execution evidence, Verifier conclusions, and any unresolved risks or blocked checks. | A test report: scope covered, results, defects found, residual risks, and recommended next actions. | Final stakeholder-facing summary, or a handoff document for the next engineering or QA action if further fixes or reruns are needed. |

For this repository, the clean handoff between roles is usually: Planner chooses the layer and scenarios, Writer creates the tests, Execution runs them narrowly, Verifier interprets failures against the app code, and Reporting turns that into a decision-ready summary.

## Artefact Flow Diagram

```text
User Goal / User Story / Change Request
		|
		v
+--------------------+
| 1. PLANNER         |
| Receives:          |
| - user objective   |
| - repo context     |
| - existing tests   |
| - known issues     |
| Produces:          |
| - test plan        |
| - scenario list    |
| - target layers    |
| - acceptance crit. |
+--------------------+
		|
		| hands off: plan, scope, target files, data/setup needs
		v
+--------------------+
| 2. WRITER          |
| Receives:          |
| - planner plan     |
| - target files     |
| - coding patterns  |
| - repo test rules  |
| Produces:          |
| - test code        |
| - fixtures         |
| - page objects     |
| - run scope        |
+--------------------+
		|
		| hands off: executable tests, setup notes, intended run commands
		v
+--------------------+
| 3. EXECUTION       |
| Receives:          |
| - test files       |
| - env config       |
| - run commands     |
| - validation scope |
| Produces:          |
| - pass/fail output |
| - logs             |
| - stack traces     |
| - repro steps      |
+--------------------+
		|
		| hands off: execution evidence, failures, logs, rerun details
		v
+--------------------+
| 4. VERIFIER        |
| Receives:          |
| - test results     |
| - failing tests    |
| - impl. code       |
| - expected behavior|
| Produces:          |
| - root-cause notes |
| - defect hypothesis|
| - test gap analysis|
| - confidence level |
+--------------------+
		|
		| hands off: assessed findings, issue classification, follow-up actions
		v
+--------------------+
| 5. REPORTING       |
| Receives:          |
| - planner scope    |
| - writer changes   |
| - execution output |
| - verifier findings|
| Produces:          |
| - final report     |
| - test summary     |
| - risk statement   |
| - recommendations  |
+--------------------+
		|
		v
Stakeholder / Team Decision / Next Action
```

```text
Planner
	input  -> goal, repo context, existing coverage
	output -> test plan, scenarios, acceptance criteria
				|
				v
Writer
	input  -> test plan, target files, repo rules
	output -> test code, fixtures, run scope
				|
				v
Execution
	input  -> test code, env config, commands
	output -> results, logs, failures, repro steps
				|
				v
Verifier
	input  -> results, failing tests, implementation
	output -> root cause, defect/test issue classification, gaps
				|
				v
Reporting
	input  -> scope, changes, results, findings
	output -> stakeholder report, residual risk, next steps
```

## GitHub Actions PR Automation

In a GitHub Actions pull request pipeline, the five roles do not execute equally. Some are naturally automatable in CI, while others remain human-led because they depend on scope selection, judgment, or merge readiness decisions.

| Role | Runs automatically on every pull request? | How it applies in this repository |
|---|---|---|
| Planner | No | Planning happens before or during test authoring. A human decides what parts of the task-manager app need coverage, which layer to test, and what risks matter for the change. |
| Writer | No | Writing or updating tests is a development activity completed before CI runs. Copilot can help generate the code, but a human chooses what to accept and commit into the PR. |
| Execution | Yes | This is the role GitHub Actions can run automatically on every PR. The pipeline can execute targeted test suites, linting, and other checks and then publish pass/fail evidence. |
| Verifier | Partly | CI can verify mechanical facts such as failed jobs, missing artifacts, or unmet thresholds. A human still has to judge whether a failure is a product defect, a flaky test, a setup issue, or a weak assertion. |
| Reporting | Partly | GitHub Actions can generate logs, job summaries, annotations, and artifacts automatically. A human reviewer still interprets the overall result and decides whether the PR should proceed or be blocked. |

The practical handoff in CI looks like this:

```text
Before PR:
Planner -> Writer

On every PR automatically:
Execution -> machine-assisted Verifier -> machine-assisted Reporting

Before merge:
human Verifier -> human Reporting / merge decision
```

In other words, GitHub Actions is strongest at running the checks and preserving the evidence. Human reviewers are still responsible for deciding whether the planned coverage was appropriate, whether the authored tests are meaningful, and whether the reported outcome is safe enough to merge.