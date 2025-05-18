from django.contrib import admin
from .models import Customer, Product, Order, OrderItem
from django.db.models import Sum
from django.utils.timezone import now, timedelta

admin.site.register(Customer)
admin.site.register(Product)
admin.site.register(OrderItem)


class OrderAdmin(admin.ModelAdmin):
    change_list_template = "admin/order_change_list.html"

    def changelist_view(self, request, extra_context=None):
        today = now().date()
        labels = []
        data = []

        for i in range(30):
            day = today - timedelta(days=i)
            labels.append(day.strftime('%b %d'))
            total = Order.objects.filter(date_ordered__date=day).aggregate(Sum('total'))['total__sum'] or 0
            data.append(float(total))

        labels.reverse()
        data.reverse()

        extra_context = extra_context or {}
        extra_context['bar_labels'] = labels
        extra_context['bar_data'] = data

        return super().changelist_view(request, extra_context=extra_context)


admin.site.register(Order, OrderAdmin)
