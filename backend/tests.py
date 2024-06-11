from django.test import TestCase
from backend.models import Add_chanel,Profile
# Create your tests here.
class AddChanelTests(TestCase):
    def test_add_chanel(self):
        profile=Profile.objects.first()


        add = Add_chanel(username=profile,chanel_link="https://t.me/good")

        # Save the instance
        add.save()

        # Now, let's verify the attributes using assertions
        self.assertEqual(add.chanel_link, "https://t.me/good")
