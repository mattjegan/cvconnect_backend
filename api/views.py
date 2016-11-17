from django.db.models import Q
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.http import Http404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from uuid import uuid4

from api.models import Profile, JobPosting, JobApplication, EducationDescription, EmploymentDescription, Skill, \
    Company, SocialLink, CompanyManager, ForgottenPasswordToken, FeedPost
from api.serializers import UserSerializer, ProfileSerializer, JobPostingSerializer, JobApplicationSerializer, \
    EducationDescriptionSerializer, EmploymentDescriptionSerializer, SkillSerializer, CompanySerializer, \
    SocialLinkSerializer, CompanyManagerSerializer, ProfileImageSerializer, FeedPostSerializer


class UserList(generics.ListCreateAPIView, ):
    serializer_class = UserSerializer
    model = User

    def get_queryset(self):
        return User.objects.all()
    
    def post(self, request, *args, **kwargs):
        """
        Create a new user and a basic profile for the user.
        Return the user profile id and user data.

        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        user_serializer = UserSerializer(data=request.data)

        # If the data isn't valid we return the error messages
        if not user_serializer.is_valid():
            return Response(user_serializer.errors, status=400)

        # Otherwise we save the user and create a profile for the user
        user_serializer.save()
        user_profile = Profile(
            user=user_serializer.instance
        )
        user_profile.save()

        ret = user_serializer.to_representation(user_serializer.instance)
        ret['profile_id'] = user_profile.id
        return Response(ret, status=201)


class UserDetail(generics.RetrieveUpdateDestroyAPIView, ):
    serializer_class = UserSerializer
    model = User
    lookup_field = 'username'

    def get_queryset(self):
        username = self.kwargs.get('username', None)
        return User.objects.filter(username=username)
    
    def patch(self, request, *args, **kwargs):
        user = self.get_queryset()
        if user.exists():
            user = user.first()
            if request.user != user:
                raise Http404

        return super(UserDetail, self).patch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        user = self.get_queryset()
        if user.exists():
            user = user.first()
            if request.user != user:
                raise Http404

        return super(UserDetail, self).delete(request, *args, **kwargs)


class ProfileList(generics.ListCreateAPIView, ):
    serializer_class = ProfileSerializer
    model = Profile

    def get_queryset(self):
        return Profile.objects.all()


class ProfileDetail(generics.RetrieveUpdateDestroyAPIView, ):
    serializer_class = ProfileSerializer
    model = Profile
    lookup_url_kwarg = 'username'
    lookup_field = 'user__username'

    def get_queryset(self):
        username = self.kwargs.get('username', None)
        return Profile.objects.filter(user__username=username)

    def patch(self, request, *args, **kwargs):
        profile = self.get_queryset()
        if profile.exists():
            profile = profile.first()
            if request.user != profile.user:
                raise Http404

        return super(ProfileDetail, self).patch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        profile = self.get_queryset()
        if profile.exists():
            profile = profile.first()
            if request.user != profile.user:
                raise Http404

        return super(ProfileDetail, self).delete(request, *args, **kwargs)


class ProfileRecommendations(generics.ListAPIView, ):
    serializer_class = ProfileSerializer
    model = Profile

    def get_queryset(self):
        # Just return 3 random profiles for the moment that aren't the user from the url
        username = self.kwargs.get('username', None)
        connection_pks = list(Profile.objects.get(user__username=username).connections.all().values_list('pk', flat=True))
        connection_pks.append(Profile.objects.get(user__username=username).pk)
        return Profile.objects.all().exclude(pk__in=connection_pks).order_by('?')[:3]

    def get(self, request, *args, **kwargs):

        queryset = self.get_queryset()
        ret_data = []

        for profile in queryset:
            profile_serializer = ProfileSerializer(instance=profile)
            profile_data = profile_serializer.data

            image = ProfileImageSerializer(instance=profile.image)

            if image.data['image'] is None:
                profile_data['image'] = 'http://res.cloudinary.com/hjfb74ijq/image/upload/v1479381082/default_rutr05.jpg'
            else:
                profile_data['image'] = image.data['image']
            ret_data.append(profile_data)

        return Response(ret_data, status=200)


class JobPostingList(generics.ListCreateAPIView, ):
    serializer_class = JobPostingSerializer
    model = JobPosting

    def get_queryset(self):
        recruiter = self.request.query_params.get('recruiter', None)
        if recruiter is not None:

            user = User.objects.filter(username=recruiter)
            if user.exists():
                return JobPosting.objects.filter(recruiter=user.first().pk)
            return JobPosting.objects.none()
        return JobPosting.objects.all()


class JobPostingDetail(generics.RetrieveUpdateDestroyAPIView, ):
    serializer_class = JobPostingSerializer
    model = JobPosting
    lookup_field = 'id'
    lookup_url_kwarg = 'job_id'

    def get_queryset(self):
        job_id = self.kwargs.get('job_id', None)
        return JobPosting.objects.filter(id=job_id)

    def patch(self, request, *args, **kwargs):
        job_posting = self.get_queryset()
        if job_posting.exists():
            job_posting = job_posting.first()
            if request.user != job_posting.recruiter:
                raise Http404

        return super(JobPostingDetail, self).patch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        job_posting = self.get_queryset()
        if job_posting.exists():
            job_posting = job_posting.first()
            if request.user != job_posting.recruiter:
                raise Http404

        return super(JobPostingDetail, self).delete(request, *args, **kwargs)


class ProfileApplicationIDs(APIView, ):

    def get(self, request, *args, **kwargs):

        username = self.kwargs.get('username', None)
        if not username:
            raise Http404

        applications = JobApplication.objects.filter(profile__user__username=username).values_list('job_posting_id', flat=True)
        return Response(applications, status=200)


class ProfileApplicationList(generics.ListAPIView, ):
    serializer_class = JobApplicationSerializer
    model = JobApplication

    def get_queryset(self):
        username = self.kwargs.get('username', None)
        if not username:
            raise Http404

        applications = JobApplication.objects.filter(profile__user__username=username)
        return applications


class JobApplicationList(generics.ListCreateAPIView, ):
    serializer_class = JobApplicationSerializer
    model = JobApplication

    def get_queryset(self):
        job_id = self.kwargs.get('job_id', None)

        if self.request.query_params.get('recruit', False):
            return JobApplication.objects.filter(job_posting_id=job_id).filter(
                Q(status='Pending') | Q(status='Accepted'))

        return JobApplication.objects.filter(job_posting_id=job_id)


class JobApplicationDetail(generics.RetrieveUpdateDestroyAPIView, ):
    serializer_class = JobApplicationSerializer
    model = JobApplication
    lookup_url_kwarg = 'application_id'
    lookup_field = 'id'

    def get_queryset(self):
        job_id = self.kwargs.get('job_id', None)
        application_id = self.kwargs.get('application_id', None)
        return JobApplication.objects.filter(id=application_id, job_posting_id=job_id)

    def patch(self, request, *args, **kwargs):
        application = self.get_queryset()
        if application.exists():
            application = application.first()
            #if request.user != application.job_posting.recruiter or application.profile.user:
            #    raise Http404
        else:
            raise Http404

        return super(JobApplicationDetail, self).patch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        application = self.get_queryset()
        if application.exists():
            application = application.first()
            if request.user != application.job_posting.recruiter or application.profile.user:
                raise Http404

        return super(JobApplicationDetail, self).delete(request, *args, **kwargs)


class InviteViaEmail(APIView, ):
    """
    Sends a basic invite email to someone
    """

    def post(self, request, *args, **kwargs):

        email = request.data.get('email', None)
        link = request.data.get('link', None)
        user = request.user

        profile = Profile.objects.get(user=user)

        try:
            validate_email(email)
        except ValidationError:
            return Response({'error': 'email field must contain a valid email address'})

        if link is None or not isinstance(link, str):
            return Response({'error': 'link field must be a string'})

        send_mail(
            'You got invited to CVConnect!',
            'Hey, you just got invited to CVConnect by {}, click the following link to register {}'.format(
                profile.preferred_name, link
            ),
            'no-reply@cvconnect.com',
            [email, ],
            fail_silently=False,
        )
        return Response({'success': 'email sent'}, status=200)


class ForgottenPasswordEmail(APIView, ):
    """
    Sends a email to request a password reset
    """

    def post(self, request, *args, **kwargs):

        email = request.data.get('email', None)
        link = request.data.get('link', None)

        profile = Profile.objects.filter(user__email=email)

        if not profile.exists():
            raise Http404
        profile = profile.first()

        try:
            validate_email(email)
        except ValidationError:
            return Response({'error': 'email field must contain a valid email address'})

        forgot_pass_token = ForgottenPasswordToken(
            user=profile.user,
            token=uuid4()
        )
        forgot_pass_token.save()

        link = link + '?token=' + str(forgot_pass_token.token)
        print(link)

        send_mail(
            'Reset your CVConnect password!',
            'Hey {}, you just requested a password reset for CVConnect, click the following link to reset your password {}'.format(
                profile.preferred_name, link
            ),
            'no-reply@cvconnect.com',
            [email, ],
            fail_silently=False,
        )
        return Response({'success': 'email sent'}, status=200)


class ProfileImageList(APIView, ):

    def get(self, request, *args, **kwargs):

        username = kwargs.get('username')
        profile = Profile.objects.filter(user__username=username)
        if profile.exists():
            profile = profile.first()
        else:
            raise Http404

        image = ProfileImageSerializer(instance=profile.image)

        ret = image.data
        if ret['image'] is None:
            ret['image'] = 'http://res.cloudinary.com/hjfb74ijq/image/upload/v1479381082/default_rutr05.jpg'

        return Response(ret, status=200)

    def post(self, request, *args, **kwargs):

        username = kwargs.get('username')
        profile = Profile.objects.filter(user__username=username)
        if profile.exists():
            profile = profile.first()
        else:
            raise Http404

        # Create the image
        image = ProfileImageSerializer(data=request.data)
        if image.is_valid():
            image.save()
            profile.image = image.instance
            profile.save()
        else:
            return Response(image.errors, status=400)

        return Response(image.to_representation(image.instance), status=200)


class ResetPassword(APIView, ):
    """
    Resets a users password using a ForgottenPasswordToken
    """

    def post(self, request, *args, **kwargs):

        token = request.data.get('token', None)
        password = request.data.get('password', None)

        forgot_pass_token = ForgottenPasswordToken.objects.filter(token=token)
        if not forgot_pass_token.exists():
            raise Http404
        forgot_pass_token = forgot_pass_token.first()

        user = forgot_pass_token.user
        user.set_password(password)
        user.save()

        return Response({'success': 'password reset'}, status=200)


class Search(APIView, ):
    """
    Returns a bunch of objects with links to detail pages
    """

    def get(self, request, *args, **kwargs):

        query = self.kwargs.get('query_string', None)

        objs = []
        if query is not None:
            profiles = Profile.objects.filter(full_name__contains=query)
            jobs = JobPosting.objects.filter(position__contains=query)
            skills = Skill.objects.filter(name__contains=query)
            locations = Profile.objects.filter(country__contains=query)
        else:
            profiles = Profile.objects.all()
            jobs = JobPosting.objects.all()
            skills = Skill.objects.all()
            locations = Profile.objects.all()

        for profile in profiles:
            objs.append({
                "type": "profiles",
                "subtype": "profiles",
                "id": profile.user.username,
                "visible_id": profile.full_name,
                "image": ProfileImageSerializer(profile.image).to_representation(profile.image)['image'],
                "match": profile.full_name
            })

        for job in jobs:
            objs.append({
                "type": "jobs",
                "subtype": "jobs",
                "id": job.id,
                "visible_id": job.position + " at " + job.company,
                "match": job.position + " at " + job.company
            })

        for skill in skills:
            objs.append({
                "type": "profiles",
                "subtype": "skills",
                "id": skill.profile.user.username,
                "visible_id": skill.profile.full_name,
                "match": skill.name
            })

        for location in locations:
            objs.append({
                "type": "profiles",
                "subtype": "locations",
                "id": location.user.username,
                "visible_id": location.full_name,
                "match": location.country
            })

        return Response(objs, status=200)


class RegisterConnection(APIView, ):
    """
    Connects two profiles
    """

    def post(self, request, *args, **kwargs):

        # usernames of the two profiles
        first = self.request.data.get('first', None)
        second = self.request.data.get('second', None)

        if first is None or second is None:
            raise Http404

        first = Profile.objects.filter(user__username=first)
        second = Profile.objects.filter(user__username=second)

        if not first.exists() or not second.exists():
            raise Http404

        first = first.first()
        second = second.first()

        first.connections.add(second)
        second.connections.add(first)
        first.save()
        second.save()

        return Response({"success": "connected"}, status=200)


class ConnectionList(generics.ListAPIView, ):
    serializer_class = ProfileSerializer
    model = Profile

    def get_queryset(self):
        # Only get connections for the profile that the endpoint hits
        # E.g. /api/profiles/matt/connections/ only returns matts connections

        username = self.kwargs.get('username', None)
        if username is None:
            return Profile.objects.none()

        profile = Profile.objects.filter(user__username=username)
        if not profile.exists():
            return Profile.objects.none()

        return profile.first().connections.all()

    def get(self, request, *args, **kwargs):

        queryset = self.get_queryset()
        ret_data = []

        for profile in queryset:
            profile_serializer = ProfileSerializer(instance=profile)
            profile_data = profile_serializer.data

            image = ProfileImageSerializer(instance=profile.image)

            if image.data['image'] is None:
                profile_data['image'] = 'http://res.cloudinary.com/hjfb74ijq/image/upload/v1479381082/default_rutr05.jpg'
            else:
                profile_data['image'] = image.data['image']
            ret_data.append(profile_data)

        return Response(ret_data, status=200)


class EducationDescriptionList(generics.ListCreateAPIView, ):
    serializer_class = EducationDescriptionSerializer
    model = EducationDescription

    def get_queryset(self):
        username = self.kwargs.get('username', None)
        if username:
            return EducationDescription.objects.filter(profile__user__username=username)
        else:
            return EducationDescription.objects.none()


class EducationDescriptionDetail(generics.RetrieveUpdateDestroyAPIView, ):
    serializer_class = EducationDescriptionSerializer
    model = EducationDescription
    lookup_url_kwarg = 'edu_hist_id'
    lookup_field = 'id'

    def get_queryset(self):
        username = self.kwargs.get('username', None)
        if username:
            return EducationDescription.objects.filter(profile__user__username=username)
        else:
            return EducationDescription.objects.none()


class EmploymentDescriptionList(generics.ListCreateAPIView, ):
    serializer_class = EmploymentDescriptionSerializer
    model = EmploymentDescription

    def get_queryset(self):
        username = self.kwargs.get('username', None)
        if username:
            return EmploymentDescription.objects.filter(profile__user__username=username)
        else:
            return EmploymentDescription.objects.none()


class EmploymentDescriptionDetail(generics.RetrieveUpdateDestroyAPIView, ):
    serializer_class = EmploymentDescriptionSerializer
    model = EmploymentDescription
    lookup_url_kwarg = 'job_hist_id'
    lookup_field = 'id'

    def get_queryset(self):
        username = self.kwargs.get('username', None)
        if username:
            return EmploymentDescription.objects.filter(profile__user__username=username)
        else:
            return EmploymentDescription.objects.none()


class SkillList(generics.ListCreateAPIView, ):
    serializer_class = SkillSerializer
    model = Skill

    def get_queryset(self):
        username = self.kwargs.get('username', None)
        if username:
            return Skill.objects.filter(profile__user__username=username)
        else:
            return Skill.objects.none()


class SkillDetail(generics.RetrieveUpdateDestroyAPIView, ):
    serializer_class = SkillSerializer
    model = Skill
    lookup_url_kwarg = 'skill_id'
    lookup_field = 'id'

    def get_queryset(self):
        username = self.kwargs.get('username', None)
        if username:
            return Skill.objects.filter(profile__user__username=username)
        else:
            return Skill.objects.none()


class CompanyList(generics.ListCreateAPIView, ):
    serializer_class = CompanySerializer
    model = Company

    def get_queryset(self):
        return Company.objects.all()


class CompanyDetail(generics.RetrieveUpdateDestroyAPIView, ):
    serializer_class = CompanySerializer
    model = Company
    lookup_url_kwarg = 'company_id'
    lookup_field = 'id'

    def get_queryset(self):
        manages = CompanyManager.objects.filter(profile__user=self.request.user).values_list('company_id', flat=True)
        return Company.objects.filter(pk__in=manages)


class FeedPostList(generics.ListCreateAPIView, ):
    serializer_class = FeedPostSerializer
    model = FeedPost

    def get_queryset(self):

        username = self.kwargs.get('username', None)
        if username is None:
            raise Http404

        return FeedPost.objects.filter(user__username=username).order_by('-created')


class UserJobPostingsList(generics.ListAPIView, ):
    serializer_class = JobPostingSerializer
    model = JobPosting

    def get_queryset(self):
        username = self.kwargs.get('username', None)
        if username is None:
            raise Http404

        user = User.objects.filter(username=username)
        if user.exists():
            return JobPosting.objects.filter(recruiter=user.first().pk)

        return JobPosting.objects.none()


class ChangePassword(APIView, ):

    def post(self, request, *args, **kwargs):
        """
        Takes a username, current_password and new_password.
        Changes the users password to the new password
        Returns the users new auth token

        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        username = request.data.get('username', None)
        current_password = request.data.get('current_password', None)
        new_password = request.data.get('new_password', None)

        if username is None or current_password is None or new_password is None:
            raise Http404

        user = User.objects.filter(username=username)
        if not user.exists():
            raise Http404

        user = user.first()

        from django.contrib.auth.hashers import check_password
        if check_password(current_password, user.password):
            user.set_password(new_password)
            user.save()
        else:
            raise Http404

        from rest_framework.authtoken.models import Token

        token = Token.objects.get(user=user)
        return Response({'token': token.key}, status=200)


class DeleteConnection(APIView, ):
    """
    Deletes a connection
    """

    def post(self, request, *args, **kwargs):

        # usernames of the two profiles
        first = self.request.data.get('first', None)
        second = self.request.data.get('second', None)

        if first is None or second is None:
            raise Http404

        first = Profile.objects.filter(user__username=first)
        second = Profile.objects.filter(user__username=second)

        if not first.exists() or not second.exists():
            raise Http404

        first = first.first()
        second = second.first()

        first.connections.remove(second)
        second.connections.remove(first)
        first.save()
        second.save()

        return Response({"success": "deconnected"}, status=200)


class SocialLinkList(generics.ListCreateAPIView, ):
    # TODO: David
    pass


class SocialLinkDetail(generics.RetrieveUpdateDestroyAPIView, ):
    # TODO: David
    pass


class CompanyManagerList(generics.ListCreateAPIView, ):
    # TODO: David
    pass


class CompanyManagerDetail(generics.RetrieveUpdateDestroyAPIView, ):
    # TODO: David
    pass