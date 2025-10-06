from pydantic import BaseModel, EmailStr



class MailboxBase(BaseModel):
    to_email: EmailStr
    from_email: EmailStr
    subject: str
    contents: str


class MailboxCreate(MailboxBase):
    pass


class MailboxOut(MailboxBase):
    id: int
    is_active: bool
    model_config = { "from_attributes": True }


class PaginatedMailboxOut(BaseModel):
    total: int
    page: int
    limit: int
    items: list[MailboxOut]


class MailboxUpdate(BaseModel):
    to_email : EmailStr | None = None
    from_email : EmailStr | None = None
    subject : str | None = None
    contents: str | None = None
    is_active: bool | None = None
