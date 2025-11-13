from django.urls import path

from .views import create_operation, get_wallet

urlpatterns = [
    path('wallets/<uuid:wallet_id>/operation', create_operation, name='create-operation'),
    path('wallets/<uuid:id>/', get_wallet, name='get-wallet')
]
