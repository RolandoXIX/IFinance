"""ifinance URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView
from main import views as main_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='transactions/'), name='main_home'),
    path('transactions/', main_views.TransactionsListView.as_view(), name='transactions_account', kwargs={'account':None}),
    path('transactions/<int:account>/', main_views.TransactionsListView.as_view(), name='transactions_account'),
    path('transactions/<int:account>/add/', main_views.CrudTransaction.as_view(), name='add_transaction'),
    path('transactions/<int:account>/<int:pk>/edit/', main_views.CrudTransaction.as_view(),
         name='edit_transaction', kwargs={'action': 'edit'}),
    path('transactions/<int:account>/<int:pk>/delete/', main_views.CrudTransaction.as_view(),
         name='delete_transaction', kwargs={'action': 'delete'}),
    path('account/add/', main_views.CrudAccount.as_view(), name='add_account'),
    path('account/<int:pk>/edit/', main_views.CrudAccount.as_view(), name='edit_account'),
]
