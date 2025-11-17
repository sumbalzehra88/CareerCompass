# CareerCompassapp/views.py
# Fixed version with correct function names and template paths

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Roadmap, RoadmapStep, UserSelectedRoadmap, UserRoadmapProgress
from .models import UserProfile
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.utils import timezone
from .models import Users, UserProfile
from django.db import connection
from datetime import datetime
import json
from django.views.decorators.csrf import csrf_protect
from django.db.models import Q
import re
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from datetime import datetime
import sqlite3
from django.shortcuts import render
from django.core.mail import EmailMessage
from matplotlib.pyplot import title
from django.db import IntegrityError
from .models import Hackathon, HackathonEnrollment, TeamMember
import traceback
from django.db import connection, IntegrityError
from django.db import connection
from django.shortcuts import render, redirect, get_object_or_404
from .models import Hackathon, HackathonEnrollment 
from .models import Internships, InternshipApplication
from django.db import models



from .models import UserProfile




@login_required
def option_roadmaps(request):
    """Process profile form and redirect to home"""

    if request.method == 'POST':
        # Collect user input from form
        user_data = {
            'current_role': request.POST.get('current_role', '').strip(),
            'experience': request.POST.get('experience', '').strip(),
            'education_level': request.POST.get('education_level', '').strip(),
            'degree': request.POST.get('degree', '').strip(),
            'country': request.POST.get('country', '').strip(),
            'preferred_industry': request.POST.get('preferred_industry', '').strip(),
            'current_skills': request.POST.get('current_skills', '').strip(),
            'target_skills': request.POST.get('target_skills', '').strip(),
            'career_goals': request.POST.get('career_goals', '').strip(),
            'timeframe': request.POST.get('timeframe', '').strip(),
        }

        # Save profile
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        profile.username = request.user.username
        profile.education = user_data['education_level']
        profile.degree = user_data['degree']
        profile.skills = user_data['current_skills']
        profile.country = user_data['country']
        profile.work_experience = user_data['experience']
        profile.user_interest = user_data['target_skills']
        profile.industry = user_data['preferred_industry']
        profile.career_goals = user_data['career_goals']

        import re
        match = re.search(r'\d+', user_data['timeframe']) if user_data['timeframe'] else None
        profile.time_frame = int(match.group()) if match else 0

        profile.save()

        # ✅ Redirect to Home after form submission
        return redirect('home')

    # GET → show profile form if needed
    profile = UserProfile.objects.filter(user=request.user).first()
    return render(request, 'CareerCompassapp/optionroadmaps.html', {'profile': profile})


@login_required
def roadmap_options_home(request):
    """Show roadmap options based on saved profile"""

    profile = UserProfile.objects.filter(user=request.user).first()
    if not profile:
        return redirect('option_roadmaps')  # safety

    # Filter roadmaps based on profile
    search_query = Q()
    if profile.industry:
        search_query |= Q(title__icontains=profile.industry) | Q(description__icontains=profile.industry)
    if profile.user_interest:
        for skill in profile.user_interest.split(','):
            search_query |= Q(title__icontains=skill.strip()) | Q(description__icontains=skill.strip())
    if profile.career_goals:
        search_query |= Q(title__icontains=profile.career_goals) | Q(description__icontains=profile.career_goals)
    if profile.work_experience:
        search_query |= Q(title__icontains=profile.work_experience) | Q(description__icontains=profile.work_experience)

    roadmaps = Roadmap.objects.filter(search_query).distinct()[:4] if search_query else Roadmap.objects.all()[:4]

    return render(request, 'CareerCompassapp/optionroadmaps.html', {'roadmap_options': roadmaps})


def home(request):
    """Home page - landing page"""
    profile = UserProfile.objects.filter(user=request.user).first() if request.user.is_authenticated else None
    return render(request, 'CareerCompassapp/home.html', {'profile': profile})

@login_required
def roadmap(request):
    """Display detailed roadmap with steps from database"""
    
    # Get user data from session
    user_data = request.session.get('user_data', {})
    
    # Get selected roadmap ID
    if request.method == 'POST':
        selected_roadmap_id = request.POST.get('selected_roadmap')
        request.session['selected_roadmap_id'] = selected_roadmap_id
    else:
        selected_roadmap_id = request.session.get('selected_roadmap_id')
    
    print("=" * 50)
    print(f"🗺️ Loading roadmap details")
    print(f"   Selected Roadmap ID: {selected_roadmap_id}")
    print("=" * 50)
    
    if not selected_roadmap_id:
        print("❌ No roadmap selected")
        return redirect('roadmaps_form')
    
    try:
        selected_roadmap_id = int(selected_roadmap_id)
        
        # Get roadmap from database
        roadmap = Roadmap.objects.get(roadmap_id=selected_roadmap_id)
        print(f"✅ Found roadmap: {roadmap.title}")
        print(f"   Description: {roadmap.description}")
        
        # Get steps from roadmap_steps table
        steps = RoadmapStep.objects.filter(roadmap=roadmap).order_by('step_number')
        print(f"\n📋 Found {steps.count()} steps from database:")
        
        # Format steps for template
        roadmap_steps = []
        for step in steps:
            content = step.step_content or ""
            
            # Parse step_content
            if ":" in content and len(content.split(":", 1)[0]) < 100:
                # If there's a colon and the part before is short, treat as title
                parts = content.split(":", 1)
                title = parts[0].strip()
                description = parts[1].strip()
            else:
                # Otherwise, use step number as title
                title = f"Step {step.step_number}"
                description = content
            
            roadmap_steps.append({
                'step': step.step_number,
                'title': title,
                'description': description,
            })
            print(f"   Step {step.step_number}: {title[:60]}")
        
        # Fallback if no steps found in database
        if not roadmap_steps:
            print("\n⚠️  No steps in database, using generated steps")
            roadmap_steps = generate_detailed_roadmap(user_data, str(selected_roadmap_id))
            print(f"   Generated {len(roadmap_steps)} fallback steps")
        
        # Save user's selection
        try:
            from django.utils import timezone
            selection, created = UserSelectedRoadmap.objects.get_or_create(
                user=request.user,
                roadmap=roadmap,
                defaults={'selected_at': timezone.now()}
            )
            
            if created:
                print(f"\n💾 Created new selection for {request.user.username}")
            else:
                print(f"\n💾 Updated selection for {request.user.username}")
        except Exception as e:
            print(f"\n⚠️  Could not save selection: {str(e)}")
        
        print("=" * 50)
        
        context = {
            'page_title': roadmap.title,
            'roadmap_steps': roadmap_steps,
            'roadmap': roadmap,
            'user_data': user_data
        }
        
        # Use correct template filename
        return render(request, 'CareerCompassapp/roadmaps_generated.html', context)
        
    except Roadmap.DoesNotExist:
        print(f"\n❌ Roadmap with ID {selected_roadmap_id} not found")
        return redirect('roadmaps_form')
    except ValueError:
        print(f"\n❌ Invalid roadmap ID format: {selected_roadmap_id}")
        return redirect('roadmaps_form')
    except Exception as e:
        print(f"\n❌ ERROR: {type(e).__name__}")
        print(f"   Message: {str(e)}")
        import traceback
        traceback.print_exc()
        return redirect('roadmaps_form')
# Helper Functions

