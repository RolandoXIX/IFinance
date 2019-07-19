from django.contrib import admin
from main.models import Account, TransactionEntry, Currency, BudgetEntry, Budget, CategoryGroup


admin.site.register(Account)
admin.site.register(TransactionEntry)
admin.site.register(Currency)
admin.site.register(CategoryGroup)
admin.site.register(BudgetEntry)
admin.site.register(Budget)
