from django.urls import path
from .views import RfopView
from .views import RuoView

from . import views

urlpatterns = [
    path('', views.index, name='index'),
]

app_name = "ratu"
# app_name will help us do a reverse look-up latter.
urlpatterns = [
    path('rfop/', RfopView.as_view()),
    path('ruo/', RuoView.as_view())
]

