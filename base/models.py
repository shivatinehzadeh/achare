from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class PhoneNumberCheck(models.Model):
    phone_number = models.CharField(max_length=11, unique=True)
    registration_status = models.BooleanField(default=False)
    user_ip = models.GenericIPAddressField()
    wrong_password_count = models.IntegerField(null=True)
    user_ip_wrong_count = models.IntegerField(null=True)
    is_lock = models.BooleanField(default=False)
    lock_until = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'PhoneNumberCheck'
        managed = True


class PersonInfo(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(max_length=100)
    user = models.ForeignKey('UserAccount', on_delete=models.DO_NOTHING, db_column='user_id')
    phone_register = models.ForeignKey(PhoneNumberCheck, on_delete=models.DO_NOTHING, db_column='phone_register')

    class Meta:
        db_table = 'PersonInfo'
        managed = True


class UserAccount(models.Model):
    password = models.CharField(_("password"), max_length=128)
    phone_register = models.OneToOneField(PhoneNumberCheck, on_delete=models.DO_NOTHING,
                                          db_column='phone_register')

    class Meta:
        db_table = 'UserAccount'
        managed = True
