from __future__ import unicode_literals

from django.db import models
import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

# Create your models here.
class Borrower(models.Model):
	borrower_id = models.AutoField(primary_key=True, db_column="borrower_id")
	ssn = models.CharField(max_length=9, db_column="ssn", unique = True)
	first_name = models.CharField(max_length=30, db_column="first_name")
	last_name = models.CharField(max_length=30, db_column="last_name")
	email = models.EmailField(db_column="email", unique = True)
	address = models.CharField(max_length=250, db_column="address")
	city = models.CharField(max_length=30, db_column="city")
	state = models.CharField(max_length=2, db_column="state")
	phone = models.CharField(max_length=10, db_column="phone")
	
	def clean(self, *args, **kwargs):
		if not re.match(r"^[0-9]+$", self.ssn):
			raise ValidationError({'ssn': _("SSN must be numbers of length 9.")})
		if not re.match(r"^[0-9]{10}$", self.phone):
			raise ValidationError({'phone': _("Phone number must be numbers of length 10.")})
		super(Borrower, self).clean(*args, **kwargs)

	class Meta:
		db_table = "borrowers"