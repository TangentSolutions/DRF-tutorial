from django.test import TestCase, Client
from django.contrib.auth.models import User, AnonymousUser
from django.core.urlresolvers import reverse
from django.db import DatabaseError
import json
from mock import patch
from rest_framework.test import APIClient

class HealthTestCase(TestCase):
    def setUp(self):
        self.c = APIClient()
        self.status_fields = ['db', 'status']

    def test_health_endpoint_ok(self):
        url = reverse('health-list')
        response = self.c.get(url)
        assert response.status_code == 200, \
            "Expect 200 OK. got: {}" . format (response.status_code)

        expected_fields = ["db", "status"]

        for field in self.status_fields:
            assert response.json().get("status", {}).get(field, None) == "up", \
                "Expected field {} to exist" . format (field)

    @patch.object(User.objects, 'first')
    def test_determine_db_status(self, mock_query):
        """Health should not be ok if it cannot connect to the db"""

        mock_query.side_effect = DatabaseError()
        url = reverse('health-list')
        response = self.c.get(url)

        status = response.json().get("status", {})
        db_status = status.get('db')
        assert db_status == 'down', \
            'Expect DB to be down. Got: {}' . format (db_status)

        status = status.get('status')        
        assert status == 'down', \
            'Expect status to be down. Got: {}' . format (status)
        


class UserAPITestCase(TestCase):

    """
    User API
    """

    def setUp(self):
        self.c = APIClient()

        self.normal_user = User.objects.create_user(
            username="joe", password="password", email="joe@soap.com")
        self.superuser = User.objects.create_superuser(
            username="clark", password="supersecret", email="joe@soap.com")

    def test_get_list_requires_login(self):
        """GET /user requires a logged in user"""
        url = reverse("user-list")
        response = self.c.get(url)

        assert response.status_code == 403, \
            "Expect 403 OK. got: {}" . format(response.status_code)
        num_users = len(response.json())

    def test_logged_in_user_can_get_list(self):
        """GET /user returns a list of users for a valid logged in user"""
        
        self.c.login(username="joe", password="password")
        url = reverse("user-list")
        response = self.c.get(url)

        assert response.status_code == 200, \
            "Expect 403. got: {}" . format(response.status_code)
        num_users = len(response.json())  
        assert num_users == 2, \
          'Expect exactly 2 users. Got: {}' . format (num_users)      


    def test_logged_in_user_can_view_self(self):
        """GET /user/{pk} works if a user is logged in"""

        self.c.login(username="joe", password="password", email="joe@soap.com")
        url = reverse("user-detail", args=[self.normal_user.pk])
        response = self.c.get(url)

        assert response.status_code == 200, \
            "Expect 200 OK. got: {}" . format(response.status_code)

    def test_logged_in_user_can_edit_self(self):
        """GET /user/{pk} A user should be able to edit their own details"""

        self.c.login(username="joe", password="password")
        url = reverse("user-detail", args=[self.normal_user.pk])

        data = {
            "username": "joe",
            "first_name": "Joe", 
            "last_name": "Soap",
        }

        response = self.c.put(url, data, format="json")

        assert response.status_code == 200, \
            "Expect 200 OK. got: {}: {}" . format(response.status_code, response.content)

        joe = User.objects.get(username="joe")
        
        assert joe.first_name == "Joe", \
            "Expect user's first_name to be Joe. Got: {}" . format(joe.first_name)
        
    def test_cannot_view_user_detail_of_different_user(self):
        """A user should not be able to get details of another user"""

        # login as joe:
        self.c.login(username="joe", password="password")
        # get clark's details
        url = reverse("user-detail", args=[self.superuser.pk])
        response = self.c.get(url)

        assert response.status_code == 403, \
            "Expect not to be able to view another user's details. Expected 403. Got: {}" . format (response.status_code)


    def test_get_user_requires_login(self):
        """GET /user/{pk} returns 403 for non-loggedin user"""

        url = reverse("user-detail", args=[self.normal_user.pk])
        response = self.c.get(url)

        assert response.status_code == 403, \
            "Expect 403. got: {}" . format(response.status_code)
       
    def test_cannot_create_user_if_not_logged_in(self):
        """POST /user/ returns 401 AUTHENTICATIOD REQUIRED if not logged in"""

        data = {
            "username": "joe2",
            "email": "joe2@soap.com",
            "password": "pass"
        }
        url = reverse("user-list")
        response = self.c.post(url, data)
        assert response.status_code == 403, \
            "Expect 403 AUTHENTICATION REQUIRED. got: {}" . format(
                response.status_code)
        assert User.objects.count() == 2, \
            'Expect no new users to have been created'

    def test_only_staff_can_create_user(self):
        """POST /user/ returns 403 AUTHENTICATIOD REQUIRED for 
a logged in user who is not superuser"""

        data = {
            "username": "joe2",
            "email": "joe2@soap.com",
            "password": "pass"
        }
        url = reverse("user-list")

        self.c.login(username="joe", password="password")
        response = self.c.post(url, data)

        assert response.status_code == 403, \
            'Expect 403 created. Got: {}' . format (response.status_code)
        
        assert User.objects.count() == 2, \
            'Expect no new users to have been created'


    def test_can_create_user_if_logged_in(self):
        """POST /user/ returns 201 CREATED for a valid logged in user"""

        data = {
            "username": "joe2",
            "email": "joe2@soap.com",
            "password": "pass"
        }
        url = reverse("user-list")

        self.c.login(username="clark", password="supersecret")
        response = self.c.post(url, data)

        assert response.status_code == 201, \
            'Expect 201 created. Got: {}' . format (response.status_code)

        assert User.objects.count() == 3, \
            'Expect a new user to have been created'

    def tearDown(self):
        for user in User.objects.all():
            user.delete()

