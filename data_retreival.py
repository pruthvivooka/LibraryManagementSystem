import csv
from HTMLParser import HTMLParser
import io

books = []
authors = {}
book_authors = []
author_id = 1
publishers = {}
book_publishers = []
publisher_id = 1
h = HTMLParser()
with open('books.csv', 'rb') as csvfile:
	#dialect = csv.Sniffer().sniff(csvfile.read())
	#csvfile.seek(0)
	#reader = csv.reader(csvfile, dialect)
	reader = csv.reader(csvfile, delimiter='\t')
	first_line = True
	for row in reader:
		if(first_line):
			first_line = False
			continue
		books.append([row[0], h.unescape(row[2].decode('utf-8').strip()).encode('utf-8'), row[4], row[6]])
		auths = row[3]
		current_book_authors = []
		for auth in auths.split(','):
			auth = h.unescape(auth.decode('utf-8').strip())
			if auth != "":
				if auth not in authors:
					authors[auth] = author_id
					author_id += 1
				if auth not in current_book_authors:
					current_book_authors.append(auth)
					book_authors.append([authors[auth], row[0]])
		pubs = row[5]
		current_book_publisher = []
		for pub in pubs.split(','):
			pub = h.unescape(pub.decode('utf-8').strip())
			if pub != "":
				if pub not in publishers:
					publishers[pub] = publisher_id
					publisher_id += 1
				if pub not in current_book_publisher:
					current_book_publisher.append(pub)
					book_publishers.append([publishers[pub], row[0]])
auth_list = []
for key, value in authors.iteritems():
	auth_list.append([key.encode('utf-8'), value])
pub_list = []
for key, value in publishers.iteritems():
	pub_list.append([key.encode('utf-8'), value])
with io.open('normalized_data/book.csv', 'wb') as csvfile:
	wr = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
	for book in books:
		wr.writerow(book)
with io.open('normalized_data/author.csv', 'wb') as csvfile:
	wr = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
	for auth in auth_list:
		wr.writerow(auth)
with io.open('normalized_data/book_author.csv', 'wb') as csvfile:
	wr = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
	for book_author in book_authors:
		wr.writerow(book_author)
with io.open('normalized_data/publisher.csv', 'wb') as csvfile:
	wr = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
	for publ in pub_list:
		wr.writerow(publ)
with io.open('normalized_data/book_publisher.csv', 'wb') as csvfile:
	wr = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
	for book_publisher in book_publishers:
		wr.writerow(book_publisher)