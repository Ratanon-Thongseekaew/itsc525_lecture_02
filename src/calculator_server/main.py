import math

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from asteval import Interpreter
from datetime import datetime, timezone
from calculator_server.calculator import expand_percent

app = FastAPI(title="Mini Calculator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

aeval = Interpreter(minimal=True, usersyms={"pi": math.pi, "e": math.e})

calculator_history: list[dict] = []

@app.post("/calculate")
def calculate(expr: str):
    try:
     
        aeval.error.clear()

        code = expand_percent(expr)
        result = aeval(code)

        if aeval.error:
            msg = "; ".join(
                str(error.get_error())
                for error in aeval.error
            )
            aeval.error.clear()

            return {
                "ok": False,
                "expr": expr,
                "result": "",
                "error": msg,
            }

        calculator_history.append(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "expr": expr,
                "result": result,
            }
        )

        return {
            "ok": True,
            "expr": expr,
            "result": result,
            "error": "",
        }

    except Exception as error:
        return {
            "ok": False,
            "expr": expr,
            "result": "",
            "error": str(error),
        }

@app.get("/history")
def get_history(limit: int = 50):
    return calculator_history[-limit:]

@app.delete("/history")
def delete_history():
    deleted_count = len(calculator_history)
    calculator_history.clear()

    return {
        "ok": True,
        "deleted": deleted_count,
        "message": "History cleared",
    }
