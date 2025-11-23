from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

# SUMBAL OLD CODE BELOW FOR REFERENCE
# class UserProfile(models.Model):
#     profile_id = models.AutoField(primary_key=True)
#     user = models.OneToOneField(User, on_delete=models.CASCADE, db_column='user_id')
#     username = models.CharField(max_length=255, blank=True)
#     education = models.CharField(max_length=255, blank=True)
#     degree = models.CharField(max_length=255, blank=True)
#     skills = models.TextField(blank=True)
#     country = models.CharField(max_length=100, blank=True)
#     work_experience = models.TextField(blank=True)
#     user_interest = models.TextField(blank=True)
#     industry = models.CharField(max_length=255, blank=True, null=True)
#     career_goals = models.TextField(blank=True, null=True)
#     time_frame = models.IntegerField(default=0)

#     class Meta:
#         db_table = 'user_profile'
#         managed = False

#     def __str__(self):
#         return self.username or self.user.username

from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    profile_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, db_column='user_id')

    # Fields merged from both models
    username = models.CharField(max_length=255, blank=True)
    # name = models.CharField(max_length=255, blank=True, null=True)

    education = models.CharField(max_length=255, blank=True, null=True)
    degree = models.CharField(max_length=255, blank=True, null=True)
    skills = models.TextField(blank=True, null=True)  # Comma-separated list
    country = models.CharField(max_length=100, blank=True, null=True)
    work_experience = models.TextField(blank=True, null=True)
    user_interest = models.TextField(blank=True, null=True)  # Comma-separated

    # Extra attributes from the second version
    industry = models.CharField(max_length=255, blank=True, null=True)
    career_goals = models.TextField(blank=True, null=True)
    time_frame = models.IntegerField(default=0)

    class Meta:
        db_table = 'user_profile'
        app_label = "CareerCompassapp"
        managed = False

    def __str__(self):
        # Prefer to display something meaningful
        return self.username or self.name or self.user.username


class UserSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    login_time = models.DateTimeField(null=True, blank=True)
    logout_time = models.DateTimeField(null=True, blank=True)
    ip_address = models.CharField(max_length=100, blank=True)
    device_info = models.TextField(blank=True)


from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
class Internships(models.Model):
    internship_id = models.AutoField(primary_key=True)
    company_id = models.IntegerField()
    title = models.CharField(max_length=255)
    duration = models.CharField(max_length=100)

    # Allowed location choices (keeps UI/forms consistent)
    LOCATION_USA = 'USA'
    LOCATION_GERMANY = 'Germany'
    LOCATION_PAKISTAN = 'Pakistan'
    LOCATION_REMOTE = 'Remote'
    LOCATION_UK = 'UK'
    LOCATION_CANADA = 'Canada'

    LOCATION_CHOICES = [
        (LOCATION_USA, 'USA'),
        (LOCATION_GERMANY, 'Germany'),
        (LOCATION_PAKISTAN, 'Pakistan'),
        (LOCATION_REMOTE, 'Remote'),
        (LOCATION_UK, 'UK'),
        (LOCATION_CANADA, 'Canada'),
    ]

    location = models.CharField(max_length=20, choices=LOCATION_CHOICES, default=LOCATION_REMOTE)
    skills_required = models.CharField(max_length=255)
    deadline = models.DateField()
    description = models.TextField()
    stipend = models.IntegerField(
        validators=[MinValueValidator(500), MaxValueValidator(1500)],
        null=True,
        blank=True,
        help_text='Stipend in local currency (500-1500)'
    )

    def __str__(self):
        return self.title


class Users(models.Model):
    user_id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)

    def __str__(self):
        return self.email


class Roadmap(models.Model):
    roadmap_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    created_by = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = 'roadmaps'
        managed = False
        ordering = ['roadmap_id']

    def __str__(self):
        return self.title


class RoadmapStep(models.Model):
    step_id = models.AutoField(primary_key=True)
    roadmap = models.ForeignKey(
        Roadmap,
        on_delete=models.CASCADE,
        db_column='roadmap_id',
        related_name='steps'
    )
    step_number = models.PositiveIntegerField()
    step_content = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'roadmap_steps'
        managed = False
        ordering = ['step_number']

    def __str__(self):
        return f"{self.roadmap.title} - Step {self.step_number}"


