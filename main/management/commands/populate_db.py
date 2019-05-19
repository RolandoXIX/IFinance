from django.core.management.base import BaseCommand
from main.models import AccountType, Account, TransactionEntry, Currency
from django.contrib.auth.models import User
import datetime


class Command(BaseCommand):

    help = 'populate db with start parameters and basic transactions'

    def create_initials(self):

        User.objects.create_superuser('admin', 'admin@myproject.com', 'admin')

        inflow = AccountType(
            name='Inflow',
            description='Categories for inflows transactions exclusively',
            budgetable=True, financeable=False, monthly_summary=False,
            transaction_allowed=True, loan_allowed=False, split_allowed=True,
            type_group='CA',
        )
        inflow.save()

        outflow = AccountType(
            name='Outflow',
            description='Categories for outflows transactions exclusively',
            budgetable=True, financeable=False, monthly_summary=False,
            transaction_allowed=True, loan_allowed=False, split_allowed=True,
            type_group='CA',
        )
        outflow.save()

        special = AccountType(
            name='Special',
            description='Special categories non-modificables used for specific operations',
            budgetable=False, financeable=False, monthly_summary=False, transaction_allowed=True,
            loan_allowed=True, split_allowed=True, type_group='CA',
        )
        special.save()

        bank = AccountType(
            name='Bank',
            description='For banks accounts',
            budgetable=True, financeable=False, monthly_summary=False, transaction_allowed=True,
            loan_allowed=True, split_allowed=True, type_group='BU',
        )
        bank.save()

        cash = AccountType(
            name='Cash',
            description='For banks accounts',
            budgetable=True, financeable=False, monthly_summary=False, transaction_allowed=True,
            loan_allowed=True, split_allowed=True, type_group='BU',
        )
        cash.save()

        credit_card = AccountType(
            name='Credit Card',
            description='Credit Card',
            budgetable=True, financeable=True, monthly_summary=True, transaction_allowed=True,
            loan_allowed=True, split_allowed=True, type_group='CR',
        )
        credit_card.save()

        credit_line = AccountType(
            name='Credit Line',
            description='Similar to credit cards but without monthly summary',
            budgetable=True, financeable=True, monthly_summary=False, transaction_allowed=True,
            loan_allowed=True, split_allowed=True, type_group='CR',
        )
        credit_line.save()

        savings = AccountType(
            name='Savings',
            description='An account like cash or bank but apart of budget',
            budgetable=False, financeable=False, monthly_summary=False, transaction_allowed=True,
            loan_allowed=False, split_allowed=True, type_group='TR',
        )
        savings.save()

        investments = AccountType(
            name='Investments',
            description='An account that can generate a return',
            budgetable=False, financeable=False, monthly_summary=False, transaction_allowed=True,
            loan_allowed=False, split_allowed=True, type_group='TR',
        )
        investments.save()

        peso = Currency(
            name='Peso',
            cod='ARS',
        )
        peso.save()

        manual_adjustment = Account(
            name='Manual adjustment',
            description='For adjustments',
            initial_balance=0, account_type=special, currency=peso, active=True,
        )
        manual_adjustment.save()

        wallet = Account(
            name='Wallet',
            description='Cash on hand',
            initial_balance=1000, account_type=cash, currency=peso, active=True,
        )
        wallet.save()

        transaction = TransactionEntry(
            date=datetime.date.today(),
            entry_type='T',
            from_account=manual_adjustment,
            to_account=wallet,
            description='Update balance',
            amount=2000,
            conciliated=True,
        )
        transaction.save()

        bank_of_america = Account(
            name='Bank American',
            description='Money in bank',
            initial_balance=10000, account_type=bank, currency=peso, active=True,
        )
        bank_of_america.save()

        transaction = TransactionEntry(
            date=datetime.date.today(),
            entry_type='T',
            from_account=manual_adjustment,
            to_account=bank_of_america,
            description='Update balance',
            amount=10000,
            conciliated=True,
        )
        transaction.save()

        market = Account(
            name='Market',
            description='Market Expenses',
            initial_balance=0, account_type=outflow, currency=peso, active=True,
        )
        market.save()

        salary = Account(
            name='Salary',
            description='Salary',
            initial_balance=0, account_type=inflow, currency=peso, active=True,
        )
        salary.save()

        transaction = TransactionEntry(
            date=datetime.date.today(),
            entry_type='T',
            from_account=wallet,
            to_account=market,
            description='Wallmart',
            amount=2000,
            conciliated=True,
        )
        transaction.save()

        transaction = TransactionEntry(
            date=datetime.date.today(),
            entry_type='T',
            from_account=bank_of_america,
            to_account=market,
            description='Wallmart',
            amount=3000,
            conciliated=True,
        )
        transaction.save()

        transaction = TransactionEntry(
            date=datetime.date.today(),
            entry_type='T',
            from_account=salary,
            to_account=wallet,
            description='May salary',
            amount=30000,
            conciliated=True,
        )
        transaction.save()

        transaction = TransactionEntry(
            date=datetime.date.today(),
            entry_type='T',
            from_account=salary,
            to_account=bank_of_america,
            description='May salary',
            amount=40000,
            conciliated=True,
        )
        transaction.save()

    def handle(self, *args, **options):
        self.create_initials()
