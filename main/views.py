from django.core.exceptions import ObjectDoesNotExist
from django.db.models.functions import Coalesce
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.utils.datetime_safe import datetime
from django.views.generic.base import View
from main.forms import TransactionForm, AccountForm
from main.models import Account, TransactionEntry
from django.db.models import Sum, Q
import datetime


class AccountsMixin:

    def get_pay_account_list(self):
        return Account.objects.filter(account_type__type_group__in=['BU', 'CR', 'TR'])

    def get_account_and_balance(self):
        account_and_balance = []
        for pay_account in self.get_pay_account_list():
            from_account_sum = TransactionEntry.objects.filter(from_account=pay_account).aggregate(
                fsum=Coalesce(Sum('amount'), 0))
            to_account_sum = TransactionEntry.objects.filter(to_account=pay_account).aggregate(
                tsum=Coalesce(Sum('amount'), 0))
            balance_account = '{:,.2f}'.format(to_account_sum['tsum'] -
                                               from_account_sum['fsum'] +
                                               pay_account.initial_balance)
            account_and_balance.append((pay_account, balance_account))
        return account_and_balance

    def get_active_account(self, pk):
        try:
            active = Account.objects.get(pk=pk)
        except ObjectDoesNotExist:
            active = {'name': 'All accounts', 'pk': 0}  # in order to use active.name and active.pk in template.
        return active


class TransactionsListView(View, AccountsMixin):

    def get(self, request, account=None):
        if account:
            transactions_list = TransactionEntry.objects.filter(Q(from_account=account) | Q(to_account=account))
        else:
            transactions_list = TransactionEntry.objects.all
        context = {
            'accounts_list': self.get_account_and_balance(), 'transactions_list': transactions_list,
            'active': self.get_active_account(account), 'pay_accounts': self.get_pay_account_list(),
        }
        return render(request, 'main/transactions_list.html', context)


class CrudTransaction(View, AccountsMixin):

    def get(self, request, pk=None, account=0):
        try:
            form = TransactionForm(instance=TransactionEntry.objects.get(pk=pk))
        except ObjectDoesNotExist:
            form = TransactionForm(initial={'date': datetime.date.today(), 'from_account': account})
        context = {'accounts_list': self.get_account_and_balance(), 'form': form, 'active': self.get_active_account(account)}
        return render(request, 'main/add_transaction.html', context)

    def post(self, request, pk=None, account=0):

        try:
            form = TransactionForm(request.POST, instance=TransactionEntry.objects.get(pk=pk))
        except ObjectDoesNotExist:
            form = TransactionForm(request.POST)
        context = {'accounts_list': self.get_account_and_balance(), 'form': form, 'active': self.get_active_account(account)}
        redirect = '{}{}{}'.format('/transactions/', account, '/')

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(redirect)
        else:
            return render(request, 'main/add_transaction.html', context)


class CrudAccount(View, AccountsMixin):

    def get(self, request, pk=None):
        try:
            form = AccountForm(instance=Account.objects.get(pk=pk))
        except ObjectDoesNotExist:
            form = AccountForm()
        context = {'accounts_list': self.get_account_and_balance(), 'form': form}
        return render(request, 'main/add_transaction.html', context)

    def post(self, request, pk=None):

        try:
            form = AccountForm(request.POST, instance=Account.objects.get(pk=pk))
        except ObjectDoesNotExist:
            form = AccountForm(request.POST)
        context = {'accounts_list': self.get_account_and_balance(), 'form': form}
        redirect = '{}{}{}'.format('/transactions/', Account.objects.order_by('-pk')[0].pk, '/')

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(redirect)
        else:
            return render(request, 'main/add_transaction.html', context)