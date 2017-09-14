import datetime
from string import rsplit
from django.shortcuts import render, redirect
from django.core.exceptions import ValidationError
from django.db.models import Q, Sum, Count
from django.http import HttpResponseNotFound
from django.contrib import messages
from .models import BookLoan, Fine
from borrowers.models import Borrower
from django.http import JsonResponse
from django.db import connection
import sys

def home(request):
	context = {}
	return render(request, 'bookLoans/home.html', context)

def checkOut(request):
	book_loan = BookLoan()
	form_errors = None
	model_is_clean = True
	loan_id = None
	if (request.method == 'POST'):
		if 'book' in request.POST and 'borrower' in request.POST:
			book_loan.book_id = request.POST['book']
			book_loan.borrower_id = request.POST['borrower']
			book_loan.date_out = datetime.date.today()
			book_loan.due_date = book_loan.date_out + datetime.timedelta(days=14)
			book_loan.date_in = None
			try:
				book_loan.full_clean()
			except ValidationError as e:
				form_errors = e.message_dict
				model_is_clean = False
			if (model_is_clean):
				book_loan.save()
				loan_id = book_loan.loan_id
				book_loan = BookLoan()
			else :
				book_loan.book_id = request.POST['book'] if 'book' in request.POST else ""
				book_loan.borrower_id = request.POST['borrower'] if 'borrower' in request.POST else ""
	context = {'book_loan' : book_loan, 'form_errors' : form_errors, 'loan_id' : loan_id}
	return render(request, 'bookLoans/check_out.html', context)

def checkIn(request):
	book_id = None if ('book' not in request.GET) else request.GET['book']
	borrower_id = None if ('borrower_id' not in request.GET) else request.GET['borrower_id']
	borrower_name = None if ('borrower_name' not in request.GET) else request.GET['borrower_name']
	page_num = int(request.GET['page']) if 'page' in request.GET and request.GET['page'].isdigit() else 0
	book_loans = None
	nxt_params = None
	back_params = None
	if (any(x is not None for x in [book_id, borrower_id, borrower_name])):
		book_loans = BookLoan.objects.all().select_related('borrower').prefetch_related('borrower')
		book_loans = book_loans.filter(date_in__isnull = True)
		if book_id is not None and book_id != '':
			book_loans = book_loans.filter(book_id__exact = book_id)
		else:
			book_id = ''
		if borrower_id is not None and borrower_id != '':
			book_loans = book_loans.filter(borrower_id__exact = borrower_id)
		else:
			borrower_id = ''
		if borrower_name is not None and borrower_name != '':
			names = borrower_name.rsplit(" ", 1)
			if (len(names) > 1):
				book_loans = book_loans.filter(borrower__first_name__icontains = names[0])
				book_loans = book_loans.filter(borrower__last_name__icontains = names[1])
			else :
				book_loans = book_loans.filter(Q(borrower__first_name__icontains = names[0]) | Q(borrower__last_name__icontains = names[0]))
		else:
			borrower_name = ''
		book_loans = book_loans[(page_num * 10):(page_num * 10)+11]
		nxt_params = "?book="+book_id+"&borrower_id="+borrower_id+"&borrower_name="+borrower_name+("&page=%d") % (page_num + 1)
		back_params = "?book="+book_id+"&borrower_id="+borrower_id+"&borrower_name="+borrower_name+("&page=%d") % (page_num - 1)
	context = {'book_loans' : book_loans, 'book_id' : book_id, 'borrower_id' : borrower_id, 'borrower_name' : borrower_name, 'nxt_params' : nxt_params, 'back_params' : back_params, 'page_num':page_num}
	return render(request, 'bookLoans/check_in.html', context)

def bookCheckIn(request):
	if request.method != 'POST' or 'loan_id' not in request.POST:
		return HttpResponseNotFound('Invalid Request')
	try:
		book_loan = BookLoan.objects.get(loan_id = request.POST['loan_id'])
		if book_loan.date_in is None:
			book_loan.date_in = datetime.date.today()
			book_loan.full_clean()
			book_loan.save()
			messages.success(request, 'The book has been checked in successfully.')
		else:
			messages.error(request, 'This book has already been checked in.')
	except ValidationError as e:
		for key, errors in e.message_dict.items():
			for error in errors:
				messages.error(request, errors)
	except:
		messages.error(request, 'Book Loan not found. Please check again.')
	return redirect('bookLoans:checkIn')

