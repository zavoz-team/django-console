from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET

from adapter.http.django.forms import ProfilesFilterForm
from adapter.http.django.presenters import (
    profile_detail,
    profile_rows,
    ui_context,
    ui_errors,
)
from adapter.http.django.runtime import get_container
from domain.error import CoreUnavailableError, ProfileNotFoundError
from domain.query import TextQuery
from usecase.profile import GetProfileQuery, ListProfilesQuery


def _profile_query(form: ProfilesFilterForm) -> TextQuery | None:
    values = [
        form.cleaned_data.get('email'),
        form.cleaned_data.get('external_id'),
        form.cleaned_data.get('segment'),
    ]
    parts = [value for value in values if value]
    if not parts:
        return None
    return TextQuery(value=' '.join(parts))


@login_required
@require_GET
def profiles_page(request: HttpRequest) -> HttpResponse:
    form = ProfilesFilterForm(request.GET or None)
    valid = form.is_valid()
    if form.is_bound and not valid:
        context = ui_context(
            title='Profiles',
            errors=ui_errors(form),
            form=form,
        )
        return render(request, 'backoffice/profiles.html', context, status=400)

    query = _profile_query(form) if valid else None
    try:
        profiles = get_container().usecases.list_profiles.execute(
            ListProfilesQuery(
                pagination=form.pagination(),
                query=query,
            )
        )
    except CoreUnavailableError:
        context = ui_context(
            title='Profiles',
            errors=ui_errors(messages=('unavailable',)),
            form=form,
        )
        return render(request, 'backoffice/profiles.html', context, status=503)

    context = ui_context(
        title='Profiles',
        form=form,
        extra={'rows': profile_rows(list(profiles))},
    )
    return render(request, 'backoffice/profiles.html', context)


@login_required
@require_GET
def profile_page(request: HttpRequest, customer_id: str) -> HttpResponse:
    try:
        profile = get_container().usecases.get_profile.execute(
            GetProfileQuery(profile_id=customer_id)
        )
    except ProfileNotFoundError:
        context = ui_context(
            title='Profile',
            errors=ui_errors(messages=('not found',)),
            values={'customer_id': customer_id},
        )
        return render(request, 'backoffice/profile.html', context, status=404)
    except CoreUnavailableError:
        context = ui_context(
            title='Profile',
            errors=ui_errors(messages=('unavailable',)),
            values={'customer_id': customer_id},
        )
        return render(request, 'backoffice/profile.html', context, status=503)

    item = profile_detail(profile)
    context = ui_context(
        title='Profile',
        values={
            'customer_id': item.id,
            'display_name': item.display_name,
            'email': item.email,
            'phone': item.phone,
            'updated_at': item.updated_at,
        },
        extra={'profile': item},
    )
    return render(request, 'backoffice/profile.html', context)
