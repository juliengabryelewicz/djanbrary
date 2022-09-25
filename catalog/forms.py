
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import datetime

from django import forms


class RenewBookForm(forms.Form):
    renewal_date = forms.DateField(
            help_text="Entrez une date jusqu'au mois prochain maximum.")

    def clean_renewal_date(self):
        data = self.cleaned_data['renewal_date']

        if data < datetime.date.today():
            raise ValidationError(_("Date invalide - Date antérieur à aujourd'hui"))
        if data > datetime.date.today() + datetime.timedelta(weeks=4):
            raise ValidationError(
                _("Date invalide - Vous ne pouvez pas aller au-delà du mois prochain"))
        return data