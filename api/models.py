from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator

class ProfileImage(models.Model, ):
    image = models.ImageField(upload_to='profile-images')


class Profile(models.Model, ):
    """
    A profile has a one to one relationship with a User and may contain
    extra information about a User. The User model is only used as a reference
    for authentication.
    """

    user = models.ForeignKey(User)
    full_name = models.CharField(max_length=100, blank=False, null=False)
    preferred_name = models.CharField(max_length=100, blank=False, null=False)
    country = models.CharField(max_length=100, blank=False, null=False)
    connections = models.ManyToManyField('self', blank=True)
    image = models.ForeignKey(ProfileImage, blank=True, null=True)

    def skills(self):
        return Skill.objects.filter(profile=self)

    def education_descriptions(self):
        return EducationDescription.objects.filter(profile=self)


class JobPosting(models.Model, ):
    """
    A JobPosting represents the advertisement of a job by some recruiter.
    There will be many-to-many relationships between Profiles and JobPostings
    through JobApplication.
    """

    recruiter = models.ForeignKey(User)
    company = models.CharField(max_length=50, blank=True, null=False, default='')
    description = models.TextField(blank=True, null=False, default='')
    compensation = models.TextField(blank=True, null=False, default='')
    position = models.TextField(blank=True, null=False, default='')
    created = models.DateTimeField(blank=False, null=False, auto_now=True)


class JobApplication(models.Model, ):
    """
    This model represents an application to a JobPosting from a Profile
    """

    STATUS_CHOICES = [('Pending', 'Pending'),
                      ('Accepted', 'Accepted'),
                      ('Rejected', 'Rejected')]

    job_posting = models.ForeignKey(JobPosting)
    profile = models.ForeignKey(Profile)
    status = models.CharField(choices=STATUS_CHOICES, max_length=10,
                              blank=False, null=False, default='Pending')


class EducationDescription(models.Model, ):
    """
    A representation of a single instance of education for a profile
    """

    profile = models.ForeignKey(Profile)
    institution = models.CharField(max_length=100, blank=False, null=False)
    degree = models.CharField(max_length=100, blank=False, null=False)
    date_started = models.DateField(blank=False, null=False)
    date_attained = models.DateField(blank=True, null=True)
    achievements = models.TextField(default='', blank=True, null=False)
    field_of_study = models.TextField(default='', blank=True, null=True)
    extra_activities = models.TextField(default='', blank=True, null=True)
    description = models.TextField(default='', blank=True, null=True)


class EmploymentDescription(models.Model, ):
    """
    A representation of a single instance of employment for a profile
    """

    profile = models.ForeignKey('api.Profile')
    location = models.CharField(max_length=100, blank=False, null=False)
    employer = models.CharField(max_length=100, blank=False, null=False)
    role = models.CharField(max_length=100, blank=False, null=False)
    start_date = models.DateField(blank=False, null=False)
    end_date = models.DateField(blank=True, null=True)
    achievements = models.TextField(default='', blank=True, null=False)


class Skill(models.Model, ):
    """
    A representation of a skill on a profile
    """

    profile = models.ForeignKey(Profile)
    name = models.CharField(max_length=100, blank=False, null=False)
    proficiency = models.PositiveIntegerField(validators=[MaxValueValidator(5),])


class Company(models.Model, ):
    """
    A representation of a Company, for use in employment descriptions
    """

    name = models.CharField(max_length=100, blank=False, null=False)
    # TODO: Add image field, this will require us to store the image (Needs Discussion)
    description = models.TextField(blank=False, null=False)
    industry = models.CharField(max_length=100, blank=False, null=False)
    home_page = models.URLField(blank=True, null=True)

    def social_links(self):
        return SocialLink.objects.filter(company=self)

    def managers(self):
        return CompanyManager.objects.filter(company=self)

    def employees(self):
        return EmploymentDescription.objects.filter(employer=self)


class SocialLink(models.Model, ):
    """
    A Companies social url
    """

    company = models.ForeignKey(Company)
    service = models.CharField(max_length=100, blank=False, null=False)
    link = models.URLField(blank=False, null=False)


class CompanyManager(models.Model, ):
    """
    A representation of someone who can update a company
    """

    profile = models.ForeignKey(Profile)
    company = models.ForeignKey(Company)


class ForgottenPasswordToken(models.Model, ):
    """
    A token for a forgotten password
    """
    user = models.ForeignKey(User)
    token = models.UUIDField(blank=False, null=False)


class FeedPost(models.Model, ):
    """
    A feed post
    """
    user = models.ForeignKey(User)
    text = models.TextField(blank=False, null=False)
    created = models.DateTimeField(blank=False, null=False, auto_now=True)