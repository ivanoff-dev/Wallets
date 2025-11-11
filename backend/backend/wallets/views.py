from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import (api_view, authentication_classes,
                                       permission_classes)

from .models import Wallet
from .serializers import OperationSerializer


@api_view(['GET'])
def get_wallet(request, id):
    wallet = get_object_or_404(Wallet, id=id)
    data = {
        'balance': wallet.balance
    }
    return JsonResponse(data, status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def create_operation(request, wallet_id):
    serializer = OperationSerializer(
        data=request.data,
        context={
            'wallet_id': wallet_id
        }
    )
    if serializer.is_valid():
        wallet = get_object_or_404(Wallet, id=wallet_id)
        operation = serializer.save(wallet_id=wallet)
        data = {
            'operation_id': operation.id,
            'status': 'SUCCESS',
            'type': operation.type,
            'amount': operation.amount
        }
        if operation.type == 'DEPOSIT':
            wallet.balance += operation.amount
        else:
            wallet.balance -= operation.amount
        wallet.save()
        return JsonResponse(data, status=status.HTTP_201_CREATED)

    data = {
        'message': serializer.errors
    }
    return JsonResponse(data, status=status.HTTP_400_BAD_REQUEST)
