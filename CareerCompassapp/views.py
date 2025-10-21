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


def home(request):
    """Home page - landing page"""
    return render(request, 'CareerCompassapp/home.html')

@ensure_csrf_cookie

def roadmaps_form(request):
    """Step 1: Show career credentials form"""
    return render(request, 'CareerCompassapp/RoadmapsForm.html')

def option_roadmaps(request):
    """Step 2: Process form data and show roadmap options"""
    if request.method == 'POST':
        # Check if this is roadmap selection (from options page)
        if 'selected_roadmap' in request.POST and 'current_role' not in request.POST:
            # This is coming from the options page - user selected a roadmap
            selected_roadmap = request.POST.get('selected_roadmap')
            request.session['selected_roadmap'] = selected_roadmap
            # Don't redirect here, let the form handle it
            return JsonResponse({'status': 'success'})
        
        # This is initial form submission from RoadmapsForm.html
        user_data = {
            'current_role': request.POST.get('current_role', ''),
            'experience': request.POST.get('experience', ''),
            'education_level': request.POST.get('education_level', ''),
            'preferred_industry': request.POST.get('preferred_industry', ''),
            'current_skills': request.POST.get('current_skills', ''),
            'target_skills': request.POST.get('target_skills', ''),
            'career_goals': request.POST.get('career_goals', ''),
            'timeframe': request.POST.get('timeframe', '')
        }
        
        # Store user data in session
        request.session['user_data'] = user_data
        
        # Generate custom roadmap options based on user data
        roadmap_options = generate_roadmap_options(user_data)
        request.session['roadmap_options'] = roadmap_options
        
        context = {
            'page_title': 'Choose A Roadmap',
            'roadmap_options': roadmap_options
        }
        return render(request, 'CareerCompassapp/optionroadmaps.html', context)
    
    # If GET request, check if we have user data in session
    user_data = request.session.get('user_data')
    if user_data:
        # Show options again
        roadmap_options = request.session.get('roadmap_options', generate_roadmap_options(user_data))
        context = {
            'page_title': 'Choose A Roadmap',
            'roadmap_options': roadmap_options
        }
        return render(request, 'CareerCompassapp/optionroadmaps.html', context)
    
    # No user data, redirect to form
    return redirect('roadmaps_form')

def roadmap(request):
    """Step 3: Show selected roadmap with detailed steps"""
    # Handle POST from option selection
    if request.method == 'POST':
        selected_roadmap = request.POST.get('selected_roadmap')
        if selected_roadmap:
            request.session['selected_roadmap'] = selected_roadmap
    
    # Get user data and selected roadmap from session
    user_data = request.session.get('user_data', {})
    selected_roadmap_id = request.session.get('selected_roadmap', None)
    
    if not user_data:
        return redirect('roadmaps_form')
    
    if not selected_roadmap_id:
        return redirect('option_roadmaps')
    
    # Generate detailed roadmap steps
    roadmap_steps = generate_detailed_roadmap(user_data, selected_roadmap_id)
    
    context = {
        'page_title': get_roadmap_title(selected_roadmap_id, user_data),
        'roadmap_steps': roadmap_steps,
        'user_profile': user_data
    }
    return render(request, 'CareerCompassapp/roadmaps_generated.html', context)

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

# Optional additional views
def about(request):
    """About page"""
    return render(request, 'CareerCompassapp/about.html')

def contact(request):
    """Contact page"""
    return render(request, 'CareerCompassapp/contact.html')

def credentials(request):
    """Credentials page"""
    return render(request, 'CareerCompassapp/Dashboard.html')


def hackathon(request, page='home'):
    return render(request, 'CareerCompassapp/Hackathon.html')

def dashboard(request):
    return render(request, 'CareerCompassapp/Dashboard.html')

def internships(request):
    return render(request, 'CareerCompassapp/internships.html')

def frontend_intern(request):
    return render(request, 'CareerCompassapp/microsoft.html')

def data_science_intern(request):
    return render(request, 'CareerCompassapp/google.html')

def amazon_intern(request):
    return render(request, 'CareerCompassapp/amazon.html')

def figma_intern(request):
    return render(request, 'CareerCompassapp/figma.html')

def cisco_intern(request):
    return render(request, 'CareerCompassapp/cisco.html')

def ibm_intern(request):
    return render(request, 'CareerCompassapp/ibm.html')

def contactus(request):
    return render(request, 'CareerCompassapp/contact.html')




def signin(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Get user by email
        try:
            user = User.objects.get(email=email)
            user = authenticate(request, username=user.username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Successfully signed in!')
                return redirect('CareerCompassapp/home')
            else:
                messages.error(request, 'Invalid email or password')
        except User.DoesNotExist:
            messages.error(request, 'Invalid email or password')
    
    return render(request, 'CareerCompassapp/Signin.html')

def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        terms = request.POST.get('terms')
        
        # Validation
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
        
        messages.success(request, 'Account created successfully! Please sign in.')
        return redirect('Signin')
    
    return render(request, 'CareerCompassapp/Signup.html')


def social_auth(request, provider):
    messages.info(request, f'Social auth with {provider} coming soon!')
    return redirect('Signin')

def logout_view(request):
    logout(request)
    messages.success(request, 'Successfully logged out!')
    return redirect('home')