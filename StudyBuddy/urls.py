
from django.urls import path
from .views import dept_list, searchDep, CourseSearchResults, ShowClasses, StudySessions, CreateSession


urlpatterns = [
    path('', dept_list, name='dept_list'),
    path('search/', searchDep, name='searchDep'),
    path('<department>/search/', CourseSearchResults.as_view(), name='searchCourse'),
    path('<department>', ShowClasses.as_view(), name='show_classes'),
    path('<department>-<number>/study-sessions', StudySessions.as_view(), name='study_sessions'),
    path('<department>-<number>/create-session', CreateSession.as_view(), name='create_session')
]
