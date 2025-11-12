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
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_wallet(request, id):
    try:
        wallet = get_object_or_404(Wallet, id=id)
        serializer = WalletSerializer(wallet)
        return JsonResponse(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        print(f'Ошибка операции: {e}')
        return JsonResponse(
            {
                'message': 'Внутренняя ошибка сервера'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def create_operation(request, wallet_id):
    try:
        with transaction.atomic():
            wallet = get_object_or_404(
                Wallet.objects.select_for_update(), id=wallet_id
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
                'type': operation.type,
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
