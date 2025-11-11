import uuid

from django.db import models


class Wallet(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    balance = models.IntegerField(
        null=False
    )


class OperationType(models.TextChoices):
    DEPOSIT = 'DEPOSIT', 'Зачисление'
    WITHDRAW = 'WITHDRAW', 'Списание'


class Operation(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    wallet_id = models.ForeignKey(
        Wallet,
        on_delete=models.CASCADE,
        related_name='wallets'
    )
    type = models.CharField(
        choices=OperationType.choices,
        null=False
    )
    amount = models.IntegerField(
        null=False
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
