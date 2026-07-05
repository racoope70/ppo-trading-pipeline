# Quarantine and Log Manifest

```text
run_id = v3_07_no_submit_ppo_v2_training_execution_001
quarantine_root = artifacts/ppo_v2/quarantine/v3_07_no_submit_ppo_v2_training_execution_001
log_root = artifacts/ppo_v2/logs/v3_07_no_submit_ppo_v2_training_execution_001
stdout_path = artifacts/ppo_v2/logs/v3_07_no_submit_ppo_v2_training_execution_001/stdout.txt
stderr_path = artifacts/ppo_v2/logs/v3_07_no_submit_ppo_v2_training_execution_001/stderr.txt
artifact_inventory_path = artifacts/ppo_v2/quarantine/v3_07_no_submit_ppo_v2_training_execution_001/manifests/artifact_inventory.json
checksum_manifest_path = artifacts/ppo_v2/quarantine/v3_07_no_submit_ppo_v2_training_execution_001/manifests/checksums.sha256
training_execution_authorized = false
quarantine_output_creation_authorized = false
```

## Policy

If a later sealed checkpoint authorizes one-time no-submit PPO v2 training, outputs must remain local-only under the quarantine/log roots.

Future output inventory must include:

- model files
- normalization files
- prediction/evaluation logs
- training logs
- config copy
- runtime/dependency snapshot
- stdout/stderr captures
- artifact inventory
- checksum manifest

This task does not create quarantine outputs or log outputs.
