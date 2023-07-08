import math

def calculate_angle(x1, y1, x2, y2, x3, y3):
    slope1 = math.atan2(y2 - y1, x2 - x1)
    slope2 = math.atan2(y3 - y2, x3 - x2)
    angle = math.degrees(slope2 - slope1)
    return angle

# Example call to the function
x1 = 1
y1 = 1
x2 = 2
y2 = 2
x3 = 2
y3 = 0

angle = calculate_angle(x1, y1, x2, y2, x3, y3)
print("Angle in degrees:", angle)

if (angle <= 30 and angle >= -30):
    print("Straight")
elif angle <= -45 and angle >= -90:
    print("Slight right")
elif angle <= -90 and angle > -135:
    print("Right")
elif angle <= -135:
    print("Sharp right")
elif angle >= 45 and angle <= 90:
    print("Slight left")
elif angle >= 90 and angle < 135:
    print("Left")
elif angle >= 135:
    print("Sharp left")