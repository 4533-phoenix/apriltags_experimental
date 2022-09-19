import ast
import bpy

bpy.ops.object.select_all(action='DESELECT')
bpy.data.objects['Cube'].select_set(True)
bpy.ops.object.delete()

points = []

with open('path.txt', 'r') as f:
    points = ast.literal_eval(f.read())

for point in points:
    bpy.ops.mesh.primitive_cube_add(location=point, size=0.01)