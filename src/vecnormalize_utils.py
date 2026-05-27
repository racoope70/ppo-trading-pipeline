"""VecNormalize helper utilities for leakage-safe PPO evaluation.

The goal is to ensure that evaluation environments use normalization statistics
learned from training data only.

This module intentionally uses duck typing so the tests do not need to construct
a full Stable-Baselines3 VecNormalize object.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any


def configure_eval_vecnormalize(
    train_env: Any,
    eval_env: Any,
    *,
    norm_reward: bool = False,
) -> Any:
    """Copy train VecNormalize stats into eval env and lock eval mode.

    Required behavior:

    - obs_rms comes from the training environment.
    - ret_rms comes from the training environment when available.
    - eval_env.training is set to False.
    - eval_env.norm_reward is disabled by default.
    """
    if not hasattr(train_env, "obs_rms"):
        raise AttributeError("train_env must expose obs_rms.")

    if not hasattr(eval_env, "obs_rms"):
        raise AttributeError("eval_env must expose obs_rms.")

    eval_env.obs_rms = deepcopy(train_env.obs_rms)

    if hasattr(train_env, "ret_rms") and hasattr(eval_env, "ret_rms"):
        eval_env.ret_rms = deepcopy(train_env.ret_rms)

    eval_env.training = False
    eval_env.norm_reward = bool(norm_reward)

    return eval_env


def assert_eval_vecnormalize_locked(eval_env: Any) -> bool:
    """Validate that an eval VecNormalize environment is locked for evaluation."""
    if getattr(eval_env, "training", None) is not False:
        raise ValueError("Eval VecNormalize must have training=False.")

    if getattr(eval_env, "norm_reward", None) is not False:
        raise ValueError("Eval VecNormalize must have norm_reward=False.")

    return True