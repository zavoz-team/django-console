from typing import cast

from adapter.di.container import AppContainer
from fastapi import Depends, Request
from usecase.user import GetUser

APP_CONTAINER_STATE = 'container'
APP_CONFIG_STATE = 'config'


def get_container(request: Request) -> AppContainer:
    container = getattr(request.app.state, APP_CONTAINER_STATE, None)
    if container is None:
        raise RuntimeError('container unavailable')
    return cast(AppContainer, container)


def get_get_user(container: AppContainer = Depends(get_container)) -> GetUser:
    return container.usecases.get_user
