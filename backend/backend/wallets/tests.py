from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from .models import Wallet, Operation


class WalletTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.wallet = Wallet.objects.create(balance=1000)
        self.url = reverse('get-wallet', kwargs={'id': self.wallet.id})
    
    def test_get_balance_success(self):
        """Тест успешного получения баланса кошелька"""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['balance'], 1000)

    def test_get_balance_not_found(self):
        """Тест запроса несуществующего кошелька"""
        url = reverse('get-wallet', kwargs={'id': '00000000-0000-0000-0000-000000000000'})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def get_balance_invalid_id(self):
        """Тест запроса по невалидному идентификатору"""
        response = self.client.get('/api/wallets/00000000-0000-0000-0000-000000000000/')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class OperationTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.wallet = Wallet.objects.create(balance=1000)
        self.url = reverse('create-operation', kwargs={'wallet_id': self.wallet.id})

    def test_create_deposit_success(self):
        """Тест успешного пополнения"""
        payload = {
            'operation_type': 'DEPOSIT',
            'amount': 100
        }
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()['status'], 'SUCCESS')
        self.assertEqual(response.json()['operation_type'], 'DEPOSIT')
        self.assertEqual(response.json()['amount'], 100)
        self.assertEqual(response.json()['new_balance'], 1100)
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, 1100)

    def test_create_withdraw_success(self):
        """Тест успешного списания"""
        payload = {
            'operation_type': 'WITHDRAW',
            'amount': 100
        }
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()['status'], 'SUCCESS')
        self.assertEqual(response.json()['operation_type'], 'WITHDRAW')
        self.assertEqual(response.json()['amount'], 100)
        self.assertEqual(response.json()['new_balance'], 900)
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, 900)

    def test_create_withdraw_low_balance_error(self):
        """Тест неуспешного списания, если недостаточно средств на кошельке"""
        payload = {
            'operation_type': 'WITHDRAW',
            'amount': 1500
        }
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()['message'], 'Недостаточно средств для списания')
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, 1000)

    def test_create_operation_invalid_type_error(self):
        """Тест неуспешной операции с неизвестным типом"""
        payload = {
            'operation_type': 'TEST',
            'amount': 500
        }
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('not a valid choice', str(response.json()['message']))

    def test_create_operation_subzero_amount_error(self):
        """Тест неуспешной операции с суммой меньше нуля"""
        payload = {
            'operation_type': 'DEPOSIT',
            'amount': -100
        }
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Ensure this value is greater than or equal to 0', str(response.json()['message']))
    
    def test_create_operation_incorrect_wallet_error(self):
        """Тест неуспешной операции с несуществующим кошельком"""
        url = reverse('create-operation', kwargs={'wallet_id': '00000000-0000-0000-0000-000000000000'})
        payload = {
            'operation_type': 'DEPOSIT',
            'amount': 100
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
