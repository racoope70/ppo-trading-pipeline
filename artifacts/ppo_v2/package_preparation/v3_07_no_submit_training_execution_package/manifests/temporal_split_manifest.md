# Temporal Split Manifest

```text
run_id = v3_07_no_submit_ppo_v2_training_execution_001
temporal_windows_defined = true
timezone = UTC
training_execution_authorized = false
```

## Windows

| Split | Start UTC | End UTC | Use |
|---|---:|---:|---|
| Train | 2023-01-03T14:30:00Z | 2024-06-14T20:00:00Z | model fitting only if later authorized |
| Train/Eval Embargo | 2024-06-17T13:30:00Z | 2024-06-21T20:00:00Z | excluded |
| Evaluation | 2024-06-24T13:30:00Z | 2024-12-13T21:00:00Z | validation only if later authorized |
| Eval/Holdout Embargo | 2024-12-16T14:30:00Z | 2024-12-20T21:00:00Z | excluded |
| Holdout | 2024-12-23T14:30:00Z | 2025-06-30T20:00:00Z | final validation only if later authorized |

## Validation Requirements

Future preflight must verify:

- train, evaluation, and holdout ranges do not overlap
- embargo ranges are excluded from train/eval/holdout rows
- holdout is used only for final validation
- date boundaries are enforced per symbol
- split-boundary validation passes before training is reconsidered