def generate_roadmap_options(user_data):
    """Generate roadmap options based on user input"""
    industry = user_data.get('preferred_industry', '').lower()
    role = user_data.get('current_role', '').lower()
    experience = user_data.get('experience', '0')
    try:
        experience = int(experience)
    except (ValueError, TypeError):
        experience = 0
    
    target_skills = user_data.get('target_skills', '').lower()
    
    options = []
    
    # Technology-related options
    if any(keyword in industry for keyword in ['tech', 'software', 'it', 'computer', 'development', 'programming']):
        options.extend([
            {
                'id': 'fullstack',
                'title': 'Full-Stack Development',
                'subtitle': 'Complete Web Development Path',
                'icon': '💻'
            },
            {
                'id': 'data_science',
                'title': 'Data Science Track',
                'subtitle': 'Analytics & Machine Learning',
                'icon': '📊'
            },
            {
                'id': 'devops',
                'title': 'DevOps Engineering',
                'subtitle': 'Cloud & Infrastructure',
                'icon': '☁️'
            },
            {
                'id': 'mobile',
                'title': 'Mobile Development',
                'subtitle': 'iOS & Android Apps',
                'icon': '📱'
            }
        ])
    
    # Business-related options
    elif any(keyword in industry for keyword in ['business', 'management', 'marketing', 'sales', 'finance']):
        options.extend([
            {
                'id': 'product_mgmt',
                'title': 'Product Management',
                'subtitle': 'Strategy & Execution',
                'icon': '🎯'
            },
            {
                'id': 'digital_marketing',
                'title': 'Digital Marketing',
                'subtitle': 'Growth & Analytics',
                'icon': '📈'
            },
            {
                'id': 'consulting',
                'title': 'Business Consulting',
                'subtitle': 'Strategy & Operations',
                'icon': '💼'
            },
            {
                'id': 'entrepreneurship',
                'title': 'Entrepreneurship',
                'subtitle': 'Startup & Innovation',
                'icon': '🚀'
            }
        ])
    
    # Healthcare-related options
    elif any(keyword in industry for keyword in ['health', 'medical', 'clinical', 'hospital', 'nursing']):
        options.extend([
            {
                'id': 'clinical_path',
                'title': 'Clinical Advancement',
                'subtitle': 'Patient Care Excellence',
                'icon': '🏥'
            },
            {
                'id': 'health_admin',
                'title': 'Healthcare Administration',
                'subtitle': 'Management & Operations',
                'icon': '📋'
            },
            {
                'id': 'health_tech',
                'title': 'Healthcare Technology',
                'subtitle': 'Digital Health Solutions',
                'icon': '⚕️'
            },
            {
                'id': 'research',
                'title': 'Medical Research',
                'subtitle': 'Clinical & Academic Research',
                'icon': '🔬'
            }
        ])
    
    # Education-related options
    elif any(keyword in industry for keyword in ['education', 'teaching', 'academic', 'training']):
        options.extend([
            {
                'id': 'teaching_excellence',
                'title': 'Teaching Excellence',
                'subtitle': 'Advanced Pedagogy',
                'icon': '📚'
            },
            {
                'id': 'ed_leadership',
                'title': 'Educational Leadership',
                'subtitle': 'Administration & Policy',
                'icon': '🎓'
            },
            {
                'id': 'curriculum_design',
                'title': 'Curriculum Design',
                'subtitle': 'Instructional Innovation',
                'icon': '✏️'
            },
            {
                'id': 'ed_tech',
                'title': 'Educational Technology',
                'subtitle': 'Digital Learning Solutions',
                'icon': '💡'
            }
        ])
    
    # Default options if industry doesn't match
    if not options:
        options = [
            {
                'id': 'leadership',
                'title': 'Leadership Track',
                'subtitle': 'Management & Strategy',
                'icon': '👔'
            },
            {
                'id': 'specialist',
                'title': 'Technical Specialist',
                'subtitle': 'Deep Expertise Path',
                'icon': '🎯'
            },
            {
                'id': 'consultant',
                'title': 'Advisory Role',
                'subtitle': 'Consulting & Guidance',
                'icon': '💡'
            },
            {
                'id': 'entrepreneur',
                'title': 'Independent Path',
                'subtitle': 'Freelance & Business',
                'icon': '🌟'
            }
        ]
    
    return options[:4]  # Return max 4 options

def generate_detailed_roadmap(user_data, selected_roadmap_id):
    """Generate detailed roadmap steps based on user data and selection"""
    experience = user_data.get('experience', '0')
    try:
        experience = int(experience)
    except (ValueError, TypeError):
        experience = 0
    
    industry = user_data.get('preferred_industry', '')
    current_skills = user_data.get('current_skills', '')
    target_skills = user_data.get('target_skills', '')
    career_goals = user_data.get('career_goals', 'advance your career')
    timeframe = user_data.get('timeframe', '1-2 years')
    
    # Base roadmap that adapts to user's experience level
    if experience < 2:  # Entry level
        steps = [
            {
                "step": 1,
                "title": "Foundation Assessment",
                "description": f"Evaluate your current {current_skills if current_skills else 'foundational'} skills and identify core competencies needed in {industry if industry else 'your field'}."
            },
            {
                "step": 2,
                "title": "Skill Building Phase",
                "description": f"Develop {target_skills if target_skills else 'key technical and soft skills'} through structured learning, courses, and certifications."
            },
            {
                "step": 3,
                "title": "Practical Experience",
                "description": f"Apply new skills through projects, internships, or entry-level positions in {industry if industry else 'your chosen field'}."
            },
            {
                "step": 4,
                "title": "Portfolio Development",
                "description": "Create a compelling portfolio showcasing your projects, achievements, and practical applications of your skills."
            },
            {
                "step": 5,
                "title": "Professional Network",
                "description": f"Build connections within {industry if industry else 'your industry'} through events, online communities, and mentorship programs."
            },
            {
                "step": 6,
                "title": "Career Launch",
                "description": f"Secure your target role and begin working towards {career_goals} within {timeframe if timeframe else 'your desired timeframe'}."
            }
        ]
    elif experience < 5:  # Mid-level
        steps = [
            {
                "step": 1,
                "title": "Strategic Assessment",
                "description": f"Analyze your current position and define clear path to {career_goals}."
            },
            {
                "step": 2,
                "title": "Advanced Skill Development",
                "description": f"Master advanced {target_skills if target_skills else 'technical capabilities'} and develop leadership skills."
            },
            {
                "step": 3,
                "title": "Project Leadership",
                "description": f"Lead high-impact projects and initiatives within {industry if industry else 'your organization'}."
            },
            {
                "step": 4,
                "title": "Industry Expertise",
                "description": f"Build recognition as a subject matter expert in {industry if industry else 'your domain'}."
            },
            {
                "step": 5,
                "title": "Team & Mentorship",
                "description": "Develop others while expanding your professional influence and building your leadership brand."
            },
            {
                "step": 6,
                "title": "Senior Role Transition",
                "description": f"Secure senior-level position aligned with {career_goals} and establish yourself as a key decision-maker."
            }
        ]
    else:  # Senior level (5+ years)
        steps = [
            {
                "step": 1,
                "title": "Executive Vision",
                "description": f"Define long-term strategic vision for your role in {industry if industry else 'your industry'}."
            },
            {
                "step": 2,
                "title": "Thought Leadership",
                "description": f"Establish yourself as a thought leader through {target_skills if target_skills else 'deep expertise'} and industry contributions."
            },
            {
                "step": 3,
                "title": "Organizational Impact",
                "description": "Drive significant organizational change, innovation, and measurable business results."
            },
            {
                "step": 4,
                "title": "Industry Influence",
                "description": f"Shape {industry if industry else 'industry'} direction through speaking engagements, publications, and advisory roles."
            },
            {
                "step": 5,
                "title": "Legacy Building",
                "description": "Mentor next generation leaders, contribute to industry standards, and build lasting impact."
            },
            {
                "step": 6,
                "title": "Executive Achievement",
                "description": f"Achieve {career_goals} and establish your executive legacy in the field."
            }
        ]
    
    return steps

