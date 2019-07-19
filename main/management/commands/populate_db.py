from django.core.management.base import BaseCommand
from main.models import AccountType, Account, TransactionEntry, Currency, BudgetEntry, AccountSubType, AccountGroup
from django.contrib.auth.models import User
import datetime


class Command(BaseCommand):

    help = 'populate db with start parameters and basic transactions'


    def create_account_type(self, name):
        account_type = AccountType(name=name)
        account_type.save()

    def create_account_subtype(self, name, account_type):
        account_subtype = AccountSubType(name=name, account_type=account_type)
        account_subtype.save()

    def create_account_group(self, name, account_subtype):
        account_group = AccountGroup(name=name, account_subtype=account_subtype)
        account_group.save()        

    def create_account(self, name, balance, account_group):
        new_account = Account(
            name=name, actual_balance=balance, account_group=AccountGroup.objects.get(name=account_group),
            currency=Currency.objects.get(name='Peso'))
        new_account.save()

        if balance:
            transaction = TransactionEntry(
                date=datetime.date.today(),
                entry_type='T',
                from_account=new_account,
                to_account=Account.objects.get(name='Manual adjustment'),
                description='Update balance',
                amount=balance,
                conciliated=True,
            )
            transaction.save()


    def create_transaction(self, from_account, to_account, amount):
            transaction = TransactionEntry(
                date=datetime.date.today(),
                entry_type='T',
                from_account=Account.objects.get(name=from_account),
                to_account=Account.objects.get(name=to_account),
                description='Some description',
                amount=amount,
                conciliated=True,
            )
            transaction.save()        

    def create_budget_entry(self, category, amount):
        budget_entry = BudgetEntry(
            year = datetime.date.today().year,
            month = datetime.date.today().month,
            account = Account.objects.get(name=category),
            amount = amount
            )
        budget_entry.save()


    def create_initials(self):

        #User.objects.create_superuser('admin', 'admin@myproject.com', 'admin')

        # AccountType
        self.create_account_type('Category')
        self.create_account_type('Account')
        self.create_account_type('Special')

        # AccountSubType
        self.create_account_subtype('Inflow', AccountType.objects.get(name='Category'))
        self.create_account_subtype('Outflow', AccountType.objects.get(name='Category'))
        self.create_account_subtype('Budget', AccountType.objects.get(name='Account'))
        self.create_account_subtype('Credit', AccountType.objects.get(name='Account'))
        self.create_account_subtype('Tracking', AccountType.objects.get(name='Account'))
        self.create_account_subtype('Special', AccountType.objects.get(name='Special'))

        # AccountGroup
        self.create_account_group('Special Inflows', AccountSubType.objects.get(name='Special'))
        self.create_account_group('Special Categories', AccountSubType.objects.get(name='Special'))
        self.create_account_group('Bank', AccountSubType.objects.get(name='Budget'))
        self.create_account_group('Cash', AccountSubType.objects.get(name='Budget'))
        self.create_account_group('Credit Card', AccountSubType.objects.get(name='Credit'))
        self.create_account_group('Credit Line', AccountSubType.objects.get(name='Credit'))
        self.create_account_group('Savings', AccountSubType.objects.get(name='Tracking'))
        self.create_account_group('Investments', AccountSubType.objects.get(name='Tracking'))
        self.create_account_group('Other Inflows', AccountSubType.objects.get(name='Inflow'))
        self.create_account_group('Other Outflows', AccountSubType.objects.get(name='Outflow'))


        # Currency
        peso = Currency(name='Peso', cod='ARS')
        peso.save()

        # Account and Initial Balance
        self.create_account('Manual adjustment', 0, 'Special Categories')
        self.create_account('Credit Inflow', 0, 'Special Inflows')
        self.create_account('Tracking Inflow', 0, 'Special Inflows')
        self.create_account('Wallet', 1000, 'Cash')
        self.create_account('Bank American', 56000, 'Bank')
        self.create_account('Visa', -6000, 'Credit Card')
        self.create_account('Mastercard', -9000, 'Credit Card')
        self.create_account('Plazo Fijo', 100000, 'Investments')
        self.create_account('Market', 0, 'Other Outflows')
        self.create_account('Education', 0, 'Other Outflows')
        self.create_account('Public Services', 0, 'Other Outflows')
        self.create_account('Suscriptions', 0, 'Other Outflows')
        self.create_account('Gasoline', 0, 'Other Outflows')
        self.create_account('Health', 0, 'Other Outflows')
        self.create_account('Hollidays', 0, 'Other Outflows')
        self.create_account('Salary', 0, 'Other Inflows')
        self.create_account('Other Inflows', 0, 'Other Inflows')
        self.create_account('Other Outflows', 0, 'Other Outflows')


        # Transactions
        self.create_transaction('Wallet', 'Market', 2000)
        self.create_transaction('Bank American', 'Market', 3000)
        self.create_transaction('Wallet', 'Salary', -30000)
        self.create_transaction('Bank American', 'Salary', -40000)
        self.create_transaction('Wallet', 'Education', 500)
        self.create_transaction('Wallet', 'Gasoline', 2000)
        self.create_transaction('Visa', 'Health', 3000)
        self.create_transaction('Visa', 'Market', 2000)
        self.create_transaction('Mastercard', 'Other Outflows', 4000)
        self.create_transaction('Wallet', 'Bank American', 6000)
        self.create_transaction('Bank American', 'Public Services', 2000)
        self.create_transaction('Bank American', 'Other Inflows', -50000)
        self.create_transaction('Wallet', 'Hollidays', 1000)
        self.create_transaction('Bank American', 'Plazo Fijo', 20000)
        self.create_transaction('Visa', 'Market', 4600)


        # Budgets
        self.create_budget_entry('Market', 10000)
        self.create_budget_entry('Education', 5000)
        self.create_budget_entry('Public Services', 1000)
        self.create_budget_entry('Suscriptions', 4000)
        self.create_budget_entry('Gasoline', 2000)
        self.create_budget_entry('Health', 1500)
        self.create_budget_entry('Hollidays', 2100)
        self.create_budget_entry('Salary', -50000)
        self.create_budget_entry('Other Inflows', -30000)
        self.create_budget_entry('Other Outflows', 4000)


    def handle(self, *args, **options):
        self.create_initials()
