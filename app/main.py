from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from decouple import config


from app.account.routers import router as account_router
from app.mailbox.routers import router as mailbox_router


app = FastAPI(title="FastAPI MAIL-CRUD Backend.")


app.add_middleware(
    CORSMiddleware, 
    allow_origins=[config("FRONTEND_URL")], 
    allow_credentials=True, 
    allow_methods=["*"], 
    allow_headers=["*"]
)


app.include_router(account_router, prefix="/api/account", tags=["Account"])
app.include_router(mailbox_router, prefix="/api/mailbox", tags=["Mailbox"])