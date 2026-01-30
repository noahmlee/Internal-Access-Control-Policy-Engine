from typing import Any, Dict

from pydantic import BaseModel


class RequestContext(BaseModel):
    user: Dict[str, Any]
    resource: Dict[str, Any]
    environment: Dict[str, Any]
