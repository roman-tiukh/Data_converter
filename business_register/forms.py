import re
from datetime import timedelta
from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _


class PeriodLimitationForm(forms.Form):
    selection_field = None
    days_limit = None

    def clean(self):
        assert self.selection_field
        assert self.days_limit
        cleaned_data = super().clean()
        selection_date = cleaned_data.get(self.selection_field, None)
        if selection_date is None or selection_date.start is None or selection_date.stop is None:
            if self.selection_field:
                raise forms.ValidationError({
                    self.selection_field: [_('Period for {} is not provided.').format(self.selection_field)]
                })
        elif not timedelta(days=0) < selection_date.stop - selection_date.start <= timedelta(days=self.days_limit):
            raise forms.ValidationError({
                self.selection_field: [_('Period for {} not matches restrictions.').format(self.selection_field)]
            })
        else:
            return cleaned_data


class PepExportForm(PeriodLimitationForm):
    selection_field = 'updated_at'
    days_limit = settings.PEP_EXPORT_XLSX_DAYS_LIMIT


class PepCheckFilterForm(forms.Form):
    def clean(self):
        cleaned_data = super().clean()
        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')
        middle_name = cleaned_data.get('middle_name')
        fullname_transcription = cleaned_data.get('fullname_transcription')

        transcription_or_ukr_names_error = forms.ValidationError(_(
            'Use first_name + last_name + middle_name '
            'or fullname_transcription fields for check person'
        ))
        if first_name or last_name or middle_name:
            if fullname_transcription:
                raise transcription_or_ukr_names_error
            if not first_name:
                raise forms.ValidationError({'first_name': _('This field is required')})
            if not last_name:
                raise forms.ValidationError({'last_name': _('This field is required')})
        elif fullname_transcription:
            fullname_transcription = re.sub(r'\s{2,}', ' ', fullname_transcription)
            if len(fullname_transcription.split(' ')) < 2:
                raise forms.ValidationError({
                    'fullname_transcription': _('The length of the field value must be 2 or more words')
                })
        else:
            raise transcription_or_ukr_names_error
        return cleaned_data
