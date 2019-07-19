from django.core.exceptions import ObjectDoesNotExist
from django.db.models.functions import Coalesce
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.datetime_safe import datetime
from django.views.generic.base import View
from main.forms import TransactionForm, AccountCreateForm, AccountEditForm, CategoryForm, BudgetEntryForm, CategoryGroupForm
from main.models import Account, TransactionEntry, BudgetEntry, CategoryGroup
from django.db.models import Sum, Q
import datetime
import calendar
from django.urls import reverse
from dateutil import relativedelta


class AccountsMixin:

    def get_accounts(self):
        return Account.objects.filter(account_group__name__in=['Budget', 'Tracking', 'Credit'])

    def get_account_groups(self):
        account_groups = list(self.get_accounts().values_list('account_group__name', flat=True).distinct())
        return CategoryGroup.objects.filter(name__in=account_groups)        

    def get_budget_accounts(self):
        return Account.objects.filter(
            ~Q(account_group__group_type='A') |
            Q(account_group__name='Credit')
            )
    
    def get_budget_groups(self):
        budget_groups = list(self.get_budget_accounts().values_list('account_group__name', flat=True).distinct())
        return CategoryGroup.objects.filter(name__in=budget_groups).order_by('ordering')


    def get_active_account(self, pk):
        try:
            active = Account.objects.get(pk=pk)
        except ObjectDoesNotExist:
            active = {'name': 'All accounts', 'pk': 0}  # in order to use active.name and active.pk in template.
        return active

    def adjust_balance(self, account):
        adjust = account.get_balance() - account.actual_balance
        if adjust:
            transaction = TransactionEntry(
                date=datetime.date.today(),
                entry_type='T',
                from_account=account,
                to_account=Account.objects.get(name='Manual adjustment'),
                description='Update balance',
                amount=adjust,
                conciliated=True,
            )
            transaction.save()

    def update_balance(self):

        for account in self.get_accounts():
            instance = Account.objects.get(pk=account.pk)
            instance.actual_balance = account.get_balance()
            instance.save()


