from __future__ import unicode_literals
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from django.db import models

# Create your models here.

class BookLoan(models.Model):
	loan_id = models.AutoField(primary_key=True, db_column="loan_id")
	book = models.ForeignKey('bookSearch.Book', on_delete = models.CASCADE, db_column="isbn", related_name = "loaners")
	borrower = models.ForeignKey('borrowers.Borrower', on_delete = models.CASCADE, db_column="card_id", related_name = "loans")
	date_out = models.DateField(db_column="date_out")
	due_date = models.DateField(db_column="due_date")
	date_in = models.DateField(db_column="date_in", null = True, blank = True)

	def clean(self, *args, **kwargs):
		if (self.due_date < self.date_out):
			raise ValidationError({'due_date': _("Due date must be date greater than Check Out date.")})
		if (self.date_in is not None and self.date_in < self.date_out):
			raise ValidationError({'date_in': _("Check in cannot happen before check out.")})
		else :
			if (self.date_in is None and BookLoan.objects.all().filter(book__exact = self.book_id).filter(date_in__isnull = True).exists()):
				raise ValidationError({'book': _("This book has been already checked out.")})
		if (self.date_in is None and self.borrower_id is not None and self.borrower_id != ""):
			if (BookLoan.objects.all().filter(borrower__exact = self.borrower_id).filter(date_in__isnull = True).count() > 2):
				raise ValidationError({'borrower': _("This borrower already has 3 books loaned.")})
		super(BookLoan, self).clean(*args, **kwargs)

	class Meta:
		db_table = "book_loans"

class Fine(models.Model):
	loan = models.OneToOneField("BookLoan", primary_key=True, on_delete = models.CASCADE, db_column="loan_id", related_name = "fines")
	fine_amt = models.DecimalField(db_column="fine_amt", max_digits=6, decimal_places = 2)
	paid = models.BooleanField(db_column="paid", default=False)

	class Meta:
		db_table = "fines"