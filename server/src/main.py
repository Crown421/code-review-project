from typing import Union
import os
import logging
import logging.config

from fastapi import FastAPI
from pydantic import BaseModel
from pydantic_core import from_json

from sqlmodel import Field, Session, SQLModel, create_engine, delete

from openai import OpenAI

# load some envs
MOCK_OPENAI = os.getenv("MOCK_OPENAI", "false").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
MODEL = os.getenv("MODEL", "gpt-5-nano")

# setup objects
logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)
logging.getLogger("sqlalchemy.engine").setLevel(LOG_LEVEL)

app = FastAPI()

engine = create_engine("sqlite:///./test.db")

client = OpenAI()


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

basic_prompt = """
Please review the above code snippet for potential issues, including but not limited to security vulnerabilities, performance concerns, and code quality.
"""
format_prompt = """
Provide a summary of your findings, specific suggestions for improvement, and categorize the severity of the issues as 'low', 'medium', or 'high'.
Respond in the following JSON format:
{{
  "summary": "<brief summary of issues>",
  "suggestions": ["<suggestion 1>", "<suggestion 2>", "...],
  "severity": "<low|medium|high>"
}}
"""


def review_code(code: str, language: str) -> Review:
    prompt = f"Here is a {language} code snippet:\n\n{code}\n\n{basic_prompt}"

    logger.info("Sending code to LLM")
    logger.debug(f"Prompt sent to LLM: {prompt}")
    # better would be to use a proper mocking library, maybe mock the completions method, but lets start here
    if not MOCK_OPENAI:
        completions = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": f"You are a helpful code review assistant.\n {format_prompt}",
                },
                {"role": "user", "content": prompt},
            ],
        )
        response_content = completions.choices[0].message.content

        review = Review.model_validate(from_json(response_content))

        logger.info("Received review from LLM")
        logger.debug(f"LLM response content: {response_content}")
    else:
        # mock response for testing without hitting OpenAI API
        review = Review(
            summary="The code contains hardcoded API keys which is a security risk.",
            suggestions=[
                "Move API keys to environment variables.",
                "Avoid using eval() for executing code.",
            ],
            severity="high",
        )

    return review


# endpoints
@app.post("/snippets")
def create_snippet(snippet: Snippet):
    logger.info(f"Received snippet from user {snippet.user} for review.")
    logger.debug(f"Snippet details: Language={snippet.language}, Code={snippet.code}")

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

    logger.debug(f"Stored snippet in DB with ID {db_snippet.id}")

    review.snippet_id = db_snippet.id

    return review


# don't know if using the same endpoint and distinguishing by methods is best practice here, but I am going with it
@app.get("/snippets/{snippet_id}")
def read_snippet(snippet_id: int):
    return {
        "snippet_id": snippet_id,
        "language": "python",
        "code": "print('Hello, World!')",
        "user": "example_user",
    }


@app.get("/snippets")
def list_snippets():
    # auto complete by copilot, first improvement would be pagination
    with Session(engine) as session:
        snippets = session.query(DB_Snippet).all()
        result = []
        for snip in snippets:
            result.append(
                {
                    "id": snip.id,
                    "language": snip.language,
                    "user": snip.user,
                    "review_summary": snip.review_summary,
                    "review_severity": snip.review_severity,
                }
            )
    return result


@app.delete("/snippets/{snippet_id}")
def delete_snippet(snippet_id: int):
    # again copilot autocomplete
    with Session(engine) as session:
        snippet = session.get(DB_Snippet, snippet_id)
        if snippet:
            session.delete(snippet)
            session.commit()
            return {"message": f"Snippet {snippet_id} deleted."}
        else:
            return {"message": f"Snippet {snippet_id} not found."}


@app.delete("/snippets")
def wipe_db():
    logger.warning("Wiping all snippets from the database!")
    # Ideally an action like this would also log request details (i.e. headers, IP if possible), but can't figure it out right now
    with Session(engine) as session:
        session.execute(delete(DB_Snippet))
        session.commit()
    return {"message": "All snippets deleted."}
