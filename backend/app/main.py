from fastapi import FastAPI
from app.api.v1 import company, chat

app = FastAPI(title="Project Sirius API")

# Include the v1 routers
app.include_router(company.router, prefix="/api/v1/company", tags=["company"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])


@app.get("/")
def read_root():
    return {"message": "Welcome to Project Sirius API"}
