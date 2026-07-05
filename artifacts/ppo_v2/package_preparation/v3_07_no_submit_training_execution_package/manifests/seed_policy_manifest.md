# Seed Policy Manifest

```text
run_id = v3_07_no_submit_ppo_v2_training_execution_001
seed_policy_defined = true
training_execution_authorized = false
```

## Seeds

| Component | Seed |
|---|---:|
| Python random | 70 |
| NumPy | 70 |
| PyTorch | 70 |
| Stable-Baselines3 PPO | 70 |
| Environment | 70 |

## Runtime Snapshot Policy

Future review must capture:

- Python version
- OS/platform
- package versions
- `pip freeze` or equivalent dependency snapshot
- CPU/GPU availability
- deterministic flags where supported
- git commit SHA
- clean/dirty working-tree status

This package does not create the runtime snapshot.
