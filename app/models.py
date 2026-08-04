from pydantic import BaseModel

class Item(BaseModel):
    text: str
    completed: bool = False
