from django.contrib import admin
from .models import Product, CartItem, Order

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'image')

class CartItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity', 'total_price')

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at')  # Fix list_display
    list_filter = ('created_at',)  # Fix list_filter

admin.site.register(Product, ProductAdmin)
admin.site.register(CartItem, CartItemAdmin)
admin.site.register(Order, OrderAdmin)
