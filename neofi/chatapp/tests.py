from django.test import TestCase, RequestFactory

# Create your tests here.
from chatapp.models import User
from chatapp.views import *

import json

class RegisterTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_wrong_method(self):
        request=self.factory.get("/api/register")
        response=register(request=request)
        self.assertEqual(response.status_code, 405)
        
    def test_username_missing(self):
        request=self.factory.post("/api/register")
        response=register(request=request)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data, "Username is missing")
        request=self.factory.post("/api/register", {"username": ""})
        response=register(request=request)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data, "Username is missing")

    def test_email_missing(self):
        request=self.factory.post("/api/register", {"username": "A"})
        response=register(request=request)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data, "Email is missing")
        request=self.factory.post("/api/register", {"username": "A", "email": ""})
        response=register(request=request)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data, "Email is missing")

    def test_password_missing(self):
        request=self.factory.post("/api/register", {"username": "A", "email": "a@b.c"})
        response=register(request=request)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data, "Password is missing")
        request=self.factory.post("/api/register", {"username": "A", "email": "a@b.c", "password": ""})
        response=register(request=request)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data, "Password is missing")

    def test_user_registered(self):
        request=self.factory.post("/api/register", {"username": "A", "email": "a@b.c", "password": "p"})
        response=register(request=request)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, "User created successfully")

    def test_username_duplicated(self):
        request=self.factory.post("/api/register", {"username": "A", "email": "a@b.c", "password": "p"})
        register(request=request)
        request=self.factory.post("/api/register", {"username": "A", "email": "d@e.f", "password": "w"})
        response=register(request=request)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data, "Username already in use")

    def test_email_duplicated(self):
        request=self.factory.post("/api/register", {"username": "A", "email": "a@b.c", "password": "p"})
        register(request=request)
        request=self.factory.post("/api/register", {"username": "B", "email": "a@b.c", "password": "w"})
        response=register(request=request)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data, "Email already in use")

class LoginTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_wrong_method(self):
        request=self.factory.get("/api/login")
        response=login(request=request)
        self.assertEqual(response.status_code, 405)

    def test_username_email_missing(self):
        request=self.factory.post("/api/login")
        response=login(request=request)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data, "Neither Username nor Email are provided")

    def test_password_missing(self):
        request=self.factory.post("/api/login", {"username_or_email": "A"})
        response=login(request=request)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data, "Password is missing")

    def test_no_user(self):
        request=self.factory.post("/api/login", {"username_or_email": "A", "password": "p"})
        response=login(request=request)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data, "User not found")
        request=self.factory.post("/api/register", {"username": "A", "email": "a@b.c", "password": "p"})
        register(request=request)
        request=self.factory.post("/api/login", {"username_or_email": "B", "password": "p"})
        response=login(request=request)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data, "User not found")

    def test_wrong_password(self):
        request=self.factory.post("/api/register", {"username": "A", "email": "a@b.c", "password": "p"})
        register(request=request)
        request=self.factory.post("/api/login", {"username_or_email": "A", "password": "q"})
        response=login(request=request)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data, "Wrong password entered")

    def test_login_via_username(self):
        request=self.factory.post("/api/register", {"username": "A", "email": "a@b.c", "password": "p"})
        register(request=request)
        request=self.factory.post("/api/login", {"username_or_email": "A", "password": "p"})
        response=login(request=request)
        self.assertEqual(response.status_code, 200)

    def test_login_via_email(self):
        request=self.factory.post("/api/register", {"username": "A", "email": "a@b.c", "password": "p"})
        register(request=request)
        request=self.factory.post("/api/login", {"username_or_email": "a@b.c", "password": "p"})
        response=login(request=request)
        self.assertEqual(response.status_code, 200)

class OnlineUsersTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_token_auth_failed(self):
        request=self.factory.get("/api/online-users")
        response=online_users(request=request)
        self.assertEqual(response.status_code, 401)
        request=self.factory.get("/api/online-users")
        response=online_users(request=request)
        self.assertEqual(response.status_code, 401)
        
    def test_wrong_method(self):
        request=self.factory.post("/api/register", {"username": "A", "email": "a@b.c", "password": "p"})
        register(request=request)
        request=self.factory.post("/api/login", {"username_or_email": "A", "password": "p"})
        response=login(request=request)
        token="Token "+response.data.split("Token ")[1]
        request=self.factory.post("/api/online-users", headers={"Authorization": token})
        response=online_users(request=request)
        self.assertEqual(response.status_code, 405)

    def test_success(self):
        request=self.factory.post("/api/register", {"username": "A", "email": "a@b.c", "password": "p"})
        register(request=request)
        request=self.factory.post("/api/register", {"username": "B", "email": "d@e.f", "password": "w"})
        register(request=request)
        request=self.factory.post("/api/login", {"username_or_email": "A", "password": "p"})
        response=login(request=request)
        token="Token "+response.data.split("Token ")[1]
        request=self.factory.get("/api/online-users", headers={"Authorization": token})
        response=online_users(request=request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["active_users"]), 1)
        self.assertEqual(response.data["active_users"][0]["username"], "A")

class SuggestedFriendsTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_wrong_method(self):
        request=self.factory.post("/api/suggested-friends/1")
        response=suggested_friends(request=request, user_id=1)
        self.assertEqual(response.status_code, 405)

    def test_no_user(self):
        request=self.factory.get("/api/suggested-friends/1001")
        response=suggested_friends(request=request, user_id=1001)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data, "User does not exist")

    def test_success(self):
        request=self.factory.get("/api/suggested-friends/1")
        response=suggested_friends(request=request, user_id=1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["suggested_users"]), 5)
        self.assertEqual(response.data["suggested_users"][0]["id"], 562)
        self.assertEqual(response.data["suggested_users"][1]["id"], 366)
        self.assertEqual(response.data["suggested_users"][2]["id"], 926)
        self.assertEqual(response.data["suggested_users"][3]["id"], 625)
        self.assertEqual(response.data["suggested_users"][4]["id"], 371)