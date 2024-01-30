from pydantic import BaseModel


class Player(BaseModel):
    sid: str
    score: int = 0
    last_asked: int = 0


class Riddle(BaseModel):
    number: int
    text: str
    answer: str
