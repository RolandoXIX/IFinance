from django.forms import ModelForm, DateInput
from main.models import TransactionEntry, Account, BudgetEntry, CategoryGroup
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
        # self.fields['from_account'].queryset = Account.objects.filter(account_group__account_subtype__account_type__name='Account')
        
        self.fields['to_account'].queryset = Account.objects.exclude(account_group__group_type__isnull=True)

        # if 'from_account' in self.data:
        #     self.fields['to_account'].queryset = Account.objects.all()
        
        # elif self.initial['from_account']:
        #     id_from_account = self.initial['from_account']
        #     from_account = Account.objects.get(pk=id_from_account)

        #     if from_account.account_group.account_subtype.name == 'Tracking':
        #         self.fields['to_account'].queryset = Account.objects.filter(
        #             ~Q(pk=id_from_account) & Q(account_group__account_subtype__account_type__name='Account')
        #             )
        #     else:
        #         self.fields['to_account'].queryset = Account.objects.filter(
        #             ~Q(pk=id_from_account) & ~Q(account_group__account_subtype__account_type__name='Special')
        #             )

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['is'] = field_name


class AccountCreateForm(ModelForm):

    class Meta:
        model = Account
        fields = ['name', 'description', 'actual_balance', 'account_type', 'currency']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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

        self.fields['account_group'].queryset = CategoryGroup.objects.filter(group_type__in=['I', 'O'])

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['is'] = field_name


class CategoryGroupForm(ModelForm):

    class Meta:
        model = CategoryGroup
        fields = ['name', 'description', 'group_type']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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