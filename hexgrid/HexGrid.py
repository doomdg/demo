import Math
import GameUtils
import hexmap.HexMetrics as HexMetrics
from hexmap.HexCell import *
from hexmap.HexGridChunk import *
from Component import Component
from KBEDebug import *

kDefaultCellDepth = -0.1


class HexGrid():
	def __init__(self, map):
		self.cellCountX = map.grid_count
		self.cellCountZ = map.grid_count
		self.cells = []
		self.chunks = []
		self.chunkCountX = int(self.cellCountX / HexMetrics.chunkSizeX)
		self.chunkCountZ = int(self.cellCountZ / HexMetrics.chunkSizeZ)
		self.map = map
		self.createChunks()
		self.createCells()

	def createCells(self):
		self.cells = [None] * self.cellCountX * self.cellCountZ
		i = 0
		for z in range(self.cellCountZ):
			for x in range(self.cellCountX):
				self.createCell(x, z, i)
				i += 1

	def createChunks(self):
		self.chunks = [None] * self.chunkCountX * self.chunkCountZ
		i = 0
		for z in range(self.chunkCountZ):
			for x in range(self.chunkCountX):
				chunk = HexGridChunk()
				self.chunks[i] = chunk
				i += 1

	def createCell(self, x, z, i):
		position = Math.Vector3(
			(x + z * 0.5 - int(z / 2.0)) * (HexMetrics.innerRadius * 2.0),
			kDefaultCellDepth, z * (HexMetrics.outerRadius * 1.5))
		cell = HexCell(position, i)
		cell.map = self.map
		cell.coordinates = HexCoordinate.FromOffsetCoordinate(x, z)
		# pass this reference so cells can create timers
		cell.grid = self
		self.cells[i] = cell
		if x > 0:
			cell.setNeighbor(HexDirection.W, self.cells[i - 1])
		if z > 0:
			if (z & 1) == 0:
				cell.setNeighbor(HexDirection.SE, self.cells[i - self.cellCountX])
				if x > 0:
					cell.setNeighbor(HexDirection.SW, self.cells[i - self.cellCountX - 1])
			else:
				cell.setNeighbor(HexDirection.SW, self.cells[i - self.cellCountX])
				if (x < self.cellCountX - 1):
					cell.setNeighbor(HexDirection.SE, self.cells[i - self.cellCountX + 1])

		self.addCellToChunk(x, z, cell)

	def getCellByPosition(self, position):
		if (position == Component.POSITION_OUTOFWORLD):
			ERROR_MSG("Attempting to access cell of OUTOFWORLD item")
			return None

		position.y = kDefaultCellDepth
		coords = HexCoordinate.FromPosition(position)
		index = coords.x + coords.z * self.cellCountX + int(coords.z / 2.0)

		if not self.cells or len(self.cells) <= index or index < 0 or self.cells[index].position.distTo(position) > 5:
			return

		return self.cells[index]
	
	def getIndexByCell(self, _cell):
		return self.cells.index(_cell)

	def getCellByIndex(self, _index):
		return self.cells[_index]

	def getDistanceBetween(self, _fromCell, _toCell):
		return _fromCell.position.distTo(_toCell.position)

	def getCellByCoord(self, hexCoord):
		z = hexCoord.z
		if z < 0 or z >= self.cellCountZ:
			return None
		x = hexCoord.x + int(z / 2)
		if x < 0 or x >= self.cellCountX:
			return None

		return self.cells[x + z * self.cellCountX]

	def addCellToChunk(self, x, z, cell):
		chunkX = int(x / HexMetrics.chunkSizeX)
		chunkZ = int(z / HexMetrics.chunkSizeZ)

		chunk = self.chunks[chunkX + chunkZ * self.chunkCountX]
		localX = x - chunkX * HexMetrics.chunkSizeX
		localZ = z - chunkZ * HexMetrics.chunkSizeZ
		chunk.addCell(localX + localZ * HexMetrics.chunkSizeX, cell)

	def updateTrackedObject(self, object):
		oldHomeCell = self.cells[object.homeCellId]
		oldHomeCell.removeTrackedObject(object)
		newHomeCell = self.getCellByPosition(object.position)
		if not newHomeCell:
			DEBUG_MSG("No Cell found for object")
			return None

		newHomeCell.setTrackedObject(object)

	def getCellsInRange(self, start, cellRange):
		return None

	# this function returns all cells. Even those that are collapsing or is destroyed
	# please parse cells states after getting the result
	def getCellRingInRange(self, start, cellRange):
		cellRange = int(cellRange)
		cellsInRing = []
		startCell = self.getCellByPosition(start)
		if startCell is None:
			return None
		startPoint = startCell.coordinates.Add(HexDirection.SouthWest.Multiply(cellRange))
		for direction in HexDirection.directions:
			for i in range(cellRange):
				cellToAdd = self.getCellByCoord(startPoint)
				if cellToAdd is not None:
					cellsInRing.append(cellToAdd)

				startPoint = startPoint.Add(direction)

		return cellsInRing

	def getCellsToCollapse(self, start, cellRange):
		cellRange = int(cellRange)
		cellsInRing = []
		
		startCell = self.getCellByPosition(start)
		if startCell is None:
			ERROR_MSG("START CELL")
			return None

		startPoint = startCell.coordinates.Add(HexDirection.SouthWest.Multiply(cellRange))
		for direction in HexDirection.directions:
			for i in range(cellRange):
				cellToAdd = self.getCellByCoord(startPoint)
				if cellToAdd is not None and cellToAdd.state == HexCellState.IDLE:
					cellsInRing.append(cellToAdd)

				startPoint = startPoint.Add(direction)

		return cellsInRing