def fines(request):
	page_num = int(request.GET['page']) if 'page' in request.GET and request.GET['page'].isdigit() else 0
	borrower_id = request.GET['borrower'] if 'borrower' in request.GET else ''
	select_string = "borrowers.first_name, borrowers.last_name, borrowers.borrower_id, SUM(fines.fine_amt) AS total_fine"
	from_string = "fines INNER JOIN book_loans ON fines.loan_id = book_loans.loan_id INNER JOIN borrowers ON borrowers.borrower_id = book_loans.card_id"
	where_string = "TRUE"
	group_by_string = "borrowers.borrower_id"
	order_by_string = "total_fine DESC"
	limit_string = "11"
	offset_string = "%s" % (page_num * 10)
	should_filter = 'filter' in request.GET and request.GET['filter'].isdigit() and int(request.GET['filter']) > 0
	sql_params = {}
	if should_filter:
		where_string += " AND fines.paid = FALSE"
	if borrower_id != '':
		where_string += " AND borrowers.borrower_id = %(borrower_id)s"
		sql_params['borrower_id'] = borrower_id
	sql = "SELECT " + select_string + " FROM " + from_string + " WHERE " + where_string + " GROUP BY " + group_by_string + " ORDER BY " + order_by_string + " LIMIT " + limit_string + " OFFSET " + offset_string
	borrowers = Borrower.objects.raw(sql, sql_params)
	borrowers = list(borrowers)
	context = {'borrowers' : borrowers, 'page_num' : page_num, 'should_filter' : should_filter, 'borrower_id' : borrower_id}
	return render(request, 'bookLoans/fines.html', context)

def finesUpdate(request):
	if (request.is_ajax) :
		loan_ids = []
		with connection.cursor() as cursor:
			update_1 = "UPDATE fines SET fine_amt = (DATE_PART('day', age(book_loans.date_in, book_loans.due_date)) * 0.25) FROM book_loans WHERE fines.loan_id = book_loans.loan_id AND book_loans.date_in IS NOT NULL AND fines.paid = FALSE AND book_loans.date_in > book_loans.due_date"
			cursor.execute(update_1)
			update_2 = "UPDATE fines SET fine_amt = (DATE_PART('day', age(current_date, book_loans.due_date)) * 0.25) FROM book_loans WHERE fines.loan_id = book_loans.loan_id AND book_loans.date_in IS NULL AND fines.paid = FALSE AND current_date > book_loans.due_date"
			cursor.execute(update_2)
			sql = "SELECT book_loans.loan_id, book_loans.due_date, book_loans.date_in FROM book_loans LEFT JOIN fines ON book_loans.loan_id = fines.loan_id WHERE fines.loan_id IS NULL AND current_date > book_loans.due_date AND (book_loans.date_in IS NULL OR book_loans.date_in > book_loans.due_date)"
			cursor.execute(sql)
			loan_ids = cursor.fetchall()

		current_date = datetime.date.today()
		for loan_id in loan_ids:
			fine = Fine()
			fine.loan_id = loan_id[0]
			due_date = loan_id[1]
			date_in = loan_id[2]
			fine.paid = False
			if date_in is None:
				fine.fine_amt = (current_date - due_date).days * 0.25
			else:
				fine.fine_amt = (date_in - due_date).days * 0.25
			try:
				fine.full_clean()
				fine.save()
			except Exception as e:
				pass
		messages.success(request, 'Fines are refreshed successfully!')
		data = {'status' : 'SUCCESS'}
		return JsonResponse(data)
	else:
		return HttpResponseNotFound("You are not allowed to request this url.")

def payFine(request):
	if request.method != 'POST' or 'card_id' not in request.POST or not request.POST['card_id'].isdigit():
		return HttpResponseNotFound('Invalid Request')
	try:
		fines = Fine.objects.all().filter(loan__borrower_id = int(request.POST['card_id'])).filter(paid=False).filter(loan__date_in__isnull = False)
		results = fines.aggregate(tot_fine = Sum('fine_amt'), num_fine = Count('loan_id'))
		fines.update(paid=True)
		if(results['num_fine'] > 0):
			messages.success(request, 'Payment of $%s has been recorded on the card number %s for total of %s fines.' % (results['tot_fine'], request.POST['card_id'], results['num_fine']))
		else:
			messages.error(request, "No valid payments to record")
	except:
		messages.error(request, 'Invalid card id provided!')
	return redirect('bookLoans:fines')