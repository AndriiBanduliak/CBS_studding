import math

def sphere_volume(radius):
    return 4/3 * math.pi * radius ** 3

def parallelepiped_volume(length, width, height):
    return length * width * height

def square_pyramid_volume(base_side, height):
    base_area = base_side ** 2
    return 1/3 * base_area * height

def cone_volume(radius, height):
    return 1/3 * math.pi * (radius ** 2) * height

def cylinder_volume(radius, height):
    return math.pi * radius ** 2 * height