from django.core.exceptions import ObjectDoesNotExist
from django.db.models.functions import Coalesce
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
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

    def get_active_account(self, pk):
        try:
            active = Account.objects.get(pk=pk)
        except ObjectDoesNotExist:
            active = {'name': 'All accounts', 'pk': 0}  # in order to use active.name and active.pk in template.
        return active

    def adjust_balance(self, account):
        adjust = account.actual_balance - self.get_balance(account)
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

    def update_balance(self):

        for account in self.get_pay_account_list():
            instance = Account.objects.get(pk=account.pk)
            instance.actual_balance = self.get_balance(account)
            instance.save()

    def get_type_group_balance(self):
        
        types_and_balance = []
        for type in ['BU', 'CR', 'TR']:
            balance = Account.objects.filter(
                account_type__type_group=type
                ).aggregate(tsum=Coalesce(Sum('actual_balance'), 0))['tsum']
            types_and_balance.append((type, balance))


class ListDeleteTransactions(View, AccountsMixin):

    def get(self, request, account=None):
        if account:
            get_object_or_404(Account, pk=account)
            transactions_list = TransactionEntry.objects.filter(Q(from_account=account) | Q(to_account=account))
        else:
            transactions_list = TransactionEntry.objects.all
        context = {
            'accounts_list': self.get_pay_account_list(), 'transactions_list': transactions_list,
            'active': self.get_active_account(account), 
        }
        return render(request, 'main/transactions_list.html', context)

    def post(self, request, account=0):

        redirect = reverse('transactions', kwargs={'account': account})
        transactions = TransactionEntry.objects.filter(id__in=request.POST.getlist('id'))
        transactions.delete()
        self.update_balance()
        return HttpResponseRedirect(redirect)


class CreateEditTransaction(View, AccountsMixin):

    def get(self, request, pk=None, account=None):

        if pk:
            instance = get_object_or_404(TransactionEntry, pk=pk)
            form = TransactionForm(instance=instance)
        else:
            form = TransactionForm(initial={'date': datetime.date.today(), 'from_account': account, 'entry_type': 'T'})
        context = {'accounts_list': self.get_pay_account_list(), 'form': form, 'active': self.get_active_account(account)}
        return render(request, 'main/create_edit.html', context)

    def post(self, request, pk=None, account=0):

        redirect = reverse('transactions', kwargs={'account': account})

        try:
            form = TransactionForm(request.POST, instance=TransactionEntry.objects.get(pk=pk))
        except ObjectDoesNotExist:
            form = TransactionForm(request.POST)
        context = {'accounts_list': self.get_pay_account_list(), 'form': form, 'active': self.get_active_account(account)}

        if form.is_valid():
            form.save()
            self.update_balance()
            return HttpResponseRedirect(redirect)
        else:
            return render(request, 'main/create_edit.html', context)


class CreateEditAccount(View, AccountsMixin):

    def get(self, request, account=None):

        if account:
            instance = get_object_or_404(Account, pk=account)
            instance.actual_balance = self.get_balance(instance)
            form = AccountEditForm(instance=instance)
        else:
            form = AccountCreateForm()
        context = {'accounts_list': self.get_pay_account_list(), 'form': form, 'active': self.get_active_account(account)}
        return render(request, 'main/create_edit.html', context)

    def post(self, request, account=None):

        try:
            instance = Account.objects.get(pk=account)
            form = AccountEditForm(request.POST, instance=instance)
        except ObjectDoesNotExist:
            form = AccountCreateForm(request.POST)
        context = {'accounts_list': self.get_pay_account_list(), 'form': form, 'active': self.get_active_account(None)}

        if form.is_valid():
            new_account = form.save()
            self.adjust_balance(new_account)
            redirect = reverse('transactions', kwargs={'account': new_account.pk})
            return HttpResponseRedirect(redirect)
        else:
            return render(request, 'main/create_edit.html', context)


class DeleteAccount(View, AccountsMixin):

    def get(self, request, account=None):

        get_object_or_404(Account, pk=account)
        context = {'accounts_list': self.get_pay_account_list(), 'active': self.get_active_account(account)}
        return render(request, 'main/delete.html', context)

    def post(self, request, account=None):

        instance = Account.objects.get(pk=account)
        instance.delete()
        self.update_balance()
        return HttpResponseRedirect(reverse('main_home'))
