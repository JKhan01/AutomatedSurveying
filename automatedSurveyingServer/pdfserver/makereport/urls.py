from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    # path('pdf/<projectId>/', views.index, name= 'index'),
    path('pushimage/', views.pushImage, name = 'pushImage'),
    path('images/<projectId>', views.imageForm, name = 'imageForm'),
    path('pushdata/<pid>/<count>', csrf_exempt(views.pushData), name = 'pushData'),
    path('pdf/<projectid>', views.report, name = 'report'),
    path('testpost/<pid>', csrf_exempt(views.test_post), name = 'testpost')
]