class ListDeleteTransactions(View, AccountsMixin):

    def get(self, request, account=None):
        if account:
            get_object_or_404(Account, pk=account)
            transactions = TransactionEntry.objects.filter(Q(from_account=account) | Q(to_account=account))
        else:
            transactions = TransactionEntry.objects.all
        context = {
            'accounts': self.get_accounts(), 'account_subtypes': self.get_account_groups(), 'transactions': transactions,
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
        context = {'accounts': self.get_accounts(), 'account_subtypes': self.get_account_groups(), 'form': form, 'active': self.get_active_account(account)}
        return render(request, 'main/create_edit.html', context)

    def post(self, request, pk=None, account=None):

        redirect = reverse('transactions', kwargs={'account': account})

        try:
            form = TransactionForm(request.POST, instance=TransactionEntry.objects.get(pk=pk))
        except ObjectDoesNotExist:
            form = TransactionForm(request.POST)
        context = {'accounts': self.get_accounts(), 'account_subtypes': self.get_account_groups(), 'form': form, 'active': self.get_active_account(account)}

        if form.is_valid():
            form.save()
            self.update_balance()
            return HttpResponseRedirect(redirect)
        else:
            return render(request, 'main/create_edit.html', context)


class LoadToAccounts(View):

    def get(self, request):
        id_from_account = request.GET.get('from_account')
        form = TransactionForm(initial={'from_account': id_from_account})
        return render(request, 'main/to_account_list_options.html', {'form': form})


class CreateEditAccount(View, AccountsMixin):

    def get(self, request, account=None):

        if account:
            instance = get_object_or_404(Account, pk=account)
            instance.actual_balance = Account.get_balance(instance)
            form = AccountEditForm(instance=instance)
        else:
            form = AccountCreateForm()
        context = {'accounts': self.get_accounts(), 'account_subtypes': self.get_account_groups(), 'form': form, 'active': self.get_active_account(account)}
        return render(request, 'main/create_edit.html', context)

    def post(self, request, account=None):

        try:
            instance = Account.objects.get(pk=account)
            form = AccountEditForm(request.POST, instance=instance)
        except ObjectDoesNotExist:
            form = AccountCreateForm(request.POST)
        context = {'accounts': self.get_accounts(), 'account_subtypes': self.get_account_groups(), 'form': form, 'active': self.get_active_account(None)}

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
        context = {'accounts': self.get_accounts(), 'account_subtypes': self.get_account_groups(), 'active': self.get_active_account(account)}
        return render(request, 'main/delete.html', context)

    def post(self, request, account=None):

        instance = Account.objects.get(pk=account)
        instance.delete()
        self.update_balance()
        return HttpResponseRedirect(reverse('main_home'))


class CreateEditCategory(View, AccountsMixin):

    def get(self, request, year, month, category=None):

        if category:
            instance = get_object_or_404(Account, pk=category)
            form = CategoryForm(instance=instance)
        else:
            form = CategoryForm()
        context = {'accounts': self.get_accounts(), 'account_subtypes': self.get_account_groups(),
        'form': form, 'year': year, 'month': month}
        return render(request, 'main/create_edit_category.html', context)

    def post(self, request, year, month, category=None):
        
        redirect = reverse('budget', kwargs={'year': year, 'month': month})
        
        try:
            instance = Account.objects.get(pk=category)
            form = CategoryForm(request.POST, instance=instance)
        except ObjectDoesNotExist:
            form = CategoryForm(request.POST)
        context = {'accounts': self.get_accounts(), 'account_subtypes': self.get_account_groups(),
        'form': form, 'year': year, 'month': month}

        if form.is_valid():
            new_account = form.save()
            return HttpResponseRedirect(redirect)
        else:
            return render(request, 'main/create_edit_category.html', context)


class CreateEditCategoryGroup(View, AccountsMixin):

    def get(self, request, year, month, category_group=None):

        if category_group:
            instance = get_object_or_404(CategoryGroup, pk=category_group)
            form = CategoryGroupForm(instance=instance)
        else:
            form = CategoryGroupForm()
        context = {'accounts': self.get_accounts(), 'account_subtypes': self.get_account_groups(),
        'form': form, 'year': year, 'month': month}
        return render(request, 'main/create_edit_category.html', context)

    def post(self, request, year, month, category_group=None):
        
        redirect = reverse('budget', kwargs={'year': year, 'month': month})
        
        try:
            instance = CategoryGroup.objects.get(pk=category_group)
            form = CategoryGroupForm(request.POST, instance=instance)
        except ObjectDoesNotExist:
            form = CategoryGroupForm(request.POST)
        context = {'accounts': self.get_accounts(), 'account_subtypes': self.get_account_groups(),
        'form': form, 'year': year, 'month': month}

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(redirect)
        else:
            return render(request, 'main/create_edit_category.html', context)


class Budget(View, AccountsMixin):

    def get(self, request, year=None, month=None):

        if not year:
            year = datetime.datetime.now().year
            month = datetime.datetime.now().month
        
        reference_date = datetime.datetime(year=year, month=month, day=1)
        next_month = reference_date + relativedelta.relativedelta(months=1)
        next_month = {'year': next_month.year, 'month': next_month.month}
        previous_month = reference_date + relativedelta.relativedelta(months=-1)
        previous_month = {'year': previous_month.year, 'month': previous_month.month}
        month_abbr = calendar.month_abbr[month]

        context = {
            'accounts': self.get_accounts(), 'account_subtypes': self.get_account_groups(), 
            'categories': self.get_budget_accounts(), 'budget_groups': self.get_budget_groups, 
            'year': year, 'month': month, 'previous_month': previous_month, 'next_month': next_month, 
            'month_abbr': month_abbr, 
         }
        return render(request, 'main/budget.html', context)


class CreateEditBudgetEntry(View, AccountsMixin):

    def get(self, request, year=None, month=None, category=None):

        try:
            instance = BudgetEntry.objects.filter(Q(account=category) & Q(year=year) & Q(month=month)).get()
            form = BudgetEntryForm(instance=instance)
        except ObjectDoesNotExist:
            form = BudgetEntryForm(initial={'account': category, 'year': year, 'month': month})
        context = {'accounts': self.get_accounts(), 'account_subtypes': self.get_account_groups(), 'form': form, 
        'year': year, 'month': month}
        return render(request, 'main/budget_entry.html', context)

    def post(self, request, year, month, category=None):
        
        redirect = reverse('budget', kwargs={'year': year, 'month': month})
        
        try:
            instance = BudgetEntry.objects.filter(Q(account=category) & Q(year=year) & Q(month=month)).get()
            form = BudgetEntryForm(request.POST, instance=instance)
        except ObjectDoesNotExist:
            form = BudgetEntryForm(request.POST)
        context = {'accounts': self.get_accounts(), 'account_subtypes': self.get_account_groups(), 'form': form, 
        'year': year, 'month': month}

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(redirect)
        else:
            return render(request, 'main/budget_entry.html', context)