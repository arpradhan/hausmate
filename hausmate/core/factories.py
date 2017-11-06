from faker import Faker

from django.contrib.auth.models import User

fake = Faker()


def create_fake_user():
    email = fake.email()
    return User.objects.create_user(
        email,
        email,
        fake.password(),
        first_name=fake.first_name(),
        last_name=fake.last_name(),
    )
