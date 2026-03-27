from django.http import HttpRequest, JsonResponse
from django.views.decorators.http import require_GET

from adapter.http.django.runtime import get_container


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
