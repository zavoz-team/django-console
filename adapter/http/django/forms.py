from django import forms
from django.contrib.auth.forms import AuthenticationForm


class OperatorLoginForm(AuthenticationForm):
    pass


class ProfileFilterForm(forms.Form):
    email = forms.CharField(required=False, strip=True)
    external_id = forms.CharField(required=False, strip=True)
    segment = forms.CharField(required=False, strip=True)


class SegmentFilterForm(forms.Form):
    query = forms.CharField(required=False, strip=True)


class SegmentMembersFilterForm(forms.Form):
    query = forms.CharField(required=False, strip=True)
    limit = forms.IntegerField(required=False, min_value=1)
    offset = forms.IntegerField(required=False, min_value=0)


class JobsFilterForm(forms.Form):
    limit = forms.IntegerField(required=False, min_value=1)
    offset = forms.IntegerField(required=False, min_value=0)


class AuditFilterForm(forms.Form):
    limit = forms.IntegerField(required=False, min_value=1)
    offset = forms.IntegerField(required=False, min_value=0)


class ExportCreateForm(forms.Form):
    segment_id = forms.CharField(strip=True)
    destination = forms.CharField(strip=True)
