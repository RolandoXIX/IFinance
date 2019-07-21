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


class CategoryGroup(models.Model):

    INFLOW = 'I'
    OUTFLOW = 'O'
    ACCOUNT = 'A'
    OTHER = 'Z'

    GROUP_TYPES = [
        (INFLOW, 'Inflow'),
        (OUTFLOW, 'Outflow'),
        (ACCOUNT, 'Account'),
        (OTHER, 'Other'),
    ]

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    description = models.TextField(max_length=1000, null=True, blank=True)
    group_type = models.CharField(max_length=1 ,choices=GROUP_TYPES, null=True, blank=True)
    ordering = models.IntegerField(null=True, blank=True)

    def get_budget_group(self):
        if self.group_type == self.ACCOUNT:
            budget_group = 'Credit Debt Payments'
        elif self.group_type == self.OTHER:
            budget_group = 'Transfers and Adjustments'
        else:
            budget_group = self.name
        return budget_group


    def __str__(self):
        return self.name

class Account(models.Model):

    BANK = 'BK'
    CASH = 'CA'
    CREDIT_CARD = 'CC'
    CREDIT_LINE = 'CL'
    SAVINGS = 'SA'
    INVESTMENTS = 'IN'

    BK = CA = 'Budget'
    CC = CL = 'Credit'
    SA = IN = 'Tracking'

    ACCOUNT_TYPES = [
        ('Budget', (
            (BANK, 'Bank'),
            (CASH, 'Cash'),
            )
        ),
        ('Credit', (
            (CREDIT_CARD, 'Credit Card'),
            (CREDIT_LINE, 'Credit Line'),
            )
        ),
        ('Tracking', (
            (SAVINGS, 'Savings'),
            (INVESTMENTS, 'Investments'),
            )
        ),
        ]

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30)
    description = models.TextField(max_length=1000, null=True, blank=True)
    actual_balance = models.FloatField(null=True, blank=True)
    account_type = models.CharField(max_length=2, choices=ACCOUNT_TYPES, null=True, blank=True)
    account_group = models.ForeignKey(CategoryGroup, on_delete=models.CASCADE, related_name='accounts')
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name='accounts', null=True, blank=True)
    active = models.BooleanField(default=True, null=True)

    def get_balance(self, month=None, year=None):
        if year:
            from_account_sum = TransactionEntry.objects.filter(
                Q(from_account=self) &
                Q(date__year=year) &
                Q(date__month=month)).aggregate(
                fsum=Coalesce(Sum('amount'), 0))
            to_account_sum = TransactionEntry.objects.filter(
                Q(to_account=self) &
                Q(date__year=year) &
                Q(date__month=month)).aggregate(
                tsum=Coalesce(Sum('amount'), 0))
            balance_account = to_account_sum['tsum'] - from_account_sum['fsum']
            return balance_account
        else:
            from_account_sum = TransactionEntry.objects.filter(from_account=self).aggregate(
                fsum=Coalesce(Sum('amount'), 0))
            to_account_sum = TransactionEntry.objects.filter(to_account=self).aggregate(
                tsum=Coalesce(Sum('amount'), 0))
            balance_account = to_account_sum['tsum'] - from_account_sum['fsum']
            return balance_account

    def clean(self):
        if self.account_type:
            self.account_group = CategoryGroup.objects.get(name=getattr(Account, self.account_type))
        if self.actual_balance == None:
            self.actual_balance = 0


    def __str__(self):
        return self.name


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
    description = models.CharField(max_length=140, blank=True)
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
