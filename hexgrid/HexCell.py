from hexmap.HexCoordinate import *
from KBEDebug import *
import GameConfigs


class HexCellState():
	IDLE, MARK_FOR_DESTROY, IN_PROCESS_DESTROY, DESTROYED = range(4)


class HexDirection():
		NE, E, SE, SW, W, NW = range(6)
		East = HexCoordinate(1, 0)
		NorthEast = HexCoordinate(0, 1)
		NorthWest = HexCoordinate(-1, 1)
		West = HexCoordinate(-1, 0)
		SouthWest = HexCoordinate(0, -1)
		SouthEast = HexCoordinate(1, -1)

		directions = [East, NorthEast, NorthWest, West, SouthWest, SouthEast]

		def __init__(self, direction):
			self.direction = direction

		def opposite(self):
			return self.direction + 3 if self.direction < 3 else self.direction - 3

		def previous(self):
			return NW if self.direction == NE else self.direction - 1

		def next(self):
			return NE if self.direction == NW else self.direction + 1


class HexCell():
	destructionDelay = 0.5

	def __init__(self, position, index):
		self.position = position
		self.state = HexCellState.IDLE
		self.neighbours = {}
		# trackedObjects are entities placed into world after the game starts. Chests, components etc
		self.trackedObjects = []
		self.index = index
		self.grid = None
		self.coordinates = None
		self.map = None
		self.indestructible = False

	def setNeighbor(self, direction, neighbor):
		self.neighbours[direction] = neighbor

	def setTrackedObject(self, object):
		# cells[object.home_cell_id].removeTrackedObect(object)
		self.trackedObjects.append(object)

	def removeTrackedObject(self, object):
		# if self.trackedObjects[object.id]:
		if object in self.trackedObjects:
			self.trackedObjects.remove(object)

	# delay here first, so that client shrinks don't all start at the same time
	def startShrink(self, shrinkDelay, shrinkWarning):
		if not self.map:
			return

		self.state = HexCellState.MARK_FOR_DESTROY
		self.shrinkDelay = shrinkDelay
		self.shrinkWarning = shrinkWarning
		self.map.owner.registTimer(self.markForDestroy, self.shrinkDelay, 0, 1)

	def markForDestroy(self, _deltaTime):
		# self.map.cellsMarkedForDestroy.append(self)
		self.state = HexCellState.IN_PROCESS_DESTROY
		self.map.owner.registTimer(self.removeCell, self.shrinkWarning, 0, 1)

	def removeCell(self, _deltaTime):
		for obj in self.trackedObjects:
			if not obj.isDestroyed:
				if hasattr(obj, "safeDestroy"):
					obj.safeDestroy()
				else:
					obj.destroy()

		# trackedDestructibles are collider IDs on top of the cell
		trackedDestructibles = self.map.owner.hexOverlap(self.position, 1 << GameConfigs.PhysxMatrix.Environment)
		if trackedDestructibles:
			for id in trackedDestructibles:
				self.map.owner.removeActor(id)

		del self.trackedObjects[:]

		self.state = HexCellState.DESTROYED

	def setIndestructible(self, isIndestructible):
		self.indestructible = True
