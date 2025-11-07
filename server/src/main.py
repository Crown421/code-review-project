from typing import Union

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class CodeMetadata(BaseModel):
    filename: str
    lines: str
    commit_hash: str


class Snippet(BaseModel):
    language: str
    code: str
    user: str
    metadata: Union[CodeMetadata, None] = None


@app.post("/snippets")
def create_snippet(snippet: Snippet):
    return {"message": "Snippet created successfully", "snippet": snippet}


@app.get("/snippets/{snippet_id}")
def read_snippet(snippet_id: int):
    return {
        "snippet_id": snippet_id,
        "language": "python",
        "code": "print('Hello, World!')",
        "user": "example_user",
    }
