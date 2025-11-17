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


    # Roadmap related routes
    path('roadmaps/', views.roadmap_list, name='roadmap_list'),
    path('roadmap/<int:roadmap_id>/', views.roadmap_detail, name='roadmap_detail'),
    
    # Progress tracking - ✅ FIXED: Changed name to 'toggle_step'
    path('roadmap/<int:roadmap_id>/step/<int:step_id>/toggle/', 
         views.toggle_step, 
         name='toggle_step'),  # Changed from 'toggle_step_completion'

    # Save selected roadmap
    path('save-selected-roadmap/', views.save_selected_roadmap, name='save_selected_roadmap'),
    path('roadmap-options/', views.roadmap_options_home, name='roadmap_options_home'), 

    # Other pages
    path('dashboard/', views.dashboard, name='dashboard'),
    
    path('hackathon/', views.hackathon, name='hackathon'),
    path('hackathon/<int:hackathon_id>/', views.hackathon_detail, name='hackathon_detail'), 
    path('enroll/<int:hackathon_id>/', views.enroll_hackathon, name='enroll_hackathon'),
    path('hackathon/register/', views.hackathon_register, name='hackathon_register'),
    path('hackathon/<int:hackathon_id>/enroll/', views.enroll_hackathon, name='enroll_hackathon'),

    path('internships/', views.internships_view, name='internships'),
    path('apply_internship/', views.apply_internship, name='apply_internship'),
    path('internship/<path:title>/', views.internship_detail, name='internship_detail'),
        
    path('contact/', views.contact, name='contact'),

    # Authentication
    path('signup/', views.signup_view, name='signup'),
    path('signin/', views.signin_view, name='signin'),
    path('logout/', views.logout_view, name='logout'),
    path('select-interest/', views.select_interest, name='select_interest'),
    path('save-interest/', views.save_interest, name='save_interest'),
    
    # Available opportunities
    path('api/internships/available/', views.get_available_internships, name='available_internships'),
    path('api/hackathons/available/', views.get_available_hackathons, name='available_hackathons'),
    
    # Progress and stats
    path('api/progress/', views.get_progress_stats, name='progress_stats'),
    
    # Notifications
    path('api/notifications/<int:notif_id>/read/', views.mark_notification_read, name='mark_read'),
    
    # API Dashboard
    path("api/dashboard/", views.dashboard_data, name="dashboard_data"),


]