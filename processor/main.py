from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Result(BaseModel):
    id: int
    value: int


@app.get("/results/{result_id}")
def get_result(result_id: int) -> Result:
    return Result(result_id, 42)
