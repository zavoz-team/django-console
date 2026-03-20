from fastapi import APIRouter, Depends, HTTPException, status

from adapter.di.container import AppContainer
from adapter.http.fastapi.dependencies import get_container, get_get_user
from adapter.http.fastapi.schemas import ErrorResponse, HealthResponse, UserResponse
from domain.error import UserNotFoundError
from usecase.user import GetUser, GetUserQuery

router = APIRouter()


@router.get(
    '/health',
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
)
def health(container: AppContainer = Depends(get_container)) -> HealthResponse:
    return HealthResponse(
        status='ok',
        app=container.config.app.name,
        env=container.config.app.env,
    )


@router.get(
    '/users/{user_id}',
    response_model=UserResponse,
    responses={status.HTTP_404_NOT_FOUND: {'model': ErrorResponse}},
    status_code=status.HTTP_200_OK,
)
def get_user(user_id: str, usecase: GetUser = Depends(get_get_user)) -> UserResponse:
    try:
        user = usecase.execute(GetUserQuery(user_id=user_id))
    except UserNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return UserResponse(id=user.id, email=user.email, name=user.name)
