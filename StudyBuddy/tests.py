from unittest import skip
from django.test import TestCase
from django.http import HttpRequest
from http import HTTPStatus
from django.db import IntegrityError
from django.contrib import messages
from .models import ThreadModel, MessageModel, User, Account, Course, StudySession
from .views import Friends, ShowClasses, StudySessions
from .forms import StudySessionForm


class PrivateMessageTests(TestCase):
    def test_create_thread(self):
        user1 = User.objects.create_user(username='user1', password='foo')
        user2 = User.objects.create_user(username='user2', password='foo')

        thread1 = ThreadModel.objects.create(user=user1, receiver=user2, has_unread=False)
        self.assertEqual(user1, thread1.user)
        self.assertEqual(user2, thread1.receiver)
        self.assertFalse(thread1.has_unread)

        thread2 = ThreadModel.objects.create(user=user1, receiver=user2, has_unread=True)
        self.assertTrue(thread2.has_unread)

    def test_create_message(self):
        user1 = User.objects.create_user(username='user1', password='foo')
        user2 = User.objects.create_user(username='user2', password='foo')
        thread = ThreadModel.objects.create(user=user1, receiver=user2, has_unread=True)

        message = MessageModel.objects.create(thread=thread, sender_user=thread.user, receiver_user=thread.receiver, body='hi user2', is_read=False)

        self.assertEqual(user1, message.sender_user)
        self.assertEqual(thread.user, message.sender_user)
        self.assertEqual(user2, message.receiver_user)
        self.assertEqual(thread.receiver, message.receiver_user)

        if thread.has_unread is False:
            self.assertTrue(message.is_read)


class ModelCreationTests(TestCase):
    def setUp(self):
        self.course = Course.objects.create(
            name='Advanced Software Development Methods',
            department='CS',
            number='3240',
            professor='McBurney'
        )
        self.account = Account.objects.create(
            username='test',
            first_name='first',
            last_name='last',
            year='First',
            major='CS',
            minor='none'
        )
        self.studysession = StudySession.objects.create(
            course=self.course,
            topic="Test"
        )

    def test_create_course(self):
        self.assertEqual(self.course.name, 'Advanced Software Development Methods')
        self.assertEqual(self.course.department, 'CS')
        self.assertEqual(self.course.number, '3240')
        self.assertEqual(self.course.professor, 'McBurney')

    def test_create_account(self):
        self.assertEqual(self.account.username, 'test')
        self.assertEqual(self.account.first_name, 'first')
        self.assertEqual(self.account.last_name, 'last')
        self.assertEqual(self.account.year, 'First')
        self.assertEqual(self.account.major, 'CS')
        self.assertEqual(self.account.minor, 'none')

    def test_unique_usernames(self):
        with self.assertRaises(IntegrityError):
            Account.objects.create(
                username='test',
                first_name='first',
                last_name='last',
                year='First',
                major='CS',
                minor='none'
            )

    def test_create_studysession(self):
        member1 = self.account
        self.studysession.members.add(member1)
        member2 = self.studysession.members.create(
            username='test2',
            first_name='first',
            last_name='last',
            year='First',
            major='CS',
            minor='none'
        )

        self.assertEqual(self.studysession.course, self.course)
        self.assertEqual(self.studysession.topic, "Test")
        self.assertEqual(self.studysession.members.get(pk=member1.pk), member1)
        self.assertEqual(self.studysession.members.get(pk=member1.pk), self.account)
        self.assertEqual(self.studysession.members.get(pk=member2.pk), member2)
        self.assertNotEqual(self.studysession.members.get(pk=member1.pk), self.studysession.members.get(pk=member2.pk))
        self.assertEqual(self.studysession.members.count(), 2)


class AddClassTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username='test',
            password='password'
        )
        self.account = Account.objects.create(
            username=self.user.username,
            first_name='first',
            last_name='last',
            year='First',
            major='CS',
            minor='none'
        )
        self.assertEqual(1, len(User.objects.all()))
        self.assertEqual(1, len(Account.objects.all()))
        self.assertEqual(0, self.account.courses.count())

    def test_add_class(self):
        request = HttpRequest()
        request._messages = messages.storage.default_storage(request)
        request.method = "POST"
        request.POST['name'] = 'name'
        request.POST['number'] = 'number'
        request.POST['professor'] = 'professor'
        department = 'department'
        request.user = self.user

        self.assertEqual(0, len(Course.objects.all()))

        response = ShowClasses.post(self, request, department)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(1, len(Course.objects.all()))
        self.assertEqual(1, self.account.courses.count())
        self.assertEqual(self.account.courses.get(pk='name').name, "name")
        self.assertEqual(self.account.courses.get(pk='name').department, "department")
        self.assertEqual(self.account.courses.get(pk='name').number, "number")
        self.assertEqual(self.account.courses.get(pk='name').professor, "professor")


class ErrorTests(TestCase):
    def test_profile_error(self):
        response = self.client.get('/profile/')
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'StudyBuddy/error.html')
        self.assertTemplateNotUsed(response, 'StudyBuddy/profile.html')

    def test_inbox_error(self):
        response = self.client.get('/inbox/')
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'StudyBuddy/error.html')
        self.assertTemplateNotUsed(response, 'StudyBuddy/inbox.html')


class StudySessionsViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username='test',
            password='password'
        )
        self.assertEqual(1, len(User.objects.all()))

    def test_view_study_session(self):
        request = HttpRequest()
        request.method = "GET"
        request.user = self.user
        request.GET['professor'] = 'professor'
        request.GET['name'] = 'name'
        department = 'department'
        number = 'number'

        self.assertEqual(0, len(Course.objects.all()))

        response = StudySessions.get(self, request, department, number)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(1, len(Course.objects.all()))
        course = Course.objects.get(pk="name")
        self.assertEqual(0, course.study_sessions.count())


class CreateSessionTest(TestCase):
    def setUp(self):
        self.url = '/classes/department-number/create-session?name=name&professor=professor'
        self.data = {
            'topic': 'topic',
            'date': '2022-11-21',
            'time': '20:02'
        }
        self.course = Course(
            name='name',
            department='department',
            number='number',
            professor='professor'
        )
        self.user = User.objects.create(
            username='test',
            password='password'
        )
        self.account = Account.objects.create(
            username=self.user.username,
            first_name='first',
            last_name='last',
            year='First',
            major='CS',
            minor='none'
        )
        request = HttpRequest()
        request.POST = self.data
        request.user = self.user
        self.request = request

    def test_empty_form(self):
        form = StudySessionForm(request=self.request)
        self.assertIn("date", form.fields)
        self.assertIn("time", form.fields)
        self.assertIn("topic", form.fields)
        self.assertTrue(form.fields["course"].disabled)

    def test_get(self):
        with self.assertRaises(Account.DoesNotExist):
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, HTTPStatus.OK)
            self.assertContains(response, "<h1>Create Session</h1>", html=True)

    def test_post(self):
        self.client.force_login(self.user)
        self.assertEqual(0, self.course.study_sessions.count())
        self.assertEqual(0, len(StudySession.objects.filter(course=self.course)))
        self.assertEqual(0, self.account.study_sessions.count())
        response = self.client.post(self.url, data=self.data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response["Location"], "/classes/department")
        self.assertTemplateNotUsed(response, 'StudyBuddy/error.html')
        self.assertEqual(1, self.course.study_sessions.count())
        self.assertEqual(1, len(StudySession.objects.filter(course=self.course)))
        self.assertEqual(1, self.account.study_sessions.count())

    def test_post_no_login(self):
        with self.assertRaises(Account.DoesNotExist):
            response = self.client.post(self.url, data=self.data)
            self.assertEqual(response.status_code, HTTPStatus.OK)
            self.assertTemplateUsed(response, 'StudyBuddy/error.html')


