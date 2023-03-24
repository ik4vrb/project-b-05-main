from django.shortcuts import render, redirect
import requests, re
from django.views import View
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from .forms import ThreadForm, MessageForm, StudySessionForm
from .models import ThreadModel, MessageModel, Account, Course, StudySession
from django.db.models import Q
from django.contrib import messages


def home(request):
    return render(request, "StudyBuddy/home.html")


def dept_list(request):
    departments = requests.get('http://luthers-list.herokuapp.com/api/deptlist/?format=json').json()

    return render(request, 'StudyBuddy/dept_list.html', {'departments': departments})


def searchDep(request):
    if request.method == 'GET':
        departments = requests.get('http://luthers-list.herokuapp.com/api/deptlist/?format=json').json()
        search = request.GET.get('search').upper()
        subjects = []
        for department in departments:
            valid = True
            if len(search) <= len(department['subject']):
                for i in range(0, len(search)):
                    if search[i] != department['subject'][i]:
                        valid = False
            else:
                valid = False
            if valid:
                subjects.append(department)
        result = subjects
        return render(request, 'StudyBuddy/depSearch.html', {'result': result})


class CourseSearchResults(ListView):
    model = Course
    template_name = 'StudyBuddy/classsearch.html'

    def get_queryset(self):
        department = self.kwargs.get('department')
        course = requests.get('http://luthers-list.herokuapp.com/api/dept/' + department + '?format=json').json()
        search = self.request.GET.get('search')
        search = re.sub(r'[^0-9]', '', search)
        subjects = []
        for c in course:
            valid = True
        #Did the user even search for anything?
            if len(search) <= 0:
                valid = False
        #Is it a catalog number?
            #elif str(search[0]) in {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9'}:
            elif len(search) <= len(c['catalog_number']):
                for i in range(0, len(search)):
                    if search[i] != c['catalog_number'][i]:
                        valid = False

        #Else if its not a catalog number, it must be a course name
            else:
                valid = False

                #Tried some different stuff. Commented code is random bits from various attempts
                #spsearch = search.split(" ")
                #desc = c['description'].split(" ")
                #for j in range(0, min(len(desc), len(spsearch))):
                #for i in range(0,min(len(desc[j])), len(spsearch[j])):
                    #if spsearch[j] not in desc:
                        #valid = False

            if valid:
                subjects.append(c)
        for c in reversed(subjects):
            for meeting in c['meetings']:
                if meeting['start_time'] != "" and meeting['end_time'] != "":
                    start = meeting['start_time']
                    end = meeting['end_time']
                    tempstrs = start.split('.')
                    tempstre = end.split('.')

                    first = str(int(tempstrs[0]) % 12)
                    second = str(int(tempstre[0]) % 12)

                    if first == '0':
                        first = '12'
                    if second == '0':
                        second = '12'

                    type1 = 'pm'
                    if int(first) >= 8:
                        type1 = 'am'

                    type2 = 'pm'
                    if int(second) >= 8 and type1 == "am":
                        type2 = 'am'

                    meeting['start_time'] = first + ':' + tempstrs[1] + ' ' + type1
                    meeting['end_time'] = second + ':' + tempstre[1] + ' ' + type2
                else:
                    subjects.remove(c)
        return subjects

    def get_context_data(self, **kwargs):
        context = super(CourseSearchResults, self).get_context_data(**kwargs)
        context['department'] = self.kwargs.get('department')
        return context


