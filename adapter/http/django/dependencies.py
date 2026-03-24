from adapter.di.container import AppContainer
from adapter.http.django.runtime import get_container as get_runtime_container
from usecase.user import GetUser


def get_container() -> AppContainer:
    return get_runtime_container()


def get_get_user() -> GetUser:
    return get_container().usecases.get_user
