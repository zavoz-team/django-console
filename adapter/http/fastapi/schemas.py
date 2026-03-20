from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    app: str
    env: str


class UserResponse(BaseModel):
    id: str
    email: str
    name: str


class ErrorResponse(BaseModel):
    detail: str
