import math
import hexmap.HexMetrics as HexMetrics


class HexCoordinate():

	@staticmethod
	def FromOffsetCoordinate(x, z):
		return HexCoordinate(x - int(z / 2), z)

	@staticmethod
	def FromPosition(position):
		x = position.x / (HexMetrics.innerRadius * 2.0)
		y = x * -1.0
		offset = position.z / (HexMetrics.outerRadius * 3.0)
		x -= offset
		y -= offset

		iX = round(x)
		iY = round(y)
		iZ = round(-x - y)
		if (iX + iY + iZ) != 0:
			dX = math.fabs(x - iX)
			dY = math.fabs(y - iY)
			dZ = math.fabs(-x - y - iZ)

			if dX > dY and dX > dZ:
				iX = -iY - iZ
			elif dZ > dY:
				iZ = -iX - iY

		return HexCoordinate(iX, iZ)

	def __init__(self, x, z):
		self.x = x
		self.z = z

	def getX(self):
		return self.x

	def getZ(self):
		return self.z

	def getY(self):
		return - self.x - self.z

	def DistanceTo(self, target):
		return (target.x - self.x if self.x < target.x else self.x - target.x) +\
			(target.getY() - self.getY() if self.getY() < target.getY() else self.getY() - target.getY()) +\
			(target.z - self.z if self.z < target.z else self.z - target.z) / 2

	def Add(self, target):
		return HexCoordinate(self.x + target.x, self.z + target.z)

	def Multiply(self, scalarValue):
		return HexCoordinate(self.x * scalarValue, self.z * scalarValue)

	def Subtract(self, target):
		return HexCoordinate(self.x - target.x, self.z - target.z)
