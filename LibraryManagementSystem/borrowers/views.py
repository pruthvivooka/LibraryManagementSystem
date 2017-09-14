from django.shortcuts import render
from .models import Borrower
from .forms import BorrowerForm
from django.template import RequestContext

# Create your views here.
def home(request):
	form = None
	borrower_id = None
	if(request.method == 'POST'):
		form = BorrowerForm(request.POST)
		if form.is_valid():
			borrower = form.save()
			borrower_id = borrower.borrower_id
			form = BorrowerForm()
	else:
		form = BorrowerForm()
	context = {'form' : form, 'borrower_id' : borrower_id}
	return render(request, 'borrowers/home.html', context)