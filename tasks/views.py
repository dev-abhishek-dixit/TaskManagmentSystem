from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from .models import Task
from .serializers import TaskSerializer, UserSerializer
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.core.cache import cache
from rest_framework_simplejwt.authentication import JWTAuthentication

# Create your views here.

class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer # serializer for the task model
    permission_classes = [permissions.IsAuthenticated] # permission for the task model
    authentication_classes = [JWTAuthentication] # authentication for the task model

    def get_queryset(self):
        # cache the queryset for 5 minutes
        queryset = cache.get('all_tasks')
        if queryset is None:
            queryset = Task.objects.all()
            cache.set('all_tasks', queryset, timeout=300)

        status = self.request.query_params.get('status', None)
        assigned_to = self.request.query_params.get('assigned_to', None)
        
        if status:
            queryset = queryset.filter(status=status)
        if assigned_to:
            queryset = queryset.filter(assigned_to_id=assigned_to)
            
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'status': 'success',
            'data': serializer.data
        })


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({
            'status': 'success',
            'message': 'Task created successfully',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            'status': 'success',
            'message': 'Task updated successfully',
            'data': serializer.data
        })

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            'status': 'success',
            'message': 'Task deleted successfully'
        }, status=status.HTTP_204_NO_CONTENT)

        overdue_tasks = Task.objects.filter(
            Q(status='pending') & 
            Q(due_date__lt=timezone.now())
        )
        serializer = self.get_serializer(overdue_tasks, many=True)
        return Response({
            'status': 'success',
            'data': serializer.data
        })

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({
            'status': 'success',
            'message': 'User created successfully',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)
