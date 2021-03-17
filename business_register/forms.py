from datetime import timedelta
from django import forms


class PepExportForm(forms.Form):

    def clean(self):
        cleaned_data = super().clean()
        updated_at = cleaned_data.get('updated_at', None)
        if updated_at is None or updated_at.start is None or updated_at.stop is None:
            raise forms.ValidationError({
                'updated_at': ['Period for updated_at is not provided.']
            })
        elif not timedelta(days=0) < updated_at.stop - updated_at.start <= timedelta(days=30):
            raise forms.ValidationError({
                'updated_at': ['Period for updated_at not matches restrictions.']
            })
        else:
            return cleaned_data
