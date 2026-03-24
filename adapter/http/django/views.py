from django.http import HttpRequest, JsonResponse
from django.views.decorators.http import require_GET

from adapter.http.django.dependencies import get_container, get_get_user
from domain.error import UserNotFoundError
from usecase.user import GetUserQuery


@require_GET
def health(_: HttpRequest) -> JsonResponse:
    container = get_container()
    return JsonResponse(
        {
            'status': 'ok',
            'app': container.config.app.name,
            'env': container.config.app.env,
        }
    )


@require_GET
def get_user(_: HttpRequest, user_id: str) -> JsonResponse:
    try:
        user = get_get_user().execute(GetUserQuery(user_id=user_id))
    except UserNotFoundError as exc:
        return JsonResponse({'detail': str(exc)}, status=404)

    return JsonResponse({'id': user.id, 'email': user.email, 'name': user.name})
