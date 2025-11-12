from rest_framework import serializers

from .models import Operation, Wallet


class WalletSerializer(serializers.ModelSerializer):
    balance = serializers.IntegerField(
        min_value=0
    )

    class Meta:
        fields = ('balance',)
        model = Wallet


class OperationSerializer(serializers.ModelSerializer):
    operation_type = serializers.ChoiceField(
        source='type',
        choices=['DEPOSIT', 'WITHDRAW']
    )
    amount = serializers.IntegerField(
        min_value=0
    )

    class Meta:
        fields = ('operation_type', 'amount')
        model = Operation
