import requests
import datetime
from decimal import Decimal
from datetime import datetime

from django.contrib.auth.models import User
from django.db.models import Q, Sum, Min, Max
from django.shortcuts import get_object_or_404
from django.db import transaction, IntegrityError

from rest_framework import status
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes, renderer_classes

from master.models import BranchMaster, DesignationMaster, EmirateMaster, LocationMaster, RouteMaster

from api_erp.v1.master.serializers import BranchMasterSerializer, DesignationMasterSerializer, EmirateMasterSerializer, LocationMasterSerializer, RouteMasterSerializer


@api_view(['GET'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def routes(request):
    route_id = request.GET.get('route_id')
    many=True
    
    instances = RouteMaster.objects.all()
    
    if route_id:
        instances = instances.filter(pk=route_id).first()
        many=False
        
    serializer = RouteMasterSerializer(instances,many=many)
    
    status_code = status.HTTP_200_OK
    response_data = {
        "StatusCode": 6000,
        "status": status_code,
        "data": serializer.data
    }

    return Response(response_data, status_code)


@api_view(['GET'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def branch(request):
    branch_id = request.GET.get('branch_id')
    many=True
    
    instances = BranchMaster.objects.all()
    
    if branch_id:
        instances = instances.filter(pk=branch_id).first()
        many=False
        
    serializer = BranchMasterSerializer(instances,many=many)
    
    status_code = status.HTTP_200_OK
    response_data = {
        "StatusCode": 6000,
        "status": status_code,
        "data": serializer.data
    }

    return Response(response_data, status_code)


@api_view(['GET'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def emirate(request):
    emirate_id = request.GET.get('emirate_id')
    many=True
    
    instances = EmirateMaster.objects.all()
    
    if emirate_id:
        instances = instances.filter(pk=emirate_id).first()
        many=False
        
    serializer = EmirateMasterSerializer(instances,many=many)
    
    status_code = status.HTTP_200_OK
    response_data = {
        "StatusCode": 6000,
        "status": status_code,
        "data": serializer.data
    }

    return Response(response_data, status_code)


@api_view(['GET'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def designation(request):
    designation_id = request.GET.get('designation_id')
    many=True
    
    instances = DesignationMaster.objects.all()
    
    if designation_id:
        instances = instances.filter(pk=designation_id).first()
        many=False
        
    serializer = DesignationMasterSerializer(instances,many=many)
    
    status_code = status.HTTP_200_OK
    response_data = {
        "StatusCode": 6000,
        "status": status_code,
        "data": serializer.data
    }

    return Response(response_data, status_code)


@api_view(['GET'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def location(request):
    location_id = request.GET.get('location_id')
    many=True
    
    instances = LocationMaster.objects.all()
    
    if location_id:
        instances = instances.filter(pk=location_id).first()
        many=False
        
    serializer = LocationMasterSerializer(instances,many=many)
    
    status_code = status.HTTP_200_OK
    response_data = {
        "StatusCode": 6000,
        "status": status_code,
        "data": serializer.data
    }

    return Response(response_data, status_code)