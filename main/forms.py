from django.forms import ModelForm, DateInput
from main.models import TransactionEntry, Account
from django.db.models import Q


class TransactionForm(ModelForm):

    class Meta:
        model = TransactionEntry
        fields = ['date', 'entry_type', 'from_account', 'to_account', 'description', 'amount']
        widgets = {
            'date': DateInput(attrs={'type': 'date'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['from_account'].queryset = Account.objects.filter(
            Q(account_type__transaction_allowed=True) & Q(account_type__type_group__in=['BU', 'CR', 'TR'])
        )
        self.fields['to_account'].queryset = Account.objects.filter(
            Q(account_type__transaction_allowed=True) & ~Q(account_type__name='special')
        )
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['is'] = 'field_name'


class AccountCreateForm(ModelForm):

    class Meta:
        model = Account
        fields = ['name', 'description', 'actual_balance', 'account_type', 'currency']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['is'] = 'field_name'


class AccountEditForm(ModelForm):

    class Meta:
        model = Account
        fields = ['name', 'description', 'actual_balance']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['is'] = 'field_name'