class ShowClasses(View):
    def get(self, request, department):
        courses = requests.get('http://luthers-list.herokuapp.com/api/dept/' + department + '?format=json').json()
        for c in reversed(courses):
            for meeting in c['meetings']:
                if meeting['start_time'] != "" and meeting['end_time'] != "":
                    start = meeting['start_time']
                    end = meeting['end_time']
                    tempstrs = start.split('.')
                    tempstre = end.split('.')

                    first = str(int(tempstrs[0]) % 12)
                    second = str(int(tempstre[0]) % 12)

                    if first == '0':
                        first = '12'
                    if second == '0':
                        second = '12'

                    type1 = 'pm'
                    if int(first) >= 8:
                        type1 = 'am'

                    type2 = 'pm'
                    if int(second) >= 8 and type1 == "am":
                        type2 = 'am'

                    meeting['start_time'] = first + ':' + tempstrs[1] + ' ' + type1
                    meeting['end_time'] = second + ':' + tempstre[1] + ' ' + type2
                else:
                    courses.remove(c)
        if request.user.id is not None:
            account = Account.objects.get(pk=request.user.username)
            return render(request, 'StudyBuddy/class.html', {'courses': courses, 'dep': department, 'account': account})
        else:
            return render(request, 'StudyBuddy/class.html', {'courses': courses, 'dep': department})

    def post(self, request, department):
        name = request.POST.get('name')
        number = request.POST.get('number')
        professor = request.POST.get('professor')

        try:
            course = Course.objects.get(pk=name)
        except Course.DoesNotExist:
            course = Course.objects.create(
                name=name,
                department=department,
                number=number,
                professor=professor
            )
        if request.user.id is not None:
            account = Account.objects.get(pk=request.user.username)
            try:
                account.courses.get(pk=course.pk)
                messages.info(request, "This course is already added to your profile")
            except Course.DoesNotExist:
                account.courses.add(course)
                messages.success(request, "Class was added successfully!")
        return redirect('show_classes', department)


class Profile(View):
    def get(self, request):
        if request.user.id is not None:
            account = Account.objects.get(pk=request.user.username)
            context = {
                'account': account,
                'user': request.user
            }
            return render(request, 'StudyBuddy/profile.html', context)
        else:
            return render(request, 'StudyBuddy/error.html')

    def post(self, request):
        if request.user.id is not None:
            account = Account.objects.get(pk=request.user.username)
            course_name = request.POST.get('course')
            course = Course.objects.get(name=course_name)
            topic = request.POST.get('topic')
            study_session = StudySession.objects.get(course=course, topic=topic)

            action = request.POST.get('action')
            if action == "delete":
                study_session.delete()
            else:
                account.study_sessions.remove(study_session)
            return redirect('profile')
        else:
            return render(request, 'StudyBuddy/error.html')


class Friends(View):
    def get(self, request):
        if request.user.id is not None:
            account = Account.objects.get(pk=request.user.username)
            context = {
                'account': account,
            }
            return render(request, 'StudyBuddy/friends.html', context)
        else:
            return render(request, 'StudyBuddy/error.html')

    def post(self, request):
        if request.user.id is not None:
            account = Account.objects.get(pk=request.user.username)
            context = {
                'account': account,
            }
            friend_username = request.POST.get('username')
            if friend_username != account.username:
                friend = Account.objects.get(pk=friend_username)
                account.friends.add(friend)

                messages.success(request, "You and " + friend_username + " are now friends!")
            else:
                messages.warning(request, "You cannot add yourself as a friend!")
            return render(request, 'StudyBuddy/friends.html', context)
        else:
            return render(request, 'StudyBuddy/error.html')


class UserSearchResults(ListView):
    model = Account
    template_name = 'StudyBuddy/searchUsers.html'

    def get_queryset(self):
        query = self.request.GET.get('search')
        if " " in query:
            query1 = query.split(" ")[0]
            query2 = query.split(" ")[1]
            return Account.objects.filter(Q(first_name=query1) | Q(last_name=query2))
        return Account.objects.filter(
            Q(username=query) | Q(username__contains=query) |
            Q(first_name=query) | Q(first_name__contains=query) |
            Q(last_name=query) | Q(last_name__contains=query))