def get_roadmap_title(roadmap_id, user_data):
    """Generate page title based on roadmap and user data"""
    industry = user_data.get('preferred_industry', 'Career')
    
    roadmap_titles = {
        'fullstack': 'Full-Stack Development Roadmap',
        'data_science': 'Data Science Career Roadmap',
        'devops': 'DevOps Engineering Roadmap',
        'mobile': 'Mobile Development Roadmap',
        'product_mgmt': 'Product Management Roadmap',
        'digital_marketing': 'Digital Marketing Roadmap',
        'consulting': 'Business Consulting Roadmap',
        'entrepreneurship': 'Entrepreneurship Roadmap',
        'clinical_path': 'Clinical Advancement Roadmap',
        'health_admin': 'Healthcare Administration Roadmap',
        'health_tech': 'Healthcare Technology Roadmap',
        'research': 'Medical Research Roadmap',
        'leadership': 'Leadership Development Roadmap',
        'specialist': 'Technical Specialist Roadmap',
        'consultant': 'Advisory Career Roadmap',
        'entrepreneur': 'Independent Career Roadmap',
        'teaching_excellence': 'Teaching Excellence Roadmap',
        'ed_leadership': 'Educational Leadership Roadmap',
        'curriculum_design': 'Curriculum Design Roadmap',
        'ed_tech': 'Educational Technology Roadmap',
    }
    
    return roadmap_titles.get(roadmap_id, f'Your {industry} Roadmap')

@login_required
def save_selected_roadmap(request):
    if request.method == "POST":
        roadmap_id = request.POST.get("selected_roadmap")

        if not roadmap_id:
            return JsonResponse({"status": "error", "message": "No roadmap selected."}, status=400)

        # Get or create selection record
        selected, created = UserSelectedRoadmap.objects.get_or_create(
            user=request.user,
            roadmap_id=roadmap_id
        )

        # Pre-populate progress for all steps
        steps = RoadmapStep.objects.filter(roadmap_id=roadmap_id)
        for step in steps:
            UserRoadmapProgress.objects.get_or_create(
                user=request.user,
                roadmap_id=roadmap_id,
                step=step
            )

        return JsonResponse({
            "status": "success",
            "message": "Roadmap saved successfully!"
        })

    return JsonResponse({"status": "error", "message": "Invalid request method."}, status=405)
    

@login_required
def roadmap_detail(request, roadmap_id):
    """Display detailed roadmap with real progress tracking - NO DB CHANGES"""
    roadmap = get_object_or_404(Roadmap, roadmap_id=roadmap_id)
    steps = RoadmapStep.objects.filter(roadmap=roadmap).order_by('step_number')

    # Ensure user has selected this roadmap
    user_selected, created = UserSelectedRoadmap.objects.get_or_create(
        user=request.user,
        roadmap=roadmap,
        defaults={'selected_at': timezone.now()}
    )

    # Get progress for each step
    total_steps = steps.count()
    completed_count = 0
    roadmap_steps_data = []

    for step in steps:
        # Get or create progress record using EXISTING table structure
        progress, _ = UserRoadmapProgress.objects.get_or_create(
            user=request.user,
            roadmap=roadmap,
            step=step,
            defaults={'is_completed': False}
        )
        
        if progress.is_completed:
            completed_count += 1
            

        roadmap_steps_data.append({
            'id': step.step_id,
            'title': step.step_content or f"Step {step.step_number}",  # ✅ Use actual content
            'description': step.step_content or '',
            'is_completed': progress.is_completed,
            'step_number': step.step_number,
        })

    # Calculate progress
    progress_percentage = round((completed_count / total_steps) * 100) if total_steps > 0 else 0
    remaining_steps = total_steps - completed_count

    context = {
        'page_title': roadmap.title,
        'roadmap': roadmap,
        'steps': roadmap_steps_data,
        'progress_percentage': progress_percentage,
        'completed_steps': completed_count,
        'total_steps': total_steps,
        'remaining_steps': remaining_steps,
        'roadmap_steps': json.dumps(roadmap_steps_data),
    }

    return render(request, 'CareerCompassapp/roadmaps_generated.html', context)


@login_required
@require_POST
def toggle_step(request, roadmap_id, step_id):
    """Toggle step completion - Works with EXISTING database structure"""
    try:
        roadmap = get_object_or_404(Roadmap, roadmap_id=roadmap_id)
        step = get_object_or_404(RoadmapStep, step_id=step_id, roadmap=roadmap)
        
        # Get or create progress record
        progress, created = UserRoadmapProgress.objects.get_or_create(
            user=request.user,
            roadmap=roadmap,
            step=step,
            defaults={'is_completed': False}
        )
        
        # Toggle completion status
        progress.is_completed = not progress.is_completed
        progress.save()
        
        # Calculate new progress
        total_steps = RoadmapStep.objects.filter(roadmap=roadmap).count()
        completed_steps = UserRoadmapProgress.objects.filter(
            user=request.user,
            roadmap=roadmap,
            is_completed=True
        ).count()
        
        progress_percentage = round((completed_steps / total_steps) * 100) if total_steps > 0 else 0
        remaining_steps = total_steps - completed_steps
        
        return JsonResponse({
            'success': True,
            'is_completed': progress.is_completed,
            'progress_percentage': progress_percentage,
            'completed_steps': completed_steps,
            'remaining_steps': remaining_steps
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)
    
@login_required
def mark_step_complete(request, roadmap_id, step_id):
    """Mark a roadmap step as complete (using session to simulate progress)"""
    roadmap = get_object_or_404(Roadmap, roadmap_id=roadmap_id)
    steps = RoadmapStep.objects.filter(roadmap=roadmap)
    total_steps = steps.count()

    # Track completed steps in user session
    completed_steps = request.session.get(f'completed_steps_{roadmap_id}', [])
    if step_id not in completed_steps:
        completed_steps.append(step_id)
        request.session[f'completed_steps_{roadmap_id}'] = completed_steps

    # Update progress dynamically
    completed_count = len(completed_steps)
    progress_percentage = round((completed_count / total_steps) * 100) if total_steps > 0 else 0

    # Redirect back to roadmap detail
    return redirect('roadmap_detail', roadmap_id=roadmap_id)


@login_required
def roadmap_list(request):
    """List all available roadmaps with user progress"""
    roadmaps = Roadmap.objects.all()
    user_selected_roadmaps = UserSelectedRoadmap.objects.filter(user=request.user)

    roadmap_data = []
    for roadmap in roadmaps:
        steps = RoadmapStep.objects.filter(roadmap=roadmap)
        total_steps = steps.count()
        completed_steps = request.session.get(f'completed_steps_{roadmap.roadmap_id}', [])
        completed_count = len(completed_steps)
        progress_percentage = round((completed_count / total_steps) * 100) if total_steps > 0 else 0

        roadmap_data.append({
            'roadmap': roadmap,
            'progress': progress_percentage,
            'is_selected': user_selected_roadmaps.filter(roadmap=roadmap).exists()
        })

    context = {
        'page_title': 'Career Roadmaps',
        'roadmaps': roadmap_data,
    }

    return render(request, 'CareerCompassapp/roadmaps_generated.html', context)

# Optional additional views
def about(request):
    """About page"""
    return render(request, 'CareerCompassapp/about.html')

def contactus(request):
    return render(request, 'CareerCompassapp/contact.html')



def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        terms = request.POST.get('terms')

        # Validations
        if password1 != password2:
            messages.error(request, 'Passwords do not match')
            return render(request, 'CareerCompassapp/Signup.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return render(request, 'CareerCompassapp/Signup.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered')
            return render(request, 'CareerCompassapp/Signup.html')

        if not terms:
            messages.error(request, 'You must agree to terms and conditions')
            return render(request, 'CareerCompassapp/Signup.html')

        # Create user
        user = User.objects.create_user(username=username, email=email, password=password1)
        user.save()

        # 🧹 Delete any leftover profiles with the same username or email (cleanup)
        UserProfile.objects.filter(username=username).delete()

        # ✅ Create a completely blank profile for this new user
        UserProfile.objects.create(
            user=user,
            username=username,
            education='',
            degree='',
            skills='',
            country='',
            work_experience='',
            industry='',
            career_goals='',
            user_interest='',
            time_frame=0
        )

        messages.success(request, 'Account created successfully! Please sign in.')
        return redirect('signin')

    return render(request, 'CareerCompassapp/Signup.html')



# --- SIGN IN ---
def signin_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user = User.objects.get(email=email)
            username = user.username
        except User.DoesNotExist:
            messages.error(request, "Invalid email or password.")
            return redirect("signin")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)

            # Make sure profile exists
            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={'username': user.username}
            )

            # Check if the profile is incomplete
            is_first_time = not all([
                profile.education.strip() if profile.education else '',
                profile.skills.strip() if profile.skills else '',
                profile.country.strip() if profile.country else '',
            ])

            print(f"DEBUG → education='{profile.education}', skills='{profile.skills}', country='{profile.country}'")
            print(f"DEBUG → is_first_time={is_first_time}")

            if is_first_time:
                return redirect("roadmaps_form")  # The form to fill first time

            return redirect("home")  # Regular home page after that

        else:
            messages.error(request, "Invalid email or password.")
            return redirect("signin")

    return render(request, 'CareerCompassapp/Signin.html')


