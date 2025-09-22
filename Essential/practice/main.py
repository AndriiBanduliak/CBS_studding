import area_calculator
import volume_calculator

print("______Demo________\n")

#triangele
baase = 5
height = 10
triangle_area = area_calculator.triangle_area(baase, height)
print(f"Triangle area: {triangle_area}")

#rectangle
length = 4 
width = 6
rectangle_area = area_calculator.rectangle_area(length, width)
print(f"Rectangle area: {rectangle_area}")

#circle
radius = 3
circle_area = area_calculator.circle_area(radius)
print(f"Circle area: {circle_area}")


print("\n" + "="*30 + "\n")
print("______Volume________\n")

#sphere
radius = 3
sphere_volume = volume_calculator.sphere_volume(radius)
print(f"Sphere volume: {sphere_volume}")

#parallelepiped
length = 4
width = 5
height = 6
parallelepiped_volume = volume_calculator.parallelepiped_volume(length, width, height)
print(f"Parallelepiped volume: {parallelepiped_volume}")

#square pyramid
base_side = 4
height = 6
square_pyramid_volume = volume_calculator.square_pyramid_volume(base_side, height)
print(f"Square pyramid volume: {square_pyramid_volume}")

#cone
radius = 3
height = 5
cone_volume = volume_calculator.cone_volume(radius, height)
print(f"Cone volume: {cone_volume}")

#cylinder
radius = 3
height = 5
cylinder_volume = volume_calculator.cylinder_volume(radius, height)
print(f"Cylinder volume: {cylinder_volume}")

print("\n" + "=" *30 + "\n")
