# Data Pipeline

Canonical observation flow:

1. Load a CSV or deterministic simulation.
2. Normalize legacy column names.
3. Validate required observation fields.
4. Apply missingness, gap, duplicate, range, rate, persistence, and thermodynamic checks.
5. Generate leakage-safe temporal and derived features.
6. Run the ensemble detector and combine model and rule evidence.
7. Add spatial/temporal context, diagnosis, health, maintenance, and recovery fields.
8. Write results to `outputs/exports` or the configured output path.

Original observations remain available in the result data; recovery suggestions do not overwrite raw values.
