from django.contrib import admin
from main.models import Account, TransactionEntry, Currency, ClosingDate, AccountType, BudgetEntry, Budget


admin.site.register(Account)
admin.site.register(TransactionEntry)
admin.site.register(Currency)
admin.site.register(ClosingDate)
admin.site.register(AccountType)
admin.site.register(BudgetEntry)
admin.site.register(Budget)
