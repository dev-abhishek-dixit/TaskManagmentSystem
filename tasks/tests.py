from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from tasks.models import Task
from django.utils import timezone
from datetime import timedelta
from django.test.utils import override_settings


class TaskAPITest(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='admin', password='password'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.task = Task.objects.create(
            title='Test Task',
            description='Test Description',
            assigned_to=self.user,
            created_by=self.user
        )
        self.task_list_url = reverse('task-list')
        self.task_detail_url = reverse('task-detail', args=[self.task.id])

    def test_list_tasks(self):
        """Test listing all tasks"""
        response = self.client.get(self.task_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data['data']), 0)
        self.assertIn('title', response.data['data'][0])

    def test_get_task_detail(self):
        """Test getting a single task"""
        response = self.client.get(self.task_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Task')

    def test_create_task(self):
        """Test creating a task"""
        payload = {
            'title': 'New Task',
            'description': 'New Description',
            'status': 'pending',
            'due_date': (timezone.now() + timedelta(days=1)).isoformat(),
            'assigned_to_id': self.user.id,
            'created_by_id': self.user.id
        }
        response = self.client.post(self.task_list_url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['data']['title'], payload['title'])

     # THROTTLE_THRESHOLD is the variable that you set for DRF DEFAULT_THROTTLE_RATES
    @override_settings(THROTTLE_THRESHOLD='5/min')
    
    def test_task_rate_limit(self):
        """Test user rate limit"""

        for _ in range(5):
            self.client.get(self.task_list_url)

        # Third request - should fail
        response = self.client.get(self.task_list_url)
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        print("Rate limit test passed")


class UserAPITest(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='admin', password='password'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.user_list_url = reverse('user-list')
        self.user_detail_url = reverse('user-detail', args=[self.user.id])

    def test_list_users(self):
        """Test listing all users"""
        response = self.client.get(self.user_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['username'], 'admin')

    def test_get_user_detail(self):
        """Test getting a single user"""
        response = self.client.get(self.user_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'admin')
