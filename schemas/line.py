from pydantic import BaseModel

class LineLoginRequest(BaseModel):
    line_id: str
