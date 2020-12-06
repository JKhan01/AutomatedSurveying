from django.urls import path
from . import views

urlpatterns = [
    # path('pdf/<projectId>/', views.index, name= 'index'),
    path('pushimage/', views.pushImage, name = 'pushImage'),
    path('images/<projectId>', views.imageForm, name = 'imageForm'),
    path('pushdata/', views.pushData, name = 'pushData'),
    path('pdf/<projectid>', views.report, name = 'report')
]