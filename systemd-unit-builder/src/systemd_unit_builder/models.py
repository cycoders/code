from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class ServiceConfig(BaseModel):
    name: str
    exec_start: str
    user: Optional[str] = None
    working_directory: Optional[str] = None
    environment: Dict[str, str] = Field(default_factory=dict)
    after: List[str] = Field(default_factory=list)
    wants: List[str] = Field(default_factory=list)
    restart: str = "on-failure"
    restart_sec: int = 5
    private_tmp: bool = True
    no_new_privileges: bool = True