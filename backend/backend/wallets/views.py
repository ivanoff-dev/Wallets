from django.db import transaction
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import (api_view, authentication_classes,
                                       permission_classes)
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated

from .models import Wallet
from .serializers import OperationSerializer, WalletSerializer


@api_view(['GET'])
@authentication_classes([])
@permission_classes([])
def get_wallet(request, id):
    """Метод позволяет получить баланс кошелька по идентификатору кошелька"""
    try:
        wallet = Wallet.objects.get(id=id)
        serializer = WalletSerializer(wallet)
        return JsonResponse(serializer.data, status=status.HTTP_200_OK)
    except Wallet.DoesNotExist:
        return JsonResponse(
            {
                'message': 'Кошелек не найден'
            },
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        print(f'Ошибка операции: {e}')
        return JsonResponse(
            {
                'message': 'Внутренняя ошибка сервера'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def create_operation(request, wallet_id):
    """Метод позволяет изменить баланс кошелька по его идентификатору.
    Доступны два типа операции:
    DEPOSIT - пополнение кошелька,
    WITHDRAW - списание с кошелька.
    Необходимо указать сумму больше либо равную нулю.
    Списание будет невозможно, если недостаточно средств на кошельке."""
    try:
        with transaction.atomic():
            try:
                wallet = Wallet.objects.select_for_update().get(id=wallet_id)
            except Wallet.DoesNotExist:
                return JsonResponse(
                    {
                        'message': 'Кошелек не найден'
                    },
                    status=status.HTTP_404_NOT_FOUND
                )
            serializer = OperationSerializer(
                data=request.data,
                context={
                    'wallet_id': wallet_id
                }
            )
            if not serializer.is_valid():
                return JsonResponse(
                    {
                        'message': serializer.errors
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            operation_data = serializer.validated_data
            amount = operation_data['amount']
            operation_type = operation_data['type']
            if operation_type == 'WITHDRAW' and wallet.balance < amount:
                return JsonResponse(
                    {
                        'message': 'Недостаточно средств для списания'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            if operation_type == 'DEPOSIT':
                Wallet.objects.filter(id=wallet_id).update(
                    balance=F('balance') + amount
                )
            else:
                Wallet.objects.filter(id=wallet_id).update(
                    balance=F('balance') - amount
                )
            operation = serializer.save(wallet_id=wallet)
            wallet.refresh_from_db()
            data = {
                'operation_id': operation.id,
                'status': 'SUCCESS',
                'operation_type': operation.type,
                'amount': operation.amount,
                'new_balance': wallet.balance
            }
            return JsonResponse(data, status=status.HTTP_201_CREATED)
    except Exception as e:
        print(f'Ошибка операции: {e}')
        return JsonResponse(
            {
                'message': 'Внутренняя ошибка сервера'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
