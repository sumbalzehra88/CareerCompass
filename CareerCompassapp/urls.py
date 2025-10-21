# CareerCompassapp/urls.py
# URL patterns for the CareerCompass application

from django.urls import path
from . import views


urlpatterns = [
    # Home page - landing page
    path('', views.home, name='home'),
    
    # Step 1: Career credentials form
    path('roadmaps-form/', views.roadmaps_form, name='roadmaps_form'),
    
    # Step 2: Select roadmap option (receives POST from form)
    path('option-roadmaps/', views.option_roadmaps, name='option_roadmaps'),
    
    # Step 3: Display selected roadmap with timeline
    path('roadmap/', views.roadmap, name='roadmap'),
    
    # Additional pages (optional - create views if needed)
    # path('about/', views.about, name='about'),
    # path('contact/', views.contact, name='contact'),
    path('hackathon/', views.hackathon, name='hackathon'),

    path('dashboard/', views.dashboard, name='dashboard'),

    path('hackathon/', views.hackathon, name='hackathon'),

    path('internships/', views.internships, name='internships'),
    
    path('microsoft/', views.frontend_intern, name='microsoft'),

    path('google/', views.data_science_intern, name='google'),

    path('amazon/', views.amazon_intern, name='amazon'),

    path('figma/', views.figma_intern, name='figma'),

    path('cisco/', views.cisco_intern, name='cisco'),

    path('ibm/', views.ibm_intern, name='ibm'),

    path('contact/', views.contact, name='contact'),

    path('signin/', views.signin, name='signin'),

    path('signup/', views.signup, name='signup'),

    path('logout/', views.logout_view, name='logout'),

]