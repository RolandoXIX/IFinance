from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.utils.datetime_safe import datetime
from django.views.generic.base import View
from main.forms import TransactionForm
from main.models import Account, TransactionEntry
from django.db.models import Sum, Q
import datetime


class AccountList:

    pay_accounts_list = Account.objects.filter(account_type__type_group__in=['BU', 'CR', 'TR'])

    def get_account_and_balance(self):
        account_and_balance = []
        for pay_account in self.pay_accounts_list:
            from_account_sum = TransactionEntry.objects.filter(from_account=pay_account).aggregate(Sum('amount'))
            to_account_sum = TransactionEntry.objects.filter(to_account=pay_account).aggregate(Sum('amount'))
            balance_account = '{:,.2f}'.format(to_account_sum['amount__sum'] - from_account_sum['amount__sum'])
            account_and_balance.append((pay_account, balance_account))
        return account_and_balance


class TransactionsListView(View, AccountList):

    def get(self, request, account=0):
        if account > 0:
            transactions_list = TransactionEntry.objects.filter(Q(from_account=account) | Q(to_account=account))
        else:
            transactions_list = TransactionEntry.objects.all
        context = {
            'accounts_list': AccountList.get_account_and_balance(self), 'transactions_list': transactions_list,
            'active': account, 'pay_accounts': AccountList.pay_accounts_list,
        }
        return render(request, 'main/transactions_list.html', context)


class CrudTransaction(View, AccountList):

    def get(self, request, pk=None, account=0):
        try:
            form = TransactionForm(instance=TransactionEntry.objects.get(pk=pk))
        except ObjectDoesNotExist:
            form = TransactionForm(initial={'date': datetime.date.today(), 'from_account': account})
        context = {'accounts_list': AccountList.get_account_and_balance(self), 'form': form, 'active': account}
        return render(request, 'main/add_transaction.html', context)

    def post(self, request, pk=None, account=0):

        try:
            form = TransactionForm(request.POST, instance=TransactionEntry.objects.get(pk=pk))
        except ObjectDoesNotExist:
            form = TransactionForm(request.POST)
        context = {'accounts_list': AccountList.get_account_and_balance(self), 'form': form, 'active': account}
        redirect = '{}{}{}'.format('/transactions/', account, '/')

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(redirect)
        else:
            return render(request, 'main/add_transaction.html', context)
