from django.conf.urls import url, include
from django.contrib import admin

from api.views import UserList, UserDetail, ProfileList, ProfileDetail, JobPostingList, \
    JobPostingDetail, JobApplicationList, JobApplicationDetail, InviteViaEmail, ProfileRecommendations, \
    EducationDescriptionList, EducationDescriptionDetail, EmploymentDescriptionList, EmploymentDescriptionDetail, \
    SkillList, SkillDetail, CompanyList, CompanyDetail, ForgottenPasswordEmail, ResetPassword, Search, RegisterConnection, \
    ConnectionList, ProfileImageList, ProfileApplicationIDs, ProfileApplicationList, FeedPostList, UserJobPostingsList, \
    ChangePassword, DeleteConnection

urlpatterns = [
    url(r'^users/$', UserList.as_view()),
    url(r'^users/(?P<username>[a-zA-Z][a-zA-Z0-9_]+)/$', UserDetail.as_view()),
    url(r'^users/(?P<username>[a-zA-Z][a-zA-Z0-9_]+)/change-password/$', ChangePassword.as_view()),
    url(r'^profiles/$', ProfileList.as_view()),
    url(r'^profiles/(?P<username>[a-zA-Z][a-zA-Z0-9_]+)/$', ProfileDetail.as_view()),
    url(r'^profiles/(?P<username>[a-zA-Z][a-zA-Z0-9_]+)/recommendations/$', ProfileRecommendations.as_view()),
    url(r'^profiles/(?P<username>[a-zA-Z][a-zA-Z0-9_]+)/application_ids/$', ProfileApplicationIDs.as_view()),
    url(r'^jobs/$', JobPostingList.as_view()),
    url(r'^jobs/(?P<job_id>[0-9]+)/$', JobPostingDetail.as_view()),
    url(r'^jobs/(?P<job_id>[0-9]+)/applications/$', JobApplicationList.as_view()),
    url(r'^jobs/(?P<job_id>[0-9]+)/applications/(?P<application_id>[0-9]+)/$', JobApplicationDetail.as_view()),
    url(r'^send-invite/$', InviteViaEmail.as_view()),
    url(r'^forgot-password/$', ForgottenPasswordEmail.as_view()),
    url(r'^reset-password/$', ResetPassword.as_view()),
    url(r'^search/(?P<query_string>[a-zA-Z0-9_]*)/$', Search.as_view()),
    url(r'^connect/$', RegisterConnection.as_view()),
    url(r'^deconnect/$', DeleteConnection.as_view()),
    url(r'^profiles/(?P<username>[a-zA-Z][a-zA-Z0-9_]+)/image/$', ProfileImageList.as_view()),
    url(r'^profiles/(?P<username>[a-zA-Z][a-zA-Z0-9_]+)/connections/$', ConnectionList.as_view()),
    url(r'^profiles/(?P<username>[a-zA-Z][a-zA-Z0-9_]+)/education/$', EducationDescriptionList.as_view()),
    url(r'^profiles/(?P<username>[a-zA-Z][a-zA-Z0-9_]+)/education/(?P<edu_hist_id>[0-9]+)/$',
        EducationDescriptionDetail.as_view()),
    url(r'^profiles/(?P<username>[a-zA-Z][a-zA-Z0-9_]+)/employment/$', EmploymentDescriptionList.as_view()),
    url(r'^profiles/(?P<username>[a-zA-Z][a-zA-Z0-9_]+)/employment/(?P<job_hist_id>[0-9]+)/$',
        EmploymentDescriptionDetail.as_view()),
    url(r'^profiles/(?P<username>[a-zA-Z][a-zA-Z0-9_]+)/skills/$', SkillList.as_view()),
    url(r'^profiles/(?P<username>[a-zA-Z][a-zA-Z0-9_]+)/skills/(?P<skill_id>[0-9]+)/$', SkillDetail.as_view()),
    url(r'^profiles/(?P<username>[a-zA-Z][a-zA-Z0-9_]+)/applications/$', ProfileApplicationList.as_view()),
    url(r'^profiles/(?P<username>[a-zA-Z][a-zA-Z0-9_]+)/feedposts/$', FeedPostList.as_view()),
    url(r'^profiles/(?P<username>[a-zA-Z][a-zA-Z0-9_]+)/postings/$', UserJobPostingsList.as_view()),
    url(r'^companies/$', CompanyList.as_view()),
    url(r'^companies/(?P<company_id>[0-9]+)/$', CompanyDetail.as_view()),
]