class Book:
	def bookdata(self,title,price,author):
		self.title = title
		self.price = price
		self.author = author
	
	def printData(self):
		print("price : %s" %self.price)
		print("title : %s" %self.title)
		print("author : %s" %self.author)
	
	def __init__(self):
		print("new book object")
