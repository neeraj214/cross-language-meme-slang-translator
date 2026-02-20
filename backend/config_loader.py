from pathlib import Path
from typing import Any, Dict

import yaml


def load_config(path: str) -> dict:
  p = Path(path)
  if not p.is_file():
    raise FileNotFoundError(f'Config file not found: {p}')
  with p.open('r', encoding='utf-8') as f:
    data: Any = yaml.safe_load(f)
  if data is None:
    return {}
  if not isinstance(data, dict):
    raise ValueError('Config file must contain a mapping at the top level')
  return data

