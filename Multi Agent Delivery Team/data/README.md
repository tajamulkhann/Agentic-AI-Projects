# Dataset dictionary and provenance

**Source:** Fully fictional local fixtures created for this repository. No external downloads, paid APIs, real orders, production logs or customer records. Original fixtures are CC0 1.0.

## Included files

- `data/eval_cases.json`: benchmark tasks with oracle labels
- `data/specs.json`: synthetic fixture data / local executable test asset

## Evaluation fields

Each task in `eval_cases.json` defines `id`, input `request`, `expected_status`, optional `expected_contains` tokens and optional `fault` for controlled failure injection. Exact-status checks plus token assertions verify known outcomes. This is a **fixture benchmark**, not a measure of general accuracy.

## Limitations

Small synthetic datasets and rule-based baselines may not resemble noisy production cases. Do not copy synthetic identifiers into real operations. Add independent holdout tasks and adversarial inputs for production research.

- `data/tool_catalog.json`: Tool allowlist derived from actual trace records for optional hosted model plan suggestions.
