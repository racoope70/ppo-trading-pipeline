import numpy as np
import pandas as pd
from gymnasium.spaces import Discrete

from src.env import ContinuousPositionEnv


def _sample_price_frame(rows: int = 140) -> pd.DataFrame:
    close = np.linspace(100.0, 110.0, rows)

    return pd.DataFrame(
        {
            "Open": close,
            "High": close + 1.0,
            "Low": close - 1.0,
            "Close": close,
            "Volume": np.arange(rows) + 1_000,
            "Denoised_Close": close,
            "SentimentScore": 0.0,
        }
    )


def test_parent_advance_action_prefers_two_when_valid():
    action = ContinuousPositionEnv._resolve_parent_advance_action(Discrete(3))

    assert action == 2


def test_parent_advance_action_falls_back_when_two_invalid():
    action_space = Discrete(2)
    action = ContinuousPositionEnv._resolve_parent_advance_action(action_space)

    assert action in {0, 1}
    assert action_space.contains(action)


def test_env_stores_valid_parent_advance_action():
    env = ContinuousPositionEnv(
        df=_sample_price_frame(),
        frame_bound=(20, 120),
        window_size=10,
    )

    try:
        assert hasattr(env, "_parent_action_space")
        assert hasattr(env, "_parent_advance_action")
        assert env._parent_action_space.contains(env._parent_advance_action)
    finally:
        env.close()


def test_env_step_returns_gymnasium_signature_and_parent_action_info():
    env = ContinuousPositionEnv(
        df=_sample_price_frame(),
        frame_bound=(20, 120),
        window_size=10,
    )

    try:
        obs, info = env.reset()
        assert obs is not None
        assert isinstance(info, dict)

        obs, reward, terminated, truncated, info = env.step(
            np.array([0.0], dtype=np.float32)
        )

        assert obs is not None
        assert isinstance(float(reward), float)
        assert isinstance(bool(terminated), bool)
        assert isinstance(bool(truncated), bool)
        assert isinstance(info, dict)
        assert "parent_advance_action" in info
        assert env._parent_action_space.contains(info["parent_advance_action"])
    finally:
        env.close()
