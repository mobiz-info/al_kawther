from accounts.models import CustomUser
from rest_framework import serializers
from .models import Vacation

class VacationSerializer(serializers.ModelSerializer):
    customer_name = serializers.SerializerMethodField()
    class Meta:
        model = Vacation
        fields = ['vacation_id', 'customer', 'customer_name', 'start_date', 'end_date', 'note']
    
    def get_customer_name(self, obj):
        return obj.customer.customer_name if obj.customer else None