class StudySessions(View):
    def get(self, request, department, number):
        name = request.GET.get('name')
        professor = request.GET.get('professor')

        try:
            course = Course.objects.get(pk=name)
        except Course.DoesNotExist:
            course = Course.objects.create(
                name=name,
                department=department,
                number=number,
                professor=professor
            )
        context = {
            'course': course,
        }
        return render(request, 'StudyBuddy/study_sessions.html', context)

    def post(self, request, department, number):
        name = request.POST.get('name')
        course = Course.objects.get(pk=name)
        topic = request.POST.get('topic')
        study_session = course.study_sessions.get(course=course, topic=topic)
        account = Account.objects.get(pk=request.user.username)
        if account not in study_session.members.all():
            study_session.members.add(account)
            messages.success(request, "You have joined study session for " + course.name)
        else:
            messages.warning(request, "You have already joined this study session")

        response = redirect('study_sessions', department, number)
        response['Location'] += '?name=' + name + '&professor=' + course.professor
        return response


class CreateSession(CreateView):
    model = StudySession
    form_class = StudySessionForm
    template_name = 'StudyBuddy/create_session.html'

    def form_valid(self, form):
        if self.request.user.id is None:
            return render(self.request, 'StudyBuddy/error.html')
        form.data._mutable = True
        account = Account.objects.get(pk=self.request.user.username)
        form = form.save()
        if form.members.all():
            form.members.add(account)
        else:
            form.members.set([account])
        messages.success(self.request, "Study session was created successfully!")
        return super(CreateSession, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('show_classes', kwargs={'department': self.kwargs.get('department')})

    def get_form_kwargs(self):
        """ Passes the request object and initial object to the form class."""
        department = self.kwargs.get('department')
        number = self.kwargs.get('number')
        professor = self.request.GET.get('professor')
        name = self.request.GET.get('name')

        try:
            course = Course.objects.get(pk=name)
        except Course.DoesNotExist:
            course = Course.objects.create(
                name=name,
                department=department,
                number=number,
                professor=professor
            )

        kwargs = super(CreateSession, self).get_form_kwargs()
        kwargs['request'] = self.request
        kwargs['initial'] = {'course': course}
        return kwargs


class ListThreads(View):
    def get(self, request, *args, **kwargs):
        if request.user.id is not None:
            threads = ThreadModel.objects.filter(Q(user=request.user) | Q(receiver=request.user))
            context = {
                'threads': threads
            }
            return render(request, 'StudyBuddy/inbox.html', context)
        else:
            return render(request, 'StudyBuddy/error.html')


class CreateThread(View):
    def get(self, request, *args, **kwargs):
        form = ThreadForm()
        context = {
            'form': form
        }
        return render(request, 'StudyBuddy/create_thread.html', context)

    def post(self, request, *args, **kwargs):
        form = ThreadForm(request.POST)
        username = request.POST.get('username')
        try:
            receiver = User.objects.get(username=username)
            if ThreadModel.objects.filter(user=request.user, receiver=receiver).exists():
                thread = ThreadModel.objects.filter(user=request.user, receiver=receiver)[0]
                return redirect('thread', pk=thread.pk)

            if form.is_valid():
                sender_thread = ThreadModel(
                    user=request.user,
                    receiver=receiver
                )
                sender_thread.save()
                thread_pk = sender_thread.pk
                return redirect('thread', pk=thread_pk)
        except User.DoesNotExist:
            return redirect('create-thread')


class ThreadView(View):
    def get(self, request, pk, *args, **kwargs):
        form = MessageForm()
        thread = ThreadModel.objects.get(pk=pk)
        message_list = MessageModel.objects.filter(thread__pk__contains=pk)
        context = {
            'thread': thread,
            'form': form,
            'message_list': message_list
        }
        return render(request, 'StudyBuddy/thread.html', context)


class CreateMessage(View):
    def post(self, request, pk, *args, **kwargs):
        thread = ThreadModel.objects.get(pk=pk)
        if thread.receiver == request.user:
            receiver = thread.user
        else:
            receiver = thread.receiver

        message = MessageModel(
            thread=thread,
            sender_user=request.user,
            receiver_user=receiver,
            body=request.POST.get('message')
        )

        message.save()
        return redirect('thread', pk=pk)
