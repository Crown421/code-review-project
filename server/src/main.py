from typing import Union

from fastapi import FastAPI
from pydantic import BaseModel

from sqlmodel import Field, Session, SQLModel, create_engine

# setup tasks
app = FastAPI()

engine = create_engine("sqlite:///./test.db", echo=True)


# schemas
## api
class CodeMetadata(BaseModel):
    filename: str
    lines: str
    commit_hash: str


class Snippet(BaseModel):
    language: str
    code: str
    user: str
    metadata: Union[CodeMetadata, None] = None


class Review(BaseModel):
    snippet_id: int | None = None
    summary: str
    suggestions: list[str]
    # this should be an enum, but 1) keeping it simple for now, 2) need to check/ possibly reprocess LLM output if hallucinates a enum option.
    severity: str


## db
class DB_Snippet(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    language: str
    code: str
    user: str
    commit_hash: str | None = None
    filename: str | None = None
    lines: str | None = None
    review_summary: str
    review_suggestions: str
    review_severity: str


SQLModel.metadata.create_all(engine)


# some functions
def review_code(code: str, language: str) -> Review:
    # placeholder implementation (by copilot autocomplete)
    return Review(
        summary="This is a placeholder review summary.",
        suggestions=["Improve variable naming.", "Add error handling."],
        severity="medium",
    )


# endpoints
@app.post("/snippets")
def create_snippet(snippet: Snippet):
    review = review_code(snippet.code, snippet.language)
    db_snippet = DB_Snippet(
        language=snippet.language,
        code=snippet.code,
        user=snippet.user,
        # wonder if this can be simplified
        commit_hash=snippet.metadata.commit_hash if snippet.metadata else None,
        filename=snippet.metadata.filename if snippet.metadata else None,
        lines=snippet.metadata.lines if snippet.metadata else None,
        review_summary=review.summary,
        review_suggestions="; ".join(review.suggestions),
        review_severity=review.severity,
    )
    with Session(engine) as session:
        session.add(db_snippet)
        session.commit()
        session.refresh(db_snippet)

    review.snippet_id = db_snippet.id

    return review
    # return snippet
    # return {"message": "Snippet created successfully", "snippet_id": db_snippet.id}


@app.get("/snippets/{snippet_id}")
def read_snippet(snippet_id: int):
    return {
        "snippet_id": snippet_id,
        "language": "python",
        "code": "print('Hello, World!')",
        "user": "example_user",
    }
