from django.db import models

# Create your models here.
from django.db import models
import uuid
from datetime import datetime
from accounts.models import *
from ckeditor.fields import RichTextField

class EmirateMaster(models.Model):
    emirate_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_by = models.CharField(max_length=20, null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    name = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        ordering = ('-created_date',)

    def __str__(self):
        return str(self.name)

class BranchMaster(models.Model):
    branch_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_by = models.CharField(max_length=20, null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    modified_by = models.CharField(max_length=20, null=True, blank=True)
    modified_date = models.DateTimeField(blank=True, null=True)
    name = models.CharField(max_length=50, null=True, blank=False)
    address = models.CharField(max_length=100, null=True, blank=False)
    mobile = models.CharField(max_length=20, null=True, blank=True)
    landline = models.CharField(max_length=20, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    fax = models.CharField(max_length=50, null=True, blank=True)
    trn = models.CharField(max_length=50, null=True, blank=True)
    website = models.CharField(max_length=50, null=True, blank=True)
    emirate = models.ForeignKey(EmirateMaster, on_delete=models.SET_NULL, null=True, blank=False)
    email = models.CharField(max_length=30, null=True, blank=True)
    user_id = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True, blank=True)
    logo = models.ImageField(null=True, blank=True, upload_to='master')

    class Meta:
        ordering = ('-created_date',)

    def __str__(self):
        return str(self.name)

class DesignationMaster(models.Model):
    designation_id   = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_by = models.CharField(max_length=20,  blank=True)
    created_date = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    modified_by = models.CharField(max_length=20, null=True, blank=True)
    modified_date = models.DateTimeField(blank=True, null=True)
    designation_name = models.CharField(max_length=50,unique=True)
    class Meta:
        ordering = ('designation_name',)

    def __str__(self):
        return str(self.designation_name)
    
class RouteMaster(models.Model):
    route_id   = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_by = models.CharField(max_length=20,  blank=True)
    created_date = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    modified_by = models.CharField(max_length=20, null=True, blank=True)
    modified_date = models.DateTimeField(blank=True, null=True)
    route_name = models.CharField(max_length=50,unique=True)
    branch_id = models.ForeignKey('master.BranchMaster', on_delete=models.SET_NULL, null=True, blank=True,related_name='route_branch')
    class Meta:
        ordering = ('route_name',)

    def __str__(self):
        return str(self.route_name)
    

class LocationMaster(models.Model):
    location_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_by = models.CharField(max_length=20,  blank=True)
    created_date = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    modified_by = models.CharField(max_length=20, null=True, blank=True)
    modified_date = models.DateTimeField(blank=True, null=True)
    location_name = models.CharField(max_length=50)
    emirate = models.ForeignKey(EmirateMaster, on_delete=models.SET_NULL, null=True, blank=False)
    branch_id = models.ForeignKey('master.BranchMaster', on_delete=models.SET_NULL, null=True, blank=True,related_name='loc_branch')
    class Meta:
        ordering = ('location_name',)

    def __str__(self):
        return str(self.location_name)

class CategoryMaster(models.Model):
    category_id   = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_by = models.CharField(max_length=20,  blank=True)
    created_date = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    modified_by = models.CharField(max_length=20, null=True, blank=True)
    modified_date = models.DateTimeField(blank=True, null=True)
    category_name = models.CharField(max_length=50,unique=True)
    is_deleted = models.BooleanField(default=False)
    class Meta:
        ordering = ('category_name',)
    
    def __str__(self):
        return str(self.category_name)
    
class PrivacyPolicy(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_by = models.CharField(max_length=20,  blank=True)
    created_date = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    modified_by = models.CharField(max_length=20, null=True, blank=True)
    modified_date = models.DateTimeField(blank=True, null=True)
    
    content = RichTextField()

    def __str__(self):
        return "Privacy Policy"

	
