from django.forms import ModelForm
from .models import Borrower

class BorrowerForm(ModelForm):
	class Meta:
		model = Borrower
		fields = ['ssn', 'first_name', 'last_name', 'email', 'address', 'city', 'state', 'phone']