class UserRoadmapProgress(models.Model):
    progress_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')
    roadmap = models.ForeignKey(Roadmap, on_delete=models.CASCADE, db_column='roadmap_id')
    step = models.ForeignKey(RoadmapStep, on_delete=models.CASCADE, db_column='step_id')
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'user_step_progress'
        unique_together = ('user', 'roadmap', 'step')
        managed = False

    def __str__(self):
        return f"{self.user.username} - {self.roadmap.title} - Step {self.step.step_number}"

    def save(self, *args, **kwargs):
        if self.is_completed and not self.completed_at:
            self.completed_at = timezone.now()
        elif not self.is_completed:
            self.completed_at = None
        super().save(*args, **kwargs)


class UserSelectedRoadmap(models.Model):
    user_roadmap_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column='user_id',
        related_name='selected_roadmaps'
    )
    roadmap = models.ForeignKey(
        Roadmap,
        on_delete=models.CASCADE,
        db_column='roadmap_id'
    )
    selected_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_selected_roadmaps'
        managed = False
        unique_together = ('user', 'roadmap')

    def __str__(self):
        return f"{self.user.username} → {self.roadmap.title}"

    @property
    def progress_percentage(self):
        total_steps = self.roadmap.steps.count()
        completed_steps = UserRoadmapProgress.objects.filter(
            user=self.user, roadmap=self.roadmap, is_completed=True
        ).count()
        return (completed_steps / total_steps * 100) if total_steps > 0 else 0
    
class Hackathon(models.Model):
    hackathon_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    details = models.TextField()
    registration_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    required_skills = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'hackathons'  # ← YE CHANGE KARO!
        app_label = 'CareerCompassapp'
        managed = False
        
    def __str__(self):
        return self.name


class HackathonTeam(models.Model):
    team_id = models.AutoField(primary_key=True)
    hackathon = models.ForeignKey(Hackathon, on_delete=models.CASCADE, related_name='teams')
    team_name = models.CharField(max_length=255)
    team_members = models.TextField(default='', help_text="Comma-separated member names")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        db_table = "hackathon_teams"
        managed=False

    def __str__(self):
        return f"{self.team_name} ({self.hackathon.name})"

class HackathonEnrollment(models.Model):
    enrollment_id = models.AutoField(primary_key=True)
    hackathon = models.ForeignKey(
        'CareerCompassapp.Hackathon',
        on_delete=models.CASCADE,
        db_column='hackathon_id'
    )
    user = models.ForeignKey(  # ✅ ADD THIS FIELD
        User, 
        on_delete=models.CASCADE, 
        db_column='user_id',
        null=True,  # Temporarily allow null for existing records
        blank=True
    )
    participation_type = models.CharField(max_length=10, choices=[('solo', 'Solo'), ('team', 'Team')])
    participant_name = models.CharField(max_length=200)
    team_name = models.CharField(max_length=200, blank=True, default='')
    skills = models.TextField()
    enrollment_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'hackathon_enrollment'
        app_label = 'CareerCompassapp'
        managed = True  # ✅ Change to True so Django can create/modify table

    def __str__(self):
        return f"{self.participant_name} - {self.hackathon.name} ({self.participation_type})"

class TeamMember(models.Model):
    member_id = models.AutoField(primary_key=True)
    enrollment = models.ForeignKey(
        HackathonEnrollment, 
        on_delete=models.CASCADE, 
        related_name='members',
    )
    member_name = models.CharField(max_length=200)
    member_skills = models.TextField(blank=True, default='')
    
    class Meta:
        db_table = 'team_members'
        app_label = 'CareerCompassapp'
        

#LAIBA OLD CODE BELOW FOR REFERENCE
# class UserProfile(models.Model):
#     profile_id = models.AutoField(primary_key=True)
#     user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')
#     name = models.CharField(max_length=200)
#     education = models.CharField(max_length=200, blank=True, null=True)
#     degree = models.CharField(max_length=200, blank=True, null=True)
#     skills = models.TextField(blank=True, null=True)  # Comma-separated
#     country = models.CharField(max_length=100, blank=True, null=True)
#     work_experience = models.TextField(blank=True, null=True)
#     user_interest = models.TextField(blank=True, null=True)  # Comma-separated
    
#     class Meta:
#         db_table = 'user_profile' 
#         app_label = "CareerCompassapp"
#         managed=False
       
    
#     def __str__(self):

#         return f"{self.name} - {self.user.username}"

# Add this model to your models.py file

class InternshipApplication(models.Model):
    application_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')
    internship = models.ForeignKey(Internships, on_delete=models.CASCADE, db_column='internship_id')
    
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    applied_on = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'internship_applications'
        app_label = 'CareerCompassapp'
        # Set managed=True if you want Django to create this table
        # Set managed=False if the table already exists
        managed = True
    
    def __str__(self):
        return f"{self.user.username} - {self.internship.title}"