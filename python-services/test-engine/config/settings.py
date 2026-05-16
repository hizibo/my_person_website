"""
配置加载器
三层合并：config.yaml（默认）→ env.yaml（环境覆盖）→ secrets.yaml（敏感信息）
"""
import os
import yaml
from pathlib import Path

_CONFIG_DIR = Path(__file__).parent
_PROJECT_ROOT = _CONFIG_DIR.parent


def _deep_merge(base: dict, override: dict) -> dict:
    for key, value in override.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _deep_merge(base[key], value)
        else:
            base[key] = value
    return base


def load_config(env: str = None) -> dict:
    if env is None:
        env = os.getenv("TEST_ENV", "dev")

    # 1. 加载默认配置
    with open(_CONFIG_DIR / "config.yaml", "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}

    # 2. 环境覆盖
    env_file = _CONFIG_DIR / "env.yaml"
    if env_file.exists():
        with open(env_file, "r", encoding="utf-8") as f:
            env_cfg = yaml.safe_load(f) or {}
        if env in env_cfg:
            _deep_merge(cfg, env_cfg[env])

    # 3. 敏感信息覆盖
    secrets_file = _CONFIG_DIR / "secrets.yaml"
    if secrets_file.exists():
        with open(secrets_file, "r", encoding="utf-8") as f:
            secrets_cfg = yaml.safe_load(f) or {}
        _deep_merge(cfg, secrets_cfg)

    # 4. 环境变量覆盖密码
    env_pwd = os.getenv("WEB_ADMIN_PASSWORD")
    if env_pwd:
        cfg.setdefault("website", {})["admin_password"] = env_pwd

    return cfg


def get_project_root() -> Path:
    return _PROJECT_ROOT
