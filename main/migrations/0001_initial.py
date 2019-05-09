# Generated by Django 2.1.5 on 2019-05-08 03:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=20)),
                ('description', models.TextField(blank=True, max_length=1000, null=True)),
                ('initial_balance', models.DecimalField(decimal_places=2, max_digits=20)),
                ('active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='AccountType',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True, max_length=1000, null=True)),
                ('budgetable', models.BooleanField()),
                ('financeable', models.BooleanField()),
                ('monthly_summary', models.BooleanField()),
                ('transaction_allowed', models.BooleanField()),
                ('loan_allowed', models.BooleanField()),
                ('split_allowed', models.BooleanField()),
                ('type_group', models.CharField(choices=[('CA', 'Category Account'), ('BU', 'Budget Account'), ('CR', 'Credit Account'), ('TR', 'Tracking Account'), ('SP', 'Special Account')], max_length=2)),
            ],
        ),
        migrations.CreateModel(
            name='Budget',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=20)),
                ('month', models.DateField()),
                ('amount', models.DecimalField(decimal_places=2, max_digits=20)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='budgets', to='main.Account')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='budgets', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='BudgetEntry',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('month', models.DateField()),
                ('notes', models.CharField(max_length=140, null=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=20)),
                ('account', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='budget_entries', to='main.Account')),
                ('budget', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='main.Budget')),
            ],
        ),
        migrations.CreateModel(
            name='ClosingDate',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('date', models.DateField()),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='closing_dates', to='main.Account')),
            ],
        ),
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=20)),
                ('cod', models.CharField(max_length=3)),
            ],
        ),
        migrations.CreateModel(
            name='TransactionEntry',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('transaction_id', models.IntegerField()),
                ('date', models.DateField()),
                ('entry_type', models.CharField(choices=[('T', 'Transaction'), ('S', 'Split'), ('C', 'Credit')], max_length=1)),
                ('description', models.CharField(max_length=140, null=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=20)),
                ('conciliated', models.BooleanField(default=False)),
                ('budget', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='main.Budget')),
                ('from_account', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='transaction_entries_from', to='main.Account')),
                ('to_account', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='transaction_entries_to', to='main.Account')),
            ],
        ),
        migrations.AddField(
            model_name='account',
            name='account_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='accounts', to='main.AccountType'),
        ),
        migrations.AddField(
            model_name='account',
            name='currency',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='accounts', to='main.Currency'),
        ),
    ]