from api.permissions import IsSelfOrSuperUser

class MockRequest:
    pass

class MockView:
    pass

class PermissionsTestCase(TestCase):

    def setUp(self):            

        self.mock_request = MockRequest()
        self.mock_view = MockView()
        self.perms = IsSelfOrSuperUser()
        self.normal_user = User.objects.create_user(
            username="joe", password="password", email="joe@soap.com")
        self.superuser = User.objects.create_superuser(
            username="clark", password="supersecret", email="joe@soap.com")

    def test_normal_user_cant_create_or_delete(self):
        """An normal user should not be able to create or delete a user"""

        normal_user_cant = ['create', 'delete']

        self.mock_request.user = self.normal_user 

        for action in normal_user_cant:
            self.mock_view.action = action

            result = self.perms.has_permission(self.mock_request, self.mock_view)
            assert result == False, \
                'Expect normal user doesnt not have access to CREATE.'

    def test_normal_user_can_view_and_update(self):

        normal_user_can = ['list', 'detail', 'retrieve', 'update', 'partial_update']

        self.mock_request.user = self.normal_user 

        for action in normal_user_can:
            self.mock_view.action = action

            result = self.perms.has_permission(self.mock_request, self.mock_view)
            assert result == True, \
                'Expect normal user can view and update records'


    def test_not_loggedin_user_cannot_access_anything(self):

        self.mock_request.user = AnonymousUser()
        result = self.perms.has_permission(self.mock_request, self.mock_view)
        assert result == False, \
            'Not logged in always returns False. Got: {}' . format (result)

    def test_superuser_can_do_anything(self):

        self.mock_request.user = self.superuser
        all_actions = ['list', 'detail', 'create', 'retrieve', 'destroy', 'update', 'partial_update']
        for action in all_actions:
            self.mock_view.action = action
            result = self.perms.has_permission(self.mock_request, self.mock_view)
            assert result is True, \
              'Expect superuser can access anything. got: {}' . format (result)

    def test_can_edit_self(self):

        self.mock_request.user = self.normal_user
        
        result = self.perms.has_object_permission(self.mock_request, None, self.normal_user)
        assert result is True    

    def test_cannot_edit_other_user(self):

        self.mock_request.user = self.normal_user
        
        result = self.perms.has_object_permission(self.mock_request, None, self.superuser)
        assert result is False

class SwaggerLoginRedirect(TestCase):


    def setUp(self):
        self.c = Client()
        self.explorer_url = '/explorer/'


    def test_anon_user_is_redirected(self):

        response = self.c.get(self.explorer_url, follow=True)
        
        expected_redirect_chain = ('/api-auth/login/?next=/explorer/', 302)
        
        assert response.redirect_chain[0] == expected_redirect_chain, \
            'Expect 302 Temp redirect to API auth screen. Got: {}' . format (response.redirect_chain)


    def test_logged_in_user_is_not_redirected(self):

        user = User.objects.create_user("joe", "joe@soap.com", password="pass")
        self.c.login(username="joe", password="pass")

        response = self.c.get(self.explorer_url)
        assert response.status_code == 200, \
          'Expect a logged-in user to be able to view the explorer. Got: {}' . format (response.status_code)

