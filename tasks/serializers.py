from rest_framework import serializers
from django.contrib.auth.models import User
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError
from .models import Task
from .aws_lambda_simulation import lambda_notify_task_completed

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'first_name', 'last_name']
        read_only_fields = ['id']
    ## validate email
    def validate_email(self, value):
        if not value:
            raise serializers.ValidationError("Email is required.")
            
        # Get the current user instance if it exists (for updates)
        current_user = self.instance if self.instance else None
        
        # Check if email is already in use by another user
        if User.objects.filter(email=value).exclude(id=current_user.id if current_user else None).exists():
            raise serializers.ValidationError("A user with this email already exists.")
            
        # Validate email format
        try:
            EmailValidator()(value)
        except ValidationError:
            raise serializers.ValidationError("Enter a valid email address.")
            
        return value
    # validate username
    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value
    
    def create(self, validated_data):
        try:
            user = User.objects.create_user(
                username=validated_data['username'],
                email=validated_data['email'],
                password=validated_data['password'],
                first_name=validated_data.get('first_name', ''),
                last_name=validated_data.get('last_name', '')
            )
            return user
        except Exception as e:
            raise serializers.ValidationError(str(e))

class TaskSerializer(serializers.ModelSerializer):
    assigned_to = UserSerializer(read_only=True)
    assigned_to_id = serializers.IntegerField(write_only=True, required=True)
    created_by = UserSerializer(read_only=True)
    created_by_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'status', 
            'created_at', 'updated_at', 'due_date',
            'assigned_to', 'created_by',
            'assigned_to_id', 'created_by_id',
            'is_overdue'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_overdue']



    def validate_status(self, value):
        if value not in dict(Task.STATUS_CHOICES):
            raise serializers.ValidationError("Invalid status value")
        return value

    def validate_assigned_to_id(self, value):
        try:
            User.objects.get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError(f"User with id {value} does not exist.")
        return value

    def create(self, validated_data):
        created_by_id = validated_data.pop('created_by_id', None)
        
        task = Task.objects.create(
            created_by_id=created_by_id or self.context['request'].user.id,
            **validated_data
        )
        return task

    def update(self, instance, validated_data):
        assigned_to_id = validated_data.pop('assigned_to_id', None)
        created_by_id = validated_data.pop('created_by_id', None)
        status = validated_data.get('status', None)
       
        if status == 'completed' and instance.status != 'completed':
            lambda_notify_task_completed(instance.id, instance.title)
        if assigned_to_id is not None:
            instance.assigned_to_id = assigned_to_id
            
        if created_by_id is not None:
            instance.created_by_id = created_by_id
            
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
            
        instance.save()
        return instance 