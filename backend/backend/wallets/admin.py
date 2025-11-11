from django.contrib import admin

from .models import Operation, Wallet


class WalletAdmin(admin.ModelAdmin):
    list_display = ('id', 'balance')
    search_fields = ('id', 'balance')
    list_filter = ('balance',)


class OperationAdmin(admin.ModelAdmin):
    ordering = ['-created_at']
    list_display = ('id', 'wallet_id_display', 'type', 'amount', 'created_at')
    search_fields = ('id', 'wallet_id', 'type', 'created_at')
    list_filter = ('wallet_id', 'type')

    def wallet_id_display(self, obj):
        return obj.wallet_id.id
    wallet_id_display.short_description = 'wallet_id'


admin.site.register(Wallet, WalletAdmin)
admin.site.register(Operation, OperationAdmin)
