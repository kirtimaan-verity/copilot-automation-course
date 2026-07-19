# Prompt: Generate Synthetic Test Data
# When to use: when you need realistic, privacy-safe test data
# Open first: db/schema.sql and any existing conftest fixtures

---

Generate a Python data factory module using Faker 25.x for:
  Entity: [e.g. Task / User]
  Schema reference: [open db/schema.sql]

Requirements:
- A factory class with methods returning dicts (not DB objects)
- valid_<entity>(): all fields, realistic values
- minimal_<entity>(): only required fields
- invalid_<entities>(): a list, ONE constraint violation per item
- bulk_<entities>(count): a list of N valid items

PRIVACY RULES (mandatory):
- All emails MUST use @example.com or @test.invalid ONLY
- All passwords MUST be hashed with hashlib.sha256 — never store plain text
- Never generate real-looking domains, phone numbers, or addresses

Add a module docstring explaining the privacy constraints.
