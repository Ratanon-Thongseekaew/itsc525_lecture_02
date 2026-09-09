from datetime import datetime

from pydantic import BaseModel


class Expression(BaseModel):
    expr: str

    def expand_percent(self) -> str:
        return self.expr.replace("%", " / 100")


class CalculatorLog(BaseModel):
    timestamp: datetime
    expr: str
    result: float