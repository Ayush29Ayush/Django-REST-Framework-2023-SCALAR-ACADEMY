from home import views
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from home.views import PeopleViewSet

router = DefaultRouter()
router.register(r"people", PeopleViewSet, basename="people")
urlpatterns = router.urls

urlpatterns = [
    path("", include(router.urls)),
    path("index/", views.index),
    path("person/", views.person),
    path("login/", views.login),
    path("register/", views.RegisterAPI.as_view()),
    path("login-api/", views.LoginAPI.as_view()),
    path("persons/", views.PersonAPI.as_view()),
]