# ==========================================
# SIGNIN VIEW - Check first-time login
# ==========================================
# ==========================================
# SIGNIN VIEW - Check first-time login
# ==========================================
def signin_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user = User.objects.get(email=email)
            username = user.username
        except User.DoesNotExist:
            messages.error(request, "Invalid email or password.")
            return redirect("signin")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)

            # Ensure user profile exists (only one per user)
            profiles = UserProfile.objects.filter(user=user)
            if profiles.exists():
                # Handle duplicates if any
                if profiles.count() > 1:
                    profile = profiles.order_by('profile_id').first()
                    profiles.exclude(profile_id=profile.profile_id).delete()
                else:
                    profile = profiles.first()
            else:
                # Create if none exists
                profile = UserProfile.objects.create(
                    user=user,
                    username=user.username
                )

            # 🟢 Check if profile is complete - MUST have these 3 core fields
            is_first_time = not all([
                profile.education and profile.education.strip(),
                profile.skills and profile.skills.strip(),
                profile.country and profile.country.strip(),
            ])

            print(f"👀 First time check for {user.username}: {is_first_time}")
            print(f"   Education: '{profile.education}'")
            print(f"   Skills: '{profile.skills}'")
            print(f"   Country: '{profile.country}'")
            
            if is_first_time:
                print(f"🎯 First-time/incomplete profile for {user.username} - redirecting to form")
                print("=" * 60)
                print(f"🧪 User: {user.username}")
                print(f"Education: '{profile.education}'")
                print(f"Skills: '{profile.skills}'")
                print(f"Country: '{profile.country}'")
                print(f"Calculated is_first_time: {is_first_time}")
                print("=" * 60)
                return redirect("roadmaps_form")

            # Profile is complete → go home
            print(f"✅ Complete profile for {user.username} - redirecting to home")
            return redirect("home")
        
            

        else:
            messages.error(request, "Invalid email or password.")
            return redirect("signin")
        
        


    return render(request, 'CareerCompassapp/Signin.html')




# ==========================================
# SELECT INTEREST - First-time setup
# ==========================================
@login_required
def select_interest(request):
    """Show interest selection page for first-time users"""
    profile, created = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={'username': request.user.username}
    )
    
    # If user already has an interest selected, redirect to home
    if profile.user_interest and profile.user_interest.strip() != '':
        print(f"⚠️ User {request.user.username} already has interest: {profile.user_interest}")
        return redirect('home')
    
    print(f"📋 Showing interest selection page to {request.user.username}")
    return render(request, 'CareerCompassapp/Select_interest.html')