class AddFriends(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username='test',
            password='password'
        )
        self.account = Account.objects.create(
            username='test',
            first_name='first',
            last_name='last',
            year='First',
            major='CS',
            minor='none'
        )
        self.friend = Account.objects.create(
            username='test2',
            first_name='first',
            last_name='last',
            year='First',
            major='CS',
            minor='none'
        )

    def test_get_request(self):
        request = HttpRequest()
        request.method = "GET"
        request.user = self.user

        response = Friends.get(self, request)

        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_get_client(self):
        response = self.client.get('/friends/')
        self.assertTemplateUsed(response, 'StudyBuddy/error.html')

    def test_post_request(self):
        request = HttpRequest()
        request._messages = messages.storage.default_storage(request)
        request.method = "POST"
        request.POST['username'] = self.friend.username
        request.user = self.user

        self.assertEqual(0, len(self.account.friends.all()))
        self.assertEqual(0, len(self.friend.friends.all()))

        response = Friends.post(self, request)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(1, len(self.account.friends.all()))
        self.assertEqual(1, len(self.friend.friends.all()))
        self.assertEqual(self.friend, self.account.friends.get(username='test2'))
        self.assertEqual(self.account, self.friend.friends.get(username='test'))

    def test_post_client(self):
        response = self.client.post('/friends/', data={'username': self.friend.username})
        self.assertTemplateUsed(response, 'StudyBuddy/error.html')

        self.client.force_login(self.user)
        response = self.client.get('/friends/')
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'StudyBuddy/friends.html')


class SearchTesting(TestCase):
    def test_dep_search_no_result(self):
        data = {
            'search': 'name'
        }
        response = self.client.get('/classes/search/', data)

        self.assertEquals(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'StudyBuddy/depSearch.html')
        self.assertContains(response, "<h4>No Result</h4>", html=True)

    def test_dep_search_result(self):
        data = {
            'search': 'ACCT'
        }
        response = self.client.get('/classes/search/', data)

        self.assertEquals(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'StudyBuddy/depSearch.html')
        self.assertNotContains(response, "<h4>No Result</h4>", html=True)

    def test_course_search_no_result(self):
        data = {
            'search': '1234'
        }
        response = self.client.get('/classes/ACCT/search/', data)

        self.assertEquals(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'StudyBuddy/classsearch.html')
        self.assertContains(response, "<h4>No Result</h4>", html=True)

    def test_course_search_result(self):
        data = {
            'search': '2010'
        }
        response = self.client.get('/classes/ACCT/search/', data)

        self.assertEquals(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'StudyBuddy/classsearch.html')
        self.assertNotContains(response, "<h4>No Result</h4>", html=True)
        self.assertContains(response, "<b>ACCT 2010</b>", html=True)


class JoinSessionTest(TestCase):
    def setUp(self):
        self.course = Course.objects.create(
            name='name',
            department='department',
            number='number',
            professor='professor'
        )
        self.study_session = StudySession.objects.create(
            course=self.course,
            topic='topic',
            date='2022-11-21',
            time='20:02'
        )
        self.user = User.objects.create(
            username='test',
            password='password'
        )
        self.account = Account.objects.create(
            username=self.user.username,
            first_name='first',
            last_name='last',
            year='First',
            major='CS',
            minor='none'
        )

    def test_join_session(self):
        request = HttpRequest()
        request.POST['name'] = self.study_session.course.name
        request.POST['topic'] = self.study_session.topic
        request._messages = messages.storage.default_storage(request)
        request.user = self.user

        self.assertEqual(1, len(self.course.study_sessions.all()))
        self.assertEqual(0, len(self.study_session.members.all()))

        response = StudySessions.post(self, request, self.course.department, self.course.number)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(1, len(self.study_session.members.all()))
        self.assertEqual(self.account, self.study_session.members.get(pk=self.user.username))
