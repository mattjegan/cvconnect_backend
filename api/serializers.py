from django.utils.timesince import timesince
from django.contrib.auth.models import User
from rest_framework import serializers

from drf_extra_fields.fields import Base64ImageField

from api.models import Profile, JobPosting, JobApplication, EducationDescription, EmploymentDescription, Skill, \
    Company, SocialLink, CompanyManager, ProfileImage, FeedPost


class UserSerializer(serializers.ModelSerializer):

    password = serializers.CharField(max_length=100, write_only=True)

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email']
        )

        # This is needed so that the password gets hashed, not just stored
        # as plain text
        user.set_password(validated_data['password'])

        user.save()

        return user

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'password',
            'email',
        ]
        write_only_fields = ['password',]
        read_only_fields = ['id',]

    def is_valid(self, raise_exception=False):
        valid = super(UserSerializer, self).is_valid()
        if not valid:
            return valid

        users = User.objects.filter(email=self.initial_data['email'])
        if users.exists():
            self._errors['email'] = ['Email already in use. Please use another email address']
            # raise ValidationError('Email already in use. Please use another email address')
            return False

        return True


class ProfileSerializer(serializers.ModelSerializer, ):

    def to_representation(self, instance):
        ret = super(ProfileSerializer, self).to_representation(instance)
        ret['username'] = instance.user.username
        ret['email'] = instance.user.email

        ret['connections'] = instance.connections.all().values_list('user__username', flat=True)

        position = EmploymentDescription.objects.filter(profile=instance).order_by('start_date')
        current_position = None
        current_company = None
        for p in position:
            if not p.end_date:
                current_position = p.role
                current_company = p.employer

        if current_company is None and current_position is None:
            current_position = "Not Employed"
            current_company = "Not Employed"

        ret['current_company'] = current_company
        ret['current_position'] = current_position

        edu = EducationDescription.objects.filter(profile=instance).order_by('date_attained')
        if edu.exists():
            ret['current_edu'] = edu.first().institution
        else:
            ret['current_edu'] = "no institution"


        return ret

    class Meta:
        model = Profile


class ProfileImageSerializer(serializers.ModelSerializer, ):

    image = Base64ImageField(required=False)

    class Meta:
        model = ProfileImage


class JobPostingSerializer(serializers.ModelSerializer, ):

    recruiter = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field='username')

    def to_representation(self, instance):
        ret = super(JobPostingSerializer, self).to_representation(instance)
        ret['created'] = timesince(instance.created)
        return ret

    class Meta:
        model = JobPosting


class JobApplicationSerializer(serializers.ModelSerializer, ):

    def is_valid(self, raise_exception=False):

        username = self.initial_data.get('profile', None)
        profile = Profile.objects.filter(user__username=username)
        if profile.exists():
            self.initial_data['profile'] = profile.first().pk

        valid = super(JobApplicationSerializer, self).is_valid(raise_exception=raise_exception)
        return valid

    def to_representation(self, instance):

        position = EmploymentDescription.objects.filter(profile=instance.profile).order_by('start_date')
        current_position = None
        current_company = None
        for p in position:
            if not p.end_date:
                current_position = p.role
                current_company = p.employer

        if current_company is None and current_position is None:
            current_position = "Not Employed"
            current_company = "Not Employed"


        ret = {
            'app_id': instance.id,
            'username': instance.profile.user.username,
            'full_name': instance.profile.full_name,
            'current_company': current_company,
            'current_position': current_position,
            'skills': ', '.join(Skill.objects.filter(profile=instance.profile).values_list('name', flat=True)),
            'status': instance.status,
            'job_posting': instance.job_posting.id,
            'profile': instance.profile.id,
            'job_posting_company': instance.job_posting.company,
            'job_posting_position': instance.job_posting.position
        }
        return ret

    class Meta:
        model = JobApplication


class EducationDescriptionSerializer(serializers.ModelSerializer, ):

    class Meta:
        model = EducationDescription


class EmploymentDescriptionSerializer(serializers.ModelSerializer, ):

    class Meta:
        model = EmploymentDescription


class SkillSerializer(serializers.ModelSerializer, ):

    class Meta:
        model = Skill


class CompanySerializer(serializers.ModelSerializer, ):

    class Meta:
        model = Company


class SocialLinkSerializer(serializers.ModelSerializer, ):

    class Meta:
        model = SocialLink


class CompanyManagerSerializer(serializers.ModelSerializer, ):

    class Meta:
        model = CompanyManager


class FeedPostSerializer(serializers.ModelSerializer, ):

    user = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field='username')

    def to_representation(self, instance):
        ret = super(FeedPostSerializer, self).to_representation(instance)
        ret['full_name'] = Profile.objects.get(user__username=ret['user']).full_name
        ret['created'] = timesince(instance.created)
        return ret

    class Meta:
        model = FeedPost