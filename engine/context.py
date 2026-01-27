from pydantic import BaseModel
from typing import Any, Dict

class RequestContext(BaseModel):
    user: Dict[str, Any]
    resource: Dict[str, Any]
    environment: Dict[str, Any]