# ==========================================
# SAVE INTEREST - Store selection
# ==========================================
@require_POST
@login_required
def save_interest(request):
    """Save the user's selected interest"""
    try:
        data = json.loads(request.body)
        interest = data.get('interest')
        
        if not interest:
            return JsonResponse({'error': 'Interest is required'}, status=400)
        
        # Interest mapping (map IDs to readable names)
        interest_map = {
            'web-dev': 'Web Development',
            'mobile-dev': 'Mobile Development',
            'ai-ml': 'AI & Machine Learning',
            'data-science': 'Data Science',
            'devops': 'DevOps & Cloud',
            'cyber-security': 'Cybersecurity',
            'game-dev': 'Game Development',
            'blockchain': 'Blockchain',
            'ui-ux': 'UI/UX Design'
        }
        
        interest_name = interest_map.get(interest, interest)
        
        # Get or create profile
        profile, created = UserProfile.objects.get_or_create(
            user=request.user,
            defaults={'username': request.user.username}
        )
        
        # Save the interest
        profile.user_interest = interest_name
        profile.save()
        
        print(f"✅ Interest saved for {request.user.username}: {interest_name}")
        
        return JsonResponse({
            'success': True,
            'message': 'Interest saved successfully'
        })
    
    except Exception as e:
        print(f"❌ Error saving interest: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)


# ==========================================
# ROADMAPS FORM - Merge with existing profile data
# ==========================================
# ==========================================
# ROADMAPS FORM - First-time create, then edit mode
# ==========================================
@login_required
def roadmaps_form(request):
    if request.method == 'POST':
        print("=" * 50)
        print("🔍 Saving profile data from roadmaps_form")
        print("=" * 50)
        
        # Get form data
        education = request.POST.get('education_level', '').strip()
        degree = request.POST.get('degree', '').strip()
        skills = request.POST.get('current_skills', '').strip()
        country = request.POST.get('country', '').strip()
        experience = request.POST.get('experience', '').strip()
        industry = request.POST.get('preferred_industry', '').strip()
        career_goals = request.POST.get('career_goals', '').strip()
        target_skills = request.POST.get('target_skills', '').strip()
        timeframe = request.POST.get('timeframe', '').strip()
        current_role = request.POST.get('current_role', '').strip()
        
        # Validate required fields
        if not all([education, degree, skills, country, industry]):
            messages.error(request, "Please fill in all required fields")
            try:
                profile = UserProfile.objects.get(user=request.user)
                context = {'profile': profile}
                return render(request, 'CareerCompassapp/RoadmapsForm.html', context)
            except UserProfile.DoesNotExist:
                return render(request, 'CareerCompassapp/RoadmapsForm.html')
        
        try:
            # Get or create profile
            profile, created = UserProfile.objects.get_or_create(
                user=request.user,
                defaults={'username': request.user.username}
            )

            # Update ALL fields
            profile.education = education
            profile.degree = degree
            profile.skills = skills
            profile.country = country
            profile.work_experience = experience
            profile.industry = industry
            profile.career_goals = career_goals
            profile.user_interest = target_skills

            # Handle timeframe
            try:
                import re
                match = re.search(r'\d+', timeframe)
                profile.time_frame = int(match.group()) if match else 0
            except (ValueError, TypeError):
                profile.time_frame = 0

            profile.save()
            print(f"💾 Profile saved successfully for {request.user.username}")
            
            # Store data in session for roadmap generation
            request.session['user_data'] = {
                'current_role': current_role,
                'experience': experience,
                'education_level': education,
                'degree': degree,
                'country': country,
                'preferred_industry': industry,
                'current_skills': skills,
                'target_skills': target_skills,
                'career_goals': career_goals,
                'timeframe': timeframe
            }
            
            messages.success(request, "Profile saved successfully!")
            return redirect('home')

        except Exception as e:
            print(f"❌ Error saving profile: {str(e)}")
            import traceback
            traceback.print_exc()
            messages.error(request, "Error saving profile. Please try again.")
            return render(request, 'CareerCompassapp/RoadmapsForm.html')

    # GET request - show form (pre-filled if profile exists)
    try:
        profile = UserProfile.objects.get(user=request.user)
        context = {'profile': profile}
        return render(request, 'CareerCompassapp/RoadmapsForm.html', context)
    except UserProfile.DoesNotExist:
        return render(request, 'CareerCompassapp/RoadmapsForm.html')


def social_auth(request, provider):
    messages.info(request, f'Social auth with {provider} coming soon!')
    return redirect('Signin')

def logout_view(request):
    logout(request)
    return redirect("home")

def internships_view(request):
    conn = sqlite3.connect("career_compass.db")
    cursor = conn.cursor()

    current_date = datetime.now().strftime("%Y-%m-%d")

    # Get filters
    search = request.GET.get("search", "").strip()
    location = request.GET.get("location", "")
    stipend = request.GET.get("stipend", "")

    query = """
        SELECT i.title, c.name AS company_name, i.location, i.duration,
               i.skills_required, i.deadline, i.description, i.stipend
        FROM internships i
        LEFT JOIN companies c ON i.company_id = c.company_id
        WHERE i.deadline >= ?
    """
    params = [current_date]

    if search:
        query += " AND (LOWER(c.name) LIKE ? OR LOWER(i.skills_required) LIKE ?)"
        params.extend([f"%{search.lower()}%", f"%{search.lower()}%"])

    if location:
        query += " AND LOWER(i.location) = ?"
        params.append(location.lower())

    if stipend:
        if stipend == "500-800":
            query += " AND i.stipend BETWEEN 500 AND 800"
        elif stipend == "800-1200":
            query += " AND i.stipend BETWEEN 800 AND 1200"
        elif stipend == "1200+":
            query += " AND i.stipend >= 1200"

    query += " ORDER BY i.deadline ASC"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    internships = [
        {
            "title": r[0],
            "company_name": r[1],
            "location": r[2],
            "duration": r[3],
            "skills_required": r[4],
            "deadline": r[5],
            "description": r[6],
            "stipend": r[7],
        }
        for r in rows
    ]

    # Pagination
    paginator = Paginator(internships, 6)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "CareerCompassapp/internships.html", {
        "internships": page_obj,
        "search": search,
        "location": location,
        "stipend": stipend,
    })


@csrf_exempt
@login_required
def apply_internship(request):
    internship = None  # Initialize outside try

    if request.method == "POST":
        fullname = request.POST.get("fullname")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        linkedin = request.POST.get("linkedin")
        portfolio = request.POST.get("portfolio")
        cover_letter = request.POST.get("cover_letter")
        cv = request.FILES.get("cv")
        internship_title = request.POST.get("internship_title", "Unknown Internship")

        try:
            internship = Internships.objects.filter(title=internship_title).first()
            if internship:
                InternshipApplication.objects.create(
                    user=request.user,
                    internship=internship,
                    status='Pending'
                )
                print(f"✅ Application saved for {request.user.username}")
            else:
                print(f"⚠️ Internship not found: {internship_title}")

        except Exception as e:
            print(f"⚠️ Could not save application: {e}")

        # Make sure to check if internship is None
        internship_name = internship.title if internship else internship_title

        # Email sending code
        subject = f"New Internship Application: {internship_name}"
        message = (
            f"Dear HR Team,\n\n"
            f"You have received a new application for the internship '{internship_name}'.\n\n"
            f"Applicant Details:\n"
            f"Name: {fullname}\n"
            f"Email: {email}\n"
            f"Phone: {phone}\n"
            f"LinkedIn: {linkedin or 'Not provided'}\n"
            f"Portfolio: {portfolio or 'Not provided'}\n\n"
            f"Cover Letter:\n{cover_letter}\n\n"
            f"Please find the attached CV if available.\n\n"
            f"Regards,\nCareerCompass System"
        )

        company_email = "khadijasehar10@gmail.com"
        mail = EmailMessage(
            subject,
            message,
            from_email="CareerCompass <yourcompanyemail@gmail.com>",
            to=[company_email],
            reply_to=[email]
        )
        if cv:
            mail.attach(cv.name, cv.read(), cv.content_type)
        try:
            mail.send()
            print("✅ Email sent successfully.")
        except Exception as e:
            print("❌ Email sending failed:", e)

        return render(request, "CareerCompassapp/apply_success.html", {
            "name": fullname,
            "title": internship_name
        })

