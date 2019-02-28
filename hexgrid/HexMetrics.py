import Math

outerToInner = 0.866025404
innerToOuter = 1 / outerToInner
outerRadius = 5
innerRadius = outerRadius * outerToInner
chunkSizeX = 5
chunkSizeZ = 5

corners = {
	Math.Vector3(0, 0, outerRadius),
	Math.Vector3(innerRadius, 0, outerRadius * 0.5),
	Math.Vector3(innerRadius, 0, outerRadius * -0.5),
	Math.Vector3(0, 0, -outerRadius),
	Math.Vector3(-innerRadius, 0, outerRadius * -0.5),
	Math.Vector3(-innerRadius, 0, outerRadius * 0.5),
	Math.Vector3(0, 0, outerRadius)}
