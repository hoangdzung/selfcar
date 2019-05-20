from shapely.geometry import LineString, Polygon

l = LineString([[0.5,0.5],[0.5,0.5]])
p = Polygon([[1.2,0.0],[2.2,1.0],[2.8,0.5]])
print(l.intersection(p))
#LINESTRING Z (1.7 0.5 0.25, 2.8 0.5 1)

l = LineString([[1,0.5],[3,0.5]])
p = Polygon([[1.2,0.0],[2.2,1.0],[2.8,0.5]])
print(l.intersection(p))