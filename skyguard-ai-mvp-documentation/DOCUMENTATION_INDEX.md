# SkyGuard AI — Documentation Index

## Product
- `prd.md` — What to build
- `architecture.md` — How it is structured
- `design.md` — UX/UI design

## Engineering
- `implementation-plan.md` — Build order
- `data-schema.md` — Data contracts
- `qc-rules.md` — Physics/QC rules
- `ml-spec.md` — ML specification
- `evaluation.md` — Evaluation methodology
- `tech-stack.md` — Technologies
- `api-spec.md` — Internal interfaces/future API

## Configuration
- `.env.example`
- `.gitignore`

## Source-of-truth rule

When documents conflict:

1. Actual validated implementation
2. `prd.md`
3. `architecture.md`
4. Relevant technical specification
5. `design.md`
6. Future roadmap

No document may claim a feature is implemented unless code and tests support it.
