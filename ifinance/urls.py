from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView
from main import views as main_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='transactions/'), name='main_home'),
    path('transactions/', main_views.ListDeleteTransactions.as_view(), name='transactions', kwargs={'account':None}),
    path('transactions/<int:account>/', main_views.ListDeleteTransactions.as_view(), name='transactions'),
    path('transactions/<int:account>/add/', main_views.CreateEditTransaction.as_view(), name='add_transaction'),
    path('transactions/<int:account>/<int:pk>/edit/', main_views.CreateEditTransaction.as_view(), name='edit_transaction'),
    path('account/add/', main_views.CreateEditAccount.as_view(), name='add_account'),
    path('account/<int:account>/edit/', main_views.CreateEditAccount.as_view(), name='edit_account'),
    path('account/<int:account>/delete/', main_views.DeleteAccount.as_view(), name='delete_account'),
]
