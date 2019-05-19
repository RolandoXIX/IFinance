from django.core.exceptions import ObjectDoesNotExist
from django.db.models.functions import Coalesce
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.utils.datetime_safe import datetime
from django.views.generic.base import View
from main.forms import TransactionForm, AccountCreateForm, AccountEditForm
from main.models import Account, TransactionEntry
from django.db.models import Sum, Q
import datetime
from django.urls import reverse


class AccountsMixin:

    def get_pay_account_list(self):
        return Account.objects.filter(account_type__type_group__in=['BU', 'CR', 'TR'])

    def get_balance(self, account):
        from_account_sum = TransactionEntry.objects.filter(from_account=account).aggregate(
            fsum=Coalesce(Sum('amount'), 0))
        to_account_sum = TransactionEntry.objects.filter(to_account=account).aggregate(
            tsum=Coalesce(Sum('amount'), 0))
        balance_account = to_account_sum['tsum'] - from_account_sum['fsum']
        return balance_account

    def get_account_and_balance(self):
        account_and_balance = []
        for pay_account in self.get_pay_account_list():
            balance_account = self.get_balance(pay_account)
            account_and_balance.append((pay_account, balance_account))
        return account_and_balance

    def get_active_account(self, pk):
        try:
            active = Account.objects.get(pk=pk)
        except ObjectDoesNotExist:
            active = {'name': 'All accounts', 'pk': 0}  # in order to use active.name and active.pk in template.
        return active

    def update_balance(self, account, initial_balance):
        actual_balance = self.get_balance(account)
        adjust = initial_balance - actual_balance
        if adjust:
            transaction = TransactionEntry(
                date=datetime.date.today(),
                entry_type='T',
                from_account=Account.objects.get(name='Manual adjustment'),
                to_account=account,
                description='Update balance',
                amount=adjust,
                conciliated=True,
            )
            transaction.save()


class TransactionsListView(View, AccountsMixin):

    def get(self, request, account=None):
        if account:
            get_object_or_404(Account, pk=account)
            transactions_list = TransactionEntry.objects.filter(Q(from_account=account) | Q(to_account=account))
        else:
            transactions_list = TransactionEntry.objects.all
        context = {
            'accounts_list': self.get_account_and_balance(), 'transactions_list': transactions_list,
            'active': self.get_active_account(account), 'pay_accounts': self.get_pay_account_list(),
        }
        return render(request, 'main/transactions_list.html', context)


class CreateEditTransaction(View, AccountsMixin):

    def get(self, request, pk=None, account=None):

        if pk:
            instance = get_object_or_404(TransactionEntry, pk=pk)
            form = TransactionForm(instance=instance)
        else:
            form = TransactionForm(initial={'date': datetime.date.today(), 'from_account': account})
        context = {'accounts_list': self.get_account_and_balance(), 'form': form, 'active': self.get_active_account(account)}
        return render(request, 'main/create_edit.html', context)

    def post(self, request, pk=None, account=0):

        redirect = reverse('transactions_account', kwargs={'account': account})

        try:
            form = TransactionForm(request.POST, instance=TransactionEntry.objects.get(pk=pk))
        except ObjectDoesNotExist:
            form = TransactionForm(request.POST)
        context = {'accounts_list': self.get_account_and_balance(), 'form': form, 'active': self.get_active_account(account)}

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(redirect)
        else:
            return render(request, 'main/create_edit.html', context)


class DeleteTransaction(View, AccountsMixin):

    def get(self, request, pk=None, account=None):

        get_object_or_404(TransactionEntry, pk=pk)
        context = {'accounts_list': self.get_account_and_balance(), 'active': self.get_active_account(account)}
        return render(request, 'main/delete.html', context)

    def post(self, request, pk=None, account=0):

        redirect = reverse('transactions_account', kwargs={'account': account})
        transaction = TransactionEntry.objects.get(pk=pk)
        transaction.delete()
        return HttpResponseRedirect(redirect)


class CreateEditAccount(View, AccountsMixin):

    def get(self, request, pk=None):

        if pk:
            instance = get_object_or_404(Account, pk=pk)
            form = AccountEditForm(instance=instance)
        else:
            form = AccountCreateForm()
        context = {'accounts_list': self.get_account_and_balance(), 'form': form, 'active': self.get_active_account(None)}
        return render(request, 'main/create_edit.html', context)

    def post(self, request, pk=None):

        try:
            form = AccountEditForm(request.POST, instance=Account.objects.get(pk=pk))
        except ObjectDoesNotExist:
            form = AccountCreateForm(request.POST)
        context = {'accounts_list': self.get_account_and_balance(), 'form': form, 'active': self.get_active_account(None)}

        if form.is_valid():
            new_account = form.save()
            self.update_balance(new_account, new_account.initial_balance)
            redirect = reverse('transactions_account', kwargs={'account': new_account.pk})
            return HttpResponseRedirect(redirect)
        else:
            return render(request, 'main/create_edit.html', context)


class DeleteAccount(View, AccountsMixin):

    def get(self, request, pk=None):

        get_object_or_404(Account, pk=pk)
        context = {'accounts_list': self.get_account_and_balance(), 'active': self.get_active_account(pk)}
        return render(request, 'main/delete.html', context)

    def post(self, request, pk=None):

        account = Account.objects.get(pk=pk)
        account.delete()
        return HttpResponseRedirect(reverse('main_home'))

