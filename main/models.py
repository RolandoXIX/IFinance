from django.db import models
from django.contrib.auth import get_user_model


class AccountType(models.Model):

    TYPE_GROUP = (
        ('CA', 'Category Account'),
        ('BU', 'Budget Account'),
        ('CR', 'Credit Account'),
        ('TR', 'Tracking Account'),
    )

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    description = models.TextField(max_length=1000, null=True, blank=True)
    budgetable = models.BooleanField()
    financeable = models.BooleanField()
    monthly_summary = models.BooleanField()

    """ Defines what type of entry the account is allowed to use """
    transaction_allowed = models.BooleanField()
    loan_allowed = models.BooleanField()
    split_allowed = models.BooleanField()
    type_group = models.CharField(max_length=2, choices=TYPE_GROUP)

    def __str__(self):
        return self.name


class Currency(models.Model):

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20)
    cod = models.CharField(max_length=3)

    class Meta:
        verbose_name_plural = 'Currencies'

    def __str__(self):
        return self.name


class Account(models.Model):

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20)
    description = models.TextField(max_length=1000, null=True, blank=True)
    actual_balance = models.FloatField()
    account_type = models.ForeignKey(AccountType, on_delete=models.CASCADE, related_name='accounts')
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name='accounts')
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


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
    month = models.DateField()
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='budgets')
    amount = models.FloatField()

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
    description = models.CharField(max_length=140, null=True)
    amount = models.FloatField()
    conciliated = models.BooleanField(default=False)

    def negative_amount(self):
        return -self.amount

    class Meta:
        verbose_name_plural = 'Transaction Entries'
        ordering = ['-pk']


class BudgetEntry(models.Model):

    id = models.AutoField(primary_key=True)
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, null=True)
    month = models.DateField()
    account = models.ForeignKey(Account, on_delete=models.CASCADE, null=True, related_name='budget_entries')
    notes = models.CharField(max_length=140, null=True)
    amount = models.FloatField()

    class Meta:
        verbose_name_plural = 'Budget Entries'
