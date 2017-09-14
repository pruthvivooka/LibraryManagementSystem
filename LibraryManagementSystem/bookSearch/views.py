from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, HttpResponseNotFound
from .models import Book, Author, BookAuthor
from django.db.models import Q, Prefetch

def home(request):
	context = {}
	return render(request, 'bookSearch/home.html', context)

def index(request):
	context = {}
	return render(request, 'bookSearch/index.html', context)

def search(request):
	book_author = BookAuthor.objects.select_related('book', 'author').all().distinct('book').order_by('book__isbn').prefetch_related('book', 'book__authors__author', 'book__loaners')
	isbn = "" if 'isbn' not in request.GET else request.GET['isbn']
	title = "" if 'btitle' not in request.GET else request.GET['btitle']
	authors = "" if 'authors' not in request.GET else request.GET['authors']
	page_num = int(request.GET['page']) if 'page' in request.GET and request.GET['page'].isdigit() else 0
	if isbn != '':
		book_author = book_author.filter(book__isbn__iexact = isbn)
	if title != '':
		book_author = book_author.filter(book__title__icontains = title)
	if authors != '':
		q_object_filter = None
		for x in authors.split(","):
			if(x.strip() != ""):
				q_object_filter = Q(author__name__icontains = x.strip()) if q_object_filter is None else q_object_filter | Q(author__name__icontains = x.strip())
		if q_object_filter != None:
			book_author = book_author.filter(q_object_filter)
	book_author = book_author[(page_num * 10):(page_num * 10)+11]
	nxt_params = "?isbn="+isbn+"&btitle="+title+"&authors="+authors+("&page=%d") % (page_num + 1)
	back_params = "?isbn="+isbn+"&btitle="+title+"&authors="+authors+("&page=%d") % (page_num - 1)
	book_authors = []
	for b_a in book_author:
		ba = {}
		ba['isbn'] = b_a.book.isbn
		ba['title'] = b_a.book.title
		ba['authors'] = ",".join(b_a.book.authors.all().values_list('author__name', flat = True))
		ba['available'] = not (b_a.book.loaners.filter(book__loaners__date_in__isnull = True).filter(book__loaners__loan_id__isnull = False).exists())
		book_authors.append(ba)
	context = {'book_authors' : book_authors, 'nxt_params' : nxt_params, 'back_params' : back_params, 'page_num' : page_num, 'authors' : authors, 'title' : title, 'isbn' : isbn}
	return render(request, 'bookSearch/search.html', context)