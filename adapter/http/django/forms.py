from django import forms
from django.contrib.auth.forms import AuthenticationForm

from domain.query import Pagination


class OperatorLoginForm(AuthenticationForm):
    pass


class PaginationForm(forms.Form):
    limit = forms.IntegerField(required=False, min_value=1)
    offset = forms.IntegerField(required=False, min_value=0)

    def pagination(self) -> Pagination:
        cleaned_data = getattr(self, 'cleaned_data', {})
        limit = cleaned_data.get('limit') or 20
        offset = cleaned_data.get('offset') or 0
        return Pagination(limit=limit, offset=offset)


class ProfilesFilterForm(PaginationForm):
    email = forms.CharField(required=False, strip=True)
    external_id = forms.CharField(required=False, strip=True)
    segment = forms.CharField(required=False, strip=True)


class SegmentsFilterForm(PaginationForm):
    pass


class SegmentMembersFilterForm(PaginationForm):
    pass


class JobsFilterForm(PaginationForm):
    pass


class AuditFilterForm(PaginationForm):
    pass


class ExportCreateForm(forms.Form):
    segment_id = forms.CharField(strip=True)
    destination = forms.CharField(strip=True)
