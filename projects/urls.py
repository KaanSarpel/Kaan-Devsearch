from django.urls import path
from . import views

urlpatterns = [
    path('', views.projects, name="projects"),
    path('project/<str:pk>/', views.project, name="project"),
    path('create-project/', views.createProject, name="create-project"),
    path('update-project/<str:pk>/', views.updateProject, name="update-project"),
    path('delete-project/<str:pk>/', views.deleteProject, name="delete-project"),

    path('update-review/<str:pk>',views.updateReview,name='update-review'),
    path('delete-skill//<str:pk>', views.deleteReview, name='delete-review'),

    path('delete-tag/<str:pk>',views.deleteTag, name='delete-tag')
]
