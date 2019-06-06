from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import Sum, Q
from django.db.models.functions import Coalesce


class Currency(models.Model):

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20)
    cod = models.CharField(max_length=3)

    class Meta:
        verbose_name_plural = 'Currencies'

    def __str__(self):
        return self.name

class AccountType(models.Model):

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    description = models.TextField(max_length=1000, null=True, blank=True)

    def __str__(self):
        return self.name


class AccountSubType(models.Model):

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    description = models.TextField(max_length=1000, null=True, blank=True)
    account_type = models.ForeignKey(AccountType, on_delete=models.CASCADE, related_name='account_subtypes')

    def get_balance(self, year=None, month=None):
        if year:
            from_account_sum = TransactionEntry.objects.filter(Q(from_account__account_group__account_subtype=self) & Q(date__year=year) &
                Q(date__month=month)).aggregate(
                fsum=Coalesce(Sum('amount'), 0))
            to_account_sum = TransactionEntry.objects.filter(Q(to_account__account_group__account_subtype=self) & Q(date__year=year) &
                Q(date__month=month)).aggregate(
                tsum=Coalesce(Sum('amount'), 0))
            balance_account = to_account_sum['tsum'] - from_account_sum['fsum']
        else:
            from_account_sum = TransactionEntry.objects.filter(from_account__account_group__account_subtype=self).aggregate(
                fsum=Coalesce(Sum('amount'), 0))
            to_account_sum = TransactionEntry.objects.filter(to_account__account_group__account_subtype=self).aggregate(
                tsum=Coalesce(Sum('amount'), 0))
            balance_account = to_account_sum['tsum'] - from_account_sum['fsum']
        return balance_account

    def get_budget(self, year=None, month=None):
        budget = BudgetEntry.objects.filter(Q(account__account_group__account_subtype=self) & Q(month=month) & Q(year=year))
        return budget.aggregate(sum=Coalesce(Sum('amount'), 0))['sum']

    def get_available(self, year=None, month=None):
        return self.get_budget(year, month) - self.get_balance(year, month)

    def __str__(self):
        return self.name


class AccountGroup(models.Model):

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    description = models.TextField(max_length=1000, null=True, blank=True)
    account_subtype = models.ForeignKey(AccountSubType, on_delete=models.CASCADE, related_name='account_gorups')    

    def get_balance(self, year=None, month=None):
        from_account_sum = TransactionEntry.objects.filter(Q(from_account__account_group=self) & Q(date__year=year) &
            Q(date__month=month)).aggregate(
            fsum=Coalesce(Sum('amount'), 0))
        to_account_sum = TransactionEntry.objects.filter(Q(to_account__account_group=self) & Q(date__year=year) &
            Q(date__month=month)).aggregate(
            tsum=Coalesce(Sum('amount'), 0))
        balance_account = to_account_sum['tsum'] - from_account_sum['fsum']
        return balance_account

    def get_budget(self, year=None, month=None):
        budget = BudgetEntry.objects.filter(Q(account__account_group=self) & Q(month=month) & Q(year=year))
        return budget.aggregate(sum=Coalesce(Sum('amount'), 0))['sum']

    def get_available(self, year=None, month=None):
        return self.get_budget(year, month) - self.get_balance(year, month)

    def __str__(self):
        return self.name


class Account(models.Model):

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20)
    description = models.TextField(max_length=1000, null=True, blank=True)
    actual_balance = models.FloatField(null=True, blank=True)
    account_group = models.ForeignKey(AccountGroup, on_delete=models.CASCADE, related_name='accounts')
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name='accounts', default=1, null=True, blank=True)
    active = models.BooleanField(default=True, null=True)

    def __str__(self):
        return self.name

    def get_balance(self, year=None, month=None):
        if year:                
            from_account_sum = TransactionEntry.objects.filter(Q(from_account=self) & Q(date__year=year) &
                Q(date__month=month)).aggregate(
                fsum=Coalesce(Sum('amount'), 0))
            to_account_sum = TransactionEntry.objects.filter(Q(to_account=self) & Q(date__year=year) &
                Q(date__month=month)).aggregate(
                tsum=Coalesce(Sum('amount'), 0))
        else:
            from_account_sum = TransactionEntry.objects.filter(from_account=self).aggregate(
                fsum=Coalesce(Sum('amount'), 0))
            to_account_sum = TransactionEntry.objects.filter(to_account=self).aggregate(
                tsum=Coalesce(Sum('amount'), 0))
        balance_account = to_account_sum['tsum'] - from_account_sum['fsum']
        return balance_account

    def get_budget(self, year=None, month=None):
        budget = BudgetEntry.objects.filter(Q(account=self) & Q(month=month) & Q(year=year))
        return budget.aggregate(sum=Coalesce(Sum('amount'), 0))['sum']

    def get_available(self, year=None, month=None):
        return self.get_budget(year, month) - self.get_balance(year, month)


class ClosingDate(models.Model):

    id = models.AutoField(primary_key=True)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='closing_dates')
    date = models.DateField()


class Budget(models.Model):

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20)
    user = models.ForeignKey(
      get_user_model(),
      on_delete=models.CASCADE, related_name='budgets'
    )

    def __str__(self):
        return self.name


class TransactionEntry(models.Model):

    ENTRY_TYPE = (
        ('T', 'Transaction'),
        ('S', 'Split'),
        ('C', 'Credit')
    )

    id = models.AutoField(primary_key=True)
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, null=True)
    transaction_id = models.IntegerField(null=True)
    date = models.DateField()
    entry_type = models.CharField(max_length=1, choices=ENTRY_TYPE)
    from_account = models.ForeignKey(Account, on_delete=models.CASCADE,
                                     null=True, related_name='transaction_entries_from')
    to_account = models.ForeignKey(Account, on_delete=models.CASCADE,
                                   null=True, related_name='transaction_entries_to')
    description = models.CharField(max_length=140, null=True, blank=True)
    amount = models.FloatField()
    conciliated = models.BooleanField(default=True)

    def negative_amount(self):
        return -self.amount

    class Meta:
        verbose_name_plural = 'Transaction Entries'
        ordering = ['-pk']


class BudgetEntry(models.Model):

    id = models.AutoField(primary_key=True)
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, null=True)
    year = models.IntegerField()
    month = models.IntegerField()
    account = models.ForeignKey(Account, on_delete=models.CASCADE, null=True, related_name='budget_entries')
    notes = models.CharField(max_length=140, null=True)
    amount = models.FloatField()

    class Meta:
        verbose_name_plural = 'Budget Entries'
