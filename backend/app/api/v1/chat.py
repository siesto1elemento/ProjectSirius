from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any

from app.services import orchestrator

router = APIRouter()

class ChatQuery(BaseModel):
    query: str

class ChatResponse(BaseModel):
    response: Any

@router.post("/", response_model=ChatResponse)
def handle_chat(chat_query: ChatQuery):
    """
    This endpoint is the main entry point for the conversational AI.
    It takes a user's query and uses the orchestration engine to get an answer.
    """
    # Step 1 & 2: Let the orchestrator decide which tool(s) to use.
    tool_calls = orchestrator.decide_on_tool(chat_query.query)

    if not tool_calls:
        # The LLM didn't choose a tool, maybe it's a greeting or general question.
        # For now, we'll return a simple response.
        return ChatResponse(response="I can only fetch financial data. Please ask me about a specific company.")

    if "error" in tool_calls[0]:
        error_detail = tool_calls[0]["error"]
        raise HTTPException(status_code=500, detail=error_detail)

    # For this version, we assume the LLM only calls one tool.
    # A more advanced version would loop through all tool_calls.
    tool_call = tool_calls[0]

    # Step 3: Execute the chosen tool.
    result = orchestrator.execute_tool_call(tool_call)

    # Step 4: For now, we just return the raw result from the tool.
    # A future "Response Synthesis" step would turn this into natural language.
    return ChatResponse(response=result)
