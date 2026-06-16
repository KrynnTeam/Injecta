"""
Injecta — Base technique executor
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple


class TechniqueBase(ABC):
    name: str = "base"

    def __init__(self, requester, config, logger):
        self.req = requester
        self.config = config
        self.log = logger

    @abstractmethod
    def inject(self, url: str, param: str, sql: str, payload_template: str = None) -> Tuple[bool, Optional[str], Any]:
        pass

    def extract_string(self, url: str, param: str, sql: str, payload_template: str = None) -> Optional[str]:
        raise NotImplementedError

    def extract_int(self, url: str, param: str, sql: str, payload_template: str = None) -> Optional[int]:
        raise NotImplementedError

    def detect(self, url: str, param: str) -> bool:
        return False