def internship_detail(request, title):
    import sqlite3
    from django.shortcuts import render

    conn = sqlite3.connect("career_compass.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT i.title, c.name AS company_name, i.location, i.duration,
               i.skills_required, i.deadline, i.description, i.stipend
        FROM internships i
        LEFT JOIN companies c ON i.company_id = c.company_id
        WHERE i.title = ?
    """, (title,))

    data = cursor.fetchone()
    conn.close()

    if not data:
        return render(request, "CareerCompassapp/error.html", {"message": "Internship not found."})

    internship = {
        "title": data[0],
        "company_name": data[1],
        "location": data[2],
        "duration": data[3],
        "skills_required": data[4],
        "deadline": data[5],
        "description": data[6],
        "stipend": data[7],
    }

    return render(request, "CareerCompassapp/internship_detail.html", {"internship": internship})

@login_required
def get_dashboard_data(request):
    """Main dashboard API - returns all user-specific data"""
    user_id = request.user.id
    
    with connection.cursor() as cursor:
        # Get user profile
        cursor.execute("""
            SELECT username, education, degree, skills, country, work_experience, user_interest
            FROM user_profile WHERE user_id = %s
        """, [user_id])
        profile = cursor.fetchone()
        
        # Get applied internships
        cursor.execute("""
            SELECT i.internship_id, i.title, c.name as company, i.location, 
                   i.deadline, a.status, a.applied_on
            FROM applications a
            JOIN internships i ON a.internship_id = i.internship_id
            LEFT JOIN companies c ON i.company_id = c.company_id
            WHERE a.user_id = %s
            ORDER BY a.applied_on DESC
        """, [user_id])
        applied_internships = cursor.fetchall()
        
        # Get user's hackathon teams
        cursor.execute("""
            SELECT h.hackathon_id, h.name, h.start_date, h.end_date, 
                   t.team_name, h.registration_date
            FROM hackathon_teams t
            JOIN hackathons h ON t.hackathon_id = h.hackathon_id
            WHERE t.user_id = %s
            ORDER BY h.start_date DESC
        """, [user_id])
        user_hackathons = cursor.fetchall()
        
        # Get roadmap progress
        cursor.execute("""
            SELECT r.title, COUNT(rs.step_id) as total_steps,
                   usr.selected_at
            FROM user_selected_roadmaps usr
            JOIN roadmaps r ON usr.roadmap_id = r.roadmap_id
            LEFT JOIN roadmap_steps rs ON r.roadmap_id = rs.roadmap_id
            WHERE usr.user_id = %s
            GROUP BY r.roadmap_id
        """, [user_id])
        roadmaps = cursor.fetchall()
        
        # Get unread notifications
        cursor.execute("""
            SELECT notif_id, type, message, created_at, is_read
            FROM notifications
            WHERE user_id = %s AND is_read = 0
            ORDER BY created_at DESC
            LIMIT 10
        """, [user_id])
        notifications = cursor.fetchall()
    
    return JsonResponse({
        'profile': {
            'name': profile[0] if profile else 'User',
            'education': profile[1] if profile else '',
            'degree': profile[2] if profile else '',
            'skills': profile[3].split(',') if profile and profile[3] else [],
            'country': profile[4] if profile else '',
        },
        'internships': [
            {
                'id': row[0],
                'title': row[1],
                'company': row[2],
                'location': row[3],
                'deadline': row[4],
                'status': row[5],
                'applied_on': row[6]
            } for row in applied_internships
        ],
        'hackathons': [
            {
                'id': row[0],
                'name': row[1],
                'start_date': row[2],
                'end_date': row[3],
                'team_name': row[4],
                'registration_date': row[5]
            } for row in user_hackathons
        ],
        'roadmaps': [
            {
                'title': row[0],
                'total_steps': row[1],
                'selected_at': row[2]
            } for row in roadmaps
        ],
        'notifications': [
            {
                'id': row[0],
                'type': row[1],
                'message': row[2],
                'created_at': row[3],
                'is_read': row[4]
            } for row in notifications
        ]
    })


@login_required
def get_available_internships(request):
    """Get internships user hasn't applied to yet, matching their skills"""
    user_id = request.user.id
    
    with connection.cursor() as cursor:
        # Get user skills
        cursor.execute("SELECT skills FROM user_profile WHERE user_id = %s", [user_id])
        result = cursor.fetchone()
        user_skills = result[0].lower().split(',') if result and result[0] else []
        
        # Get internships not applied to yet
        cursor.execute("""
            SELECT i.internship_id, i.title, c.name as company, i.location, 
                   i.deadline, i.skills_required, i.description
            FROM internships i
            LEFT JOIN companies c ON i.company_id = c.company_id
            WHERE i.internship_id NOT IN (
                SELECT internship_id FROM applications WHERE user_id = %s
            )
            AND i.deadline >= date('now')
            ORDER BY i.deadline ASC
        """, [user_id])
        internships = cursor.fetchall()
    
    # Match skills and sort
    matched_internships = []
    for row in internships:
        required_skills = row[5].lower().split(',') if row[5] else []
        match_count = sum(1 for skill in user_skills if any(skill.strip() in req.strip() for req in required_skills))
        
        matched_internships.append({
            'id': row[0],
            'title': row[1],
            'company': row[2],
            'location': row[3],
            'deadline': row[4],
            'skills_required': row[5],
            'description': row[6],
            'match_score': match_count
        })
    
    # Sort by match score
    matched_internships.sort(key=lambda x: x['match_score'], reverse=True)
    
    return JsonResponse({'internships': matched_internships})


@login_required
def get_available_hackathons(request):
    """Get upcoming hackathons user hasn't joined"""
    user_id = request.user.id
    
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT h.hackathon_id, h.name, h.start_date, h.end_date, 
                   h.details, h.registration_date
            FROM hackathons h
            WHERE h.hackathon_id NOT IN (
                SELECT hackathon_id FROM hackathon_teams WHERE user_id = %s
            )
            AND h.registration_date >= date('now')
            ORDER BY h.start_date ASC
        """, [user_id])
        hackathons = cursor.fetchall()
    
    return JsonResponse({
        'hackathons': [
            {
                'id': row[0],
                'name': row[1],
                'start_date': row[2],
                'end_date': row[3],
                'details': row[4],
                'registration_date': row[5]
            } for row in hackathons
        ]
    })


@login_required
def get_progress_stats(request):
    """Calculate user's overall progress statistics"""
    user_id = request.user.id
    
    with connection.cursor() as cursor:
        # Roadmap completion
        cursor.execute("""
            SELECT COUNT(DISTINCT usr.roadmap_id) as selected_roadmaps
            FROM user_selected_roadmaps usr
            WHERE usr.user_id = %s
        """, [user_id])
        roadmap_count = cursor.fetchone()[0]
        
        # Application stats
        cursor.execute("""
            SELECT status, COUNT(*) as count
            FROM applications
            WHERE user_id = %s
            GROUP BY status
        """, [user_id])
        app_stats = dict(cursor.fetchall())
        
        # Activity heatmap (last 365 days)
        cursor.execute("""
            SELECT DATE(created_at) as date, COUNT(*) as activity
            FROM (
                SELECT created_at FROM applications WHERE user_id = %s
                UNION ALL
                SELECT selected_at FROM user_selected_roadmaps WHERE user_id = %s
            )
            WHERE created_at >= date('now', '-365 days')
            GROUP BY DATE(created_at)
            ORDER BY date
        """, [user_id, user_id])
        activity = cursor.fetchall()
    
    # Calculate roadmap progress percentage (simplified)
    progress_percent = min(int((roadmap_count / 7) * 100), 100) if roadmap_count else 0
    
    return JsonResponse({
        'progress_percent': progress_percent,
        'roadmaps_selected': roadmap_count,
        'applications': {
            'total': sum(app_stats.values()),
            'pending': app_stats.get('Pending', 0),
            'accepted': app_stats.get('Accepted', 0),
            'rejected': app_stats.get('Rejected', 0)
        },
        'activity_heatmap': [
            {'date': row[0], 'count': row[1]} for row in activity
        ]
    })


@login_required
def mark_notification_read(request, notif_id):
    """Mark a notification as read"""
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE notifications 
                SET is_read = 1 
                WHERE notif_id = ? AND user_id = %s
            """, [notif_id, request.user.id])
        
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Invalid method'}, status=400)

def dashboard(request):
    return render(request, 'CareerCompassapp/Dashboard.html')

def contact(request):
    return render(request, 'CareerCompassapp/contact.html')



from django.shortcuts import render, get_object_or_404
from .models import Hackathon
from datetime import datetime
def safe_parse_datetime(value):
    if isinstance(value, str):  # sirf tab convert kare jab string ho
        return datetime.fromisoformat(value)
    return value

def hackathon_detail(request, hackathon_id):
    selected_hackathon = get_object_or_404(Hackathon, hackathon_id = hackathon_id)
    hackathons = Hackathon.objects.order_by('-created_at')[:5]
    return render(request, 'CareerCompassapp/hackathon.html', {
        'hackathons': hackathons,
        'selected_hackathon': selected_hackathon
    })

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import UserProfile

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Hackathon, UserProfile

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Hackathon, UserProfile

def hackathon(request, hackathon_id=None):
    if hackathon_id:
        # Individual hackathon detail page
        selected_hackathon = get_object_or_404(Hackathon, pk=hackathon_id)
        
        # Get skill-based recommendations for sidebar
        if request.user.is_authenticated:
            try:
                # Get user profile
                user_profile = UserProfile.objects.get(user_id=request.user.id)
                
                # Extract and clean user skills
                user_skills = []
                if user_profile.skills:
                    user_skills = [skill.strip().lower() for skill in user_profile.skills.split(',') if skill.strip()]
                
                # Extract and clean user interests
                user_interests = []
                if user_profile.user_interest:
                    user_interests = [interest.strip().lower() for interest in user_profile.user_interest.split(',') if interest.strip()]
                
                # Combine skills and interests
                user_keywords = set(user_skills + user_interests)
                
                if user_keywords:
                    # Get all hackathons except current one
                    all_hackathons = Hackathon.objects.exclude(pk=hackathon_id)
                    
                    recommended_hackathons = []
                    for hackathon in all_hackathons:
                        if hackathon.required_skills:
                            hackathon_skills = [skill.strip().lower() for skill in hackathon.required_skills.split(',') if skill.strip()]
                            
                            # Find matching skills
                            matching_items = user_keywords & set(hackathon_skills)
                            
                            if matching_items:
                                hackathon.match_count = len(matching_items)
                                hackathon.matching_skills_list = list(matching_items)
                                recommended_hackathons.append(hackathon)
                    
                    # Sort by match count (descending) then by start_date and limit to 5
                    
                    if recommended_hackathons:
                        recommended_hackathons.sort(key=lambda x: x.match_count, reverse=True)
                        hackathons = recommended_hackathons[:5]
                    else:
                        # No skill matches, show recent hackathons
                        hackathons = []
                else:
                    # User has no skills/interests set
                    hackathons = Hackathon.objects.exclude(hackathon_id=hackathon_id).order_by('-start_date')[:5]
                
            except UserProfile.DoesNotExist:
                print(f"⚠️ User profile not found for user_id: {request.user.id}")
                hackathons = Hackathon.objects.exclude(hackathon_id=hackathon_id).order_by('-start_date')[:5]
            except Exception as e:
                print(f"❌ Error in skill matching: {e}")
                hackathons = Hackathon.objects.exclude(hackathon_id=hackathon_id).order_by('-start_date')[:5]
        else:
            # Anonymous user - show recent hackathons
            hackathons = Hackathon.objects.exclude(hackathon_id=hackathon_id).order_by('-start_date')[:5]
        
        return render(request, 'CareerCompassapp/hackathon.html', {
            'selected_hackathon': selected_hackathon,
            'hackathons': hackathons
        })
    
    else:
        # Main hackathon list page with skill-based recommendations
        if request.user.is_authenticated:
            try:
                # Get user profile
                user_profile = UserProfile.objects.get(user_id=request.user.id)
                
                # Extract and clean user skills
                user_skills = []
                if user_profile.skills:
                    user_skills = [skill.strip().lower() for skill in user_profile.skills.split(',') if skill.strip()]
                
                # Extract and clean user interests
                user_interests = []
                if user_profile.user_interest:
                    user_interests = [interest.strip().lower() for interest in user_profile.user_interest.split(',') if interest.strip()]
                
                # Combine skills and interests
                user_keywords = set(user_skills + user_interests)
                
                print(f"🔍 User Keywords: {user_keywords}")  # Debug
                
                if user_keywords:
                    # Get all hackathons
                    all_hackathons = Hackathon.objects.all()
                    
                    recommended_hackathons = []
                    for hackathon in all_hackathons:
                        if hackathon.required_skills:
                            hackathon_skills = [skill.strip().lower() for skill in hackathon.required_skills.split(',') if skill.strip()]
                            
                            print(f"🎯 Hackathon '{hackathon.name}' skills: {hackathon_skills}")  # Debug
                            
                            # Find matching skills
                            matching_items = user_keywords & set(hackathon_skills)
                            
                            if matching_items:
                                hackathon.match_count = len(matching_items)
                                hackathon.matching_skills_list = list(matching_items)
                                recommended_hackathons.append(hackathon)
                                print(f"✅ Match found! Skills: {matching_items}")  # Debug
                    
                    # Sort by match count (descending) then by start_date and limit to 5
                    if recommended_hackathons:
                        recommended_hackathons.sort(key=lambda x: (x.match_count, x.start_date), reverse=True)
                        hackathons = recommended_hackathons[:5]  # Limit to 5
                        print(f"📊 Total recommended hackathons: {len(hackathons)}")  # Debug
                    else:
                        # No skill matches, show recent hackathons (limit 5)
                        print("⚠️ No skill matches found, showing recent hackathons")  # Debug
                        hackathons = Hackathon.objects.all().order_by('-start_date')[:5]
                else:
                    # User has no skills/interests set (limit 5)
                    print("⚠️ User has no skills/interests set")  # Debug
                    hackathons = Hackathon.objects.all().order_by('-start_date')[:5]
                
            except UserProfile.DoesNotExist:
                print(f"⚠️ User profile not found for user_id: {request.user.id}")
                hackathons = Hackathon.objects.all().order_by('-start_date')[:5]
            except Exception as e:
                print(f"❌ Error in skill matching: {e}")
                import traceback
                traceback.print_exc()
                hackathons = Hackathon.objects.all().order_by('-start_date')[:5]
        else:
            # Anonymous user - show recent hackathons (limit 5)
            hackathons = Hackathon.objects.all().order_by('-start_date')[:5]
        
        return render(request, 'CareerCompassapp/hackathon.html', {
            'hackathons': hackathons
        })
        
# Enrollment view

def enroll_hackathon(request, hackathon_id):
    # Get hackathon directly from hackathons table
    try:
        table_name = Hackathon._meta.db_table  # ✅ Safely get actual table name
        with connection.cursor() as cursor:
            query = f"SELECT * FROM {table_name} WHERE hackathon_id = %s"
            cursor.execute(query, [hackathon_id])
            row = cursor.fetchone()
        
            if not row:
                messages.error(request, 'Hackathon not found!')
                return redirect('hackathon_detail', hackathon_id=hackathon_id)
            
            hackathon_data = {
                'hackathon_id': row[0],
                'name': row[1],
                'start_date': row[2],
                'end_date': row[3],
                'details': row[4]
            }
    except Exception as e:
        messages.error(request, f'Error fetching hackathon: {e}')
        return redirect('hackathon_detail', hackathon_id=hackathon_id)

    if request.method == 'POST':
        participation_type = request.POST.get('participation_type')
        
        try:
            if participation_type == 'solo':
                solo_name = request.POST.get('solo_name', '').strip()
                solo_skills = request.POST.get('solo_skills', '').strip()
                
                # Validation
                if not solo_name or not solo_skills:
                    messages.error(request, 'Please fill all required fields!')
                    return render(request, 'CareerCompassapp/enrollment_form.html', {
                        'hackathon': hackathon_data
                    })

                # Check if name already exists for this hackathon
                existing = HackathonEnrollment.objects.filter(
                    hackathon_id=hackathon_id,
                    participant_name=solo_name,
                    participation_type='solo'
                ).first()
                
                if existing:
                    messages.error(request, f'Name "{solo_name}" is already registered for this hackathon!')
                    return render(request, 'CareerCompassapp/enrollment_form.html', {
                        'hackathon': hackathon_data
                    })

                # Create solo enrollment - USE hackathon_id
                hackathon_obj = Hackathon.objects.get(hackathon_id=hackathon_id)
                enrollment = HackathonEnrollment.objects.create(
                  hackathon=hackathon_obj,
                  participant_name=solo_name,
                  skills=solo_skills,
                  participation_type='solo',
                  team_name=''
                )


                messages.success(request, f'Successfully enrolled as solo participant! Your ID: {enrollment.enrollment_id}')
                return redirect('hackathon_detail', hackathon_id=hackathon_id)
                
            elif participation_type == 'team':
                team_name = request.POST.get('team_name', '').strip()
                team_leader = request.POST.get('team_leader_name', '').strip()
                team_skills = request.POST.get('team_skills', '').strip()
                member_names = request.POST.getlist('member_names[]')
                member_skills = request.POST.getlist('member_skills[]')
                
                # Validation
                if not team_name or not team_leader or not team_skills:
                    messages.error(request, 'Please fill all required team fields!')
                    return render(request, 'CareerCompassapp/enrollment_form.html', {
                        'hackathon': hackathon_data
                    })
                
                # Check if team name already exists for this hackathon
                existing = HackathonEnrollment.objects.filter(
                    hackathon_id=hackathon_id,
                    team_name=team_name,
                    participation_type='team'
                ).first()
                
                if existing:
                    messages.error(request, f'Team name "{team_name}" is already registered for this hackathon!')
                    return render(request, 'CareerCompassapp/enrollment_form.html', {
                        'hackathon': hackathon_data
                    })
                
                # Create team enrollment - USE hackathon_id
                hackathon_obj = Hackathon.objects.get(pk=hackathon_id)

                enrollment = HackathonEnrollment.objects.create(
                  hackathon=hackathon_obj,
                  participation_type='team',
                  participant_name=member_names,
                  team_name=team_name,
                  skills=team_skills
)

                
                # Save team members
                for name, skills in zip(member_names, member_skills):
                    if name and name.strip():
                        TeamMember.objects.create(
                            enrollment_id=enrollment.enrollment_id,
                            member_name=name.strip(),
                            member_skills=skills.strip() if skills else ''
                        )
                
                messages.success(request, f'Successfully enrolled as team! Your Team ID: {enrollment.enrollment_id}')
                return redirect('hackathon_detail', hackathon_id=hackathon_id)
            
        except IntegrityError as e:
            print(f"IntegrityError: {e}")
            print(traceback.format_exc())
            messages.error(request, f'Database error: {e}')
            return render(request, 'CareerCompassapp/enrollment_form.html', {
                'hackathon': hackathon_data
            })
        except Exception as e:
            print(f"General Error: {e}")
            print(traceback.format_exc())
            messages.error(request, f'An error occurred: {str(e)}')
            return render(request, 'CareerCompassapp/enrollment_form.html', {
                'hackathon': hackathon_data
            })
    
    print("Hackathon ID received:", hackathon_id)
    return render(request, 'CareerCompassapp/enrollment_form.html', {
        'hackathon': hackathon_data
    })

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

@login_required
def hackathon_register(request):
    if request.method == 'POST':
        registration_type = request.POST.get('registration_type')
        
        if registration_type == 'solo':
            # Solo registration
            name = request.POST.get('name')
            email = request.POST.get('email')
            skills = request.POST.get('skills')
            
            # Database mein save karo
            # Solo registration logic
            
        elif registration_type == 'team':
            # Team registration
            team_name = request.POST.get('team_name')
            team_leader_name = request.POST.get('team_leader_name')
            team_email = request.POST.get('team_email')
            team_skills = request.POST.get('team_skills')
            
            # Team members (optional)
            member_names = request.POST.getlist('member_names[]')
            member_skills = request.POST.getlist('member_skills[]')
            
            # Database mein save karo
            # Team ID auto-generate hogi database mein
            
        messages.success(request, 'Registration successful!')
        return redirect('dashboard')
    
    return render(request, 'hackathon_register.html')

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import (
    UserSelectedRoadmap,
    UserRoadmapProgress,
    Roadmap,
    HackathonEnrollment
)

@login_required
def dashboard_data(request):
    """API endpoint for dashboard - matches /api/dashboard/ URL"""
    user = request.user

    try:
        # Get user profile
        profile = UserProfile.objects.filter(user=user).first()
        
        # -------------------------------
        # 1. HACKATHONS (User Enrollments)
        # -------------------------------
        # Find enrollments where user is participant (solo) or in team
        enrolled_hackathons = HackathonEnrollment.objects.filter(
            models.Q(participant_name__icontains=user.username) |
            models.Q(team_name__icontains=user.username)
        ).select_related('hackathon')

        hackathon_list = []
        for enrollment in enrolled_hackathons:
            hack = enrollment.hackathon
            hackathon_list.append({
                "id": hack.hackathon_id,
                "name": hack.name,
                "team_name": enrollment.team_name if enrollment.team_name else "Solo",
                "start_date": str(hack.start_date),
                "end_date": str(hack.end_date),
                "participation_type": enrollment.participation_type,
            })

        # -------------------------------
        # 2. INTERNSHIPS (Real Applications)
        # -------------------------------
        applications = InternshipApplication.objects.filter(
            user=user
        ).select_related('internship').order_by('-applied_on')

        internships_list = []
        for app in applications:
            internships_list.append({
                "title": app.internship.title,
                "company": app.internship.company.name if app.internship.company else "Company",  # Or fetch company name if you have Companies model
                "status": app.status,
                "applied_on": str(app.applied_on.date()),
                "location": app.internship.location,
                "deadline": str(app.internship.deadline),
            })

        # -------------------------------
        # 3. ROADMAPS (User Selected)
        # -------------------------------
        selected_roadmaps = UserSelectedRoadmap.objects.filter(
            user=user
        ).select_related('roadmap')

        roadmap_list = []
        for selection in selected_roadmaps:
            roadmap = selection.roadmap
            total_steps = roadmap.steps.count()

            completed_steps = UserRoadmapProgress.objects.filter(
                user=user,
                roadmap=roadmap,
                is_completed=True
            ).count()

            progress = int((completed_steps / total_steps) * 100) if total_steps > 0 else 0

            roadmap_list.append({
                "title": roadmap.title,
                "description": roadmap.description or "",
                "completed_steps": completed_steps,
                "total_steps": total_steps,
                "progress_percentage": progress,
            })

        # -------------------------------
        # FINAL RESPONSE
        # -------------------------------
        return JsonResponse({
            "profile": {
                "name": profile.username if profile else user.username,
                "education": profile.education if profile else "",
                "skills": profile.skills if profile else "",
            },
            "internships": internships_list,
            "hackathons": hackathon_list,
            "roadmaps": roadmap_list,
        })
        
    except Exception as e:
        import traceback
        print(f"❌ Dashboard API Error: {e}")
        traceback.print_exc()
        return JsonResponse({
            "error": str(e),
            "profile": {"name": user.username},
            "internships": [],
            "hackathons": [],
            "roadmaps": []
        }, status=500)
    
@login_required
def get_applied_internships(request):
    """Fetch internships the logged-in user has applied to"""
    user_id = request.user.id

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT i.internship_id, i.title, c.name AS company, i.location, i.deadline, a.status, a.applied_on
            FROM applications a
            JOIN internships i ON a.internship_id = i.internship_id
            LEFT JOIN companies c ON i.company_id = c.company_id
            WHERE a.user_id = %s
            ORDER BY a.applied_on DESC
        """, [user_id])
        rows = cursor.fetchall()

    applied_internships = [
        {
            'id': row[0],
            'title': row[1],
            'company': row[2] or 'Company',
            'location': row[3],
            'deadline': str(row[4]),
            'status': row[5],
            'applied_on': str(row[6])
        } for row in rows
    ]

    return JsonResponse({'internships': applied_internships})