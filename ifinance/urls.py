from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView
from main import views as main_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='transactions/'), name='main_home'),
    #transactions
    path('transactions/', main_views.ListDeleteTransactions.as_view(), name='transactions', kwargs={'account':None}),
    path('transactions/<int:account>/', main_views.ListDeleteTransactions.as_view(), name='transactions'),
    path('transactions/<int:account>/add/', main_views.CreateEditTransaction.as_view(), name='add_transaction'),
    path('transactions/<int:account>/<int:pk>/edit/', main_views.CreateEditTransaction.as_view(), name='edit_transaction'),
    #accounts
    path('accounts/add/', main_views.CreateEditAccount.as_view(), name='add_account'),
    path('accounts/<int:account>/edit/', main_views.CreateEditAccount.as_view(), name='edit_account'),
    path('accounts/<int:account>/delete/', main_views.DeleteAccount.as_view(), name='delete_account'),
    #budget
    path('budget/', main_views.Budget.as_view(), name='budget'),
    path('budget/<int:year>/<int:month>/', main_views.Budget.as_view(), name='budget'),
    path('budget/<int:year>/<int:month>/add_category/', main_views.CreateEditCategory.as_view(), name='add_category'),
    path('budget/<int:year>/<int:month>/add_group/', main_views.CreateEditCategoryGroup.as_view(), name='add_group'),
    path('budget/<int:year>/<int:month>/<int:category>/budget', main_views.CreateEditBudgetEntry.as_view(), name='edit_budget'),
    path('budget/<int:year>/<int:month>/<int:category>/edit', main_views.CreateEditCategory.as_view(), name='edit_category'),
    #path('budget/<int:year>/<int:month>/<int:category>/delete/', main_views.ListCategories.as_view(), name='delete_category'),
    #ajax
    path('ajax/load-to-accounts/', main_views.LoadToAccounts.as_view(), name='load_to_accounts'),
]
