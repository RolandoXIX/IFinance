from django.forms import ModelForm, DateInput
from main.models import TransactionEntry, Account, AccountType, BudgetEntry, AccountGroup, AccountSubType
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
        self.fields['from_account'].queryset = Account.objects.filter(account_group__account_subtype__account_type__name='Account')
        
        self.fields['to_account'].queryset = Account.objects.none()

        if 'from_account' in self.data:
            self.fields['to_account'].queryset = Account.objects.all()
        
        elif self.initial['from_account']:
            id_from_account = self.initial['from_account']
            from_account = Account.objects.get(pk=id_from_account)

            if from_account.account_group.account_subtype.name == 'Tracking':
                self.fields['to_account'].queryset = Account.objects.filter(
                    ~Q(pk=id_from_account) & Q(account_group__account_subtype__account_type__name='Account')
                    )
            else:
                self.fields['to_account'].queryset = Account.objects.filter(
                    ~Q(pk=id_from_account) & ~Q(account_group__account_subtype__account_type__name='Special')
                    )

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['is'] = field_name


class AccountCreateForm(ModelForm):

    class Meta:
        model = Account
        fields = ['name', 'description', 'actual_balance', 'account_group', 'currency']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['account_group'].queryset = AccountGroup.objects.filter(account_subtype__account_type__name='Account')

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['is'] = field_name


class AccountEditForm(ModelForm):

    class Meta:
        model = Account
        fields = ['name', 'description', 'actual_balance']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['is'] = field_name


class CategoryForm(ModelForm):

    class Meta:
        model = Account
        fields = ['name', 'description', 'account_group']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['account_group'].queryset = AccountGroup.objects.filter(account_subtype__account_type__name='Category')

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['is'] = field_name


class CategoryGroupForm(ModelForm):

    class Meta:
        model = AccountGroup
        fields = ['name', 'description', 'account_subtype']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['account_subtype'].queryset = AccountSubType.objects.filter(account_type__name='Category')

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['is'] = field_name


class BudgetEntryForm(ModelForm):

    class Meta:
        model = BudgetEntry
        fields = ['year', 'month', 'account', 'amount']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['is'] = field_name