from django.contrib.auth import get_user_model
from evans_django_tools.testsuite import UniqueFaker
from factory import Faker
from factory.declarations import LazyAttribute, SubFactory
from factory.django import DjangoModelFactory

from core.models import Hunt, Token

User = get_user_model()


class UserFactory(DjangoModelFactory):

    class Meta:
        model = User

    first_name = Faker('first_name_female')
    last_name = Faker('last_name_female')
    username = UniqueFaker('user_name')
    email = Faker('ascii_safe_email')


class HuntFactory(DjangoModelFactory):

    class Meta:
        model = Hunt

    name = Faker('catch_phrase')
    authors = Faker('company')
    start_date = Faker('date_time')
    visible = False
    allow_skip = False


# ... Sanjana should write other factories here


class TokenFactory(DjangoModelFactory):

    class Meta:
        model = Token

    user = SubFactory(UserFactory)
    name = LazyAttribute(lambda o: o.user.first_name + ' ' + o.user.last_name)
    reduced_name = LazyAttribute(lambda o: Token.reduce(o.name))
