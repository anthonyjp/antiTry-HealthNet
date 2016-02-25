from typing import Callable, Any, Optional
from django.db import models

class Dictionary(models.Model):
    def put(self, key: str, value: str) -> None: ...
    def get(self, key: str) -> Optional[str]: ...


class SeparatedValuesField:
    def __init__(self, *args, **kwargs):
        self.token = ...  # type: str
        self.py_to_str = ...  # type: Callable[[Any], str]