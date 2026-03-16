from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('incharge-dashboard/', views.incharge_dashboard, name='incharge_dashboard'),
    path('student-dashboard/', views.student_dashboard, name='student_dashboard'),
    path('staff-dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('my-complaints/', views.my_complaints, name='my_complaints'),
    path('track-complaint/', views.track_complaint, name='track_complaint')

]