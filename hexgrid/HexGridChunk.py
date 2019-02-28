from hexmap.HexCell import *

# each hex grid chunk is a 5x5 block of cells

chunkSizeX = 5
chunkSizeY = 5


class HexGridChunk():
	def __init__(self):
		self.cells = [None] * 5 * 5
		self.trackedObjects = []

	def addCell(self, index, cell):
		self.cells[index] = cell
		cell.chunk = self

	def addTrackedObject(self, object):
		self.trackedObjects.append[object]
