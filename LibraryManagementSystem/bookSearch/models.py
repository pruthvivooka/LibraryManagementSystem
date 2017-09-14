from __future__ import unicode_literals

from django.db import models

# Create your models here.

class Book(models.Model):
	isbn = models.CharField(primary_key=True, max_length=10, db_column="isbn")
	title = models.CharField(max_length=250, db_column="title", null = True)
	cover_link = models.CharField(max_length=100, db_column="cover_link", null = True)
	pages = models.IntegerField(db_column="pages", null = True)

	def save(self, *args, **kwargs):
		if(len(self.isbn) == 10):
			super(Book, self).save(*args, **kwargs)
		else:
			raise Exception, "ISBN should be 10 characters" 

	class Meta:
		db_table = "book"

class Author(models.Model):
	author_id = models.AutoField(primary_key=True, db_column="author_id")
	name = models.CharField(max_length=100, db_column="name")

	class Meta:
		db_table = "authors"

class BookAuthor(models.Model):
	id = models.AutoField(primary_key=True, db_column="id")
	author = models.ForeignKey("Author", on_delete = models.CASCADE, db_column="author_id", related_name = "books")
	book = models.ForeignKey("Book", on_delete = models.CASCADE, db_column="isbn", related_name = "authors")

	class Meta:
		db_table = "book_authors"
		unique_together = ('book', 'author')

class Publisher(models.Model):
	publisher_id = models.AutoField(primary_key=True, db_column="publisher_id")
	name = models.CharField(max_length=100, db_column="name")

	class Meta:
		db_table = "publishers"

class BookPublisher(models.Model):
	id = models.AutoField(primary_key=True, db_column="id")
	publisher = models.ForeignKey("Publisher", on_delete = models.CASCADE, db_column="publisher_id", related_name = "books")
	book = models.ForeignKey("Book", on_delete = models.CASCADE, db_column="isbn", related_name = "publishers")

	class Meta:
		db_table = "book_publishers"
		unique_together = ('book', 'publisher')