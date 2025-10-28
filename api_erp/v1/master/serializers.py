import datetime
from django.conf import settings

from rest_framework import serializers

from master.models import *

class RouteMasterSerializer(serializers.ModelSerializer):
    branch_name = serializers.SerializerMethodField()
    
    class Meta:
        model = RouteMaster
        fields = ['route_id','route_name','branch_id','branch_name']
        
    def get_branch_name(self,obj):
        return obj.branch_id.name
    
    
class BranchMasterSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = BranchMaster
        fields = ['branch_id','name','address','mobile','landline','phone','fax','trn','website','emirate','email','user_id','logo']
        
        
class EmirateMasterSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = EmirateMaster
        fields = ['emirate_id','name']
        
        
class DesignationMasterSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = DesignationMaster
        fields = ['designation_id','designation_name']
        
        
class LocationMasterSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = LocationMaster
        fields = ['location_id','location_name']