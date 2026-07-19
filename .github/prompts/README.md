# Copilot Prompt Library

Reusable Copilot Chat templates for this project. Copy the relevant prompt
into Copilot Chat, fill in the `[PLACEHOLDERS]`, and open the files listed
under "Open first" before sending.

These prompts complement `.github/copilot-instructions.md`:
**instructions apply automatically; prompts are used on demand.**

| Prompt | When to use | Open first | Produces |
|--------|-------------|-----------|----------|
| [generate-tests.md](generate-tests.md) | Writing a new test file | Source component + API route + related tests | Framework-correct test file |
| [automation-strategy.md](automation-strategy.md) | New project / major feature | User stories + source + coverage | Multi-layer strategy + pyramid |
| [review-tests.md](review-tests.md) | Before approving a test PR | The changed test files | Quality review + fixes |
| [generate-test-data.md](generate-test-data.md) | Need synthetic test data | db/schema.sql + conftest | Faker factory with privacy rules |
| [analyse-ci-failure.md](analyse-ci-failure.md) | A test fails, cause unclear | Failing test + source file | Root-cause classification + fix |

## Contributing

Found a great prompt? Add it here as a new `.md` file and update this table
in the same PR. Prompt files are code-reviewed like any other change.
