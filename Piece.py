#Class that represents piece objects for the clobber game
from Piece import *

class Piece:

	#Constructor for piece objects
	def __init__(self, row, column):
		self.row = row
		self.column = column
		self.stranded = False

	#Returns the piece row
	def get_row(self):
		return self.row

	#Returns the piece column
	def get_col(self):
		return self.col

	#Tests for Piece equality
	def equals(self, other):
		if (self.row != other.row):
			return False
		if (self.column != other.column):
			return False
		return True

	#Display functon for the piece
	def display(self):
		print("(" + str(self.row) + "," + str(self.column) + ")" )
