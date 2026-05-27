from types import SimpleNamespace

import pytest

from src.vecnormalize_utils import (
    assert_eval_vecnormalize_locked,
    configure_eval_vecnormalize,
)


def _fake_vecnormalize(obs_value, ret_value, *, training=True, norm_reward=True):
    return SimpleNamespace(
        obs_rms={"mean": obs_value, "var": obs_value + 1},
        ret_rms={"mean": ret_value, "var": ret_value + 1},
        training=training,
        norm_reward=norm_reward,
    )


def test_configure_eval_vecnormalize_copies_train_stats_and_locks_eval():
    train_env = _fake_vecnormalize(10, 20)
    eval_env = _fake_vecnormalize(999, 999)

    configured = configure_eval_vecnormalize(train_env, eval_env)

    assert configured.obs_rms == train_env.obs_rms
    assert configured.ret_rms == train_env.ret_rms
    assert configured.training is False
    assert configured.norm_reward is False


def test_configure_eval_vecnormalize_deep_copies_stats():
    train_env = _fake_vecnormalize(10, 20)
    eval_env = _fake_vecnormalize(999, 999)

    configured = configure_eval_vecnormalize(train_env, eval_env)
    train_env.obs_rms["mean"] = -1

    assert configured.obs_rms["mean"] == 10


def test_configure_eval_vecnormalize_requires_obs_rms():
    train_env = SimpleNamespace()
    eval_env = _fake_vecnormalize(999, 999)

    with pytest.raises(AttributeError, match="obs_rms"):
        configure_eval_vecnormalize(train_env, eval_env)


def test_assert_eval_vecnormalize_locked_passes_for_eval_mode():
    eval_env = _fake_vecnormalize(10, 20, training=False, norm_reward=False)

    assert assert_eval_vecnormalize_locked(eval_env) is True


def test_assert_eval_vecnormalize_locked_rejects_training_mode():
    eval_env = _fake_vecnormalize(10, 20, training=True, norm_reward=False)

    with pytest.raises(ValueError, match="training=False"):
        assert_eval_vecnormalize_locked(eval_env)


def test_assert_eval_vecnormalize_locked_rejects_reward_normalization():
    eval_env = _fake_vecnormalize(10, 20, training=False, norm_reward=True)

    with pytest.raises(ValueError, match="norm_reward=False"):
        assert_eval_vecnormalize_locked(eval_env)