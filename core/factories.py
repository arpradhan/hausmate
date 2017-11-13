from faker import Faker

from users.models import User

fake = Faker()


def create_fake_user():
    return User.objects.create_user(
        fake.first_name(),
        fake.email(),
        fake.password(),
    )
