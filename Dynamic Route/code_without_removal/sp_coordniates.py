import networkx as nx
import math

def get_lat_lon(G, SP):
    SP_lat_lon = []
    for i in SP:
        SP_lat_lon.append((G.nodes[i]['y'], G.nodes[i]['x'])) # y = lat, x = long
    return SP_lat_lon

def get_dist_list(G, SP):
    SP_dist = []
    for i in range(0, len(SP) - 2):
        edge_data = G.get_edge_data(SP[i], SP[i + 1])
        length = edge_data[0]['length']
        SP_dist.append(length)
    return SP_dist

def calculate_angle(x1, y1, x2, y2, x3, y3):
    # Calculation of the slope angles of the two lines
    SLOPE1 = math.atan2(y2 - y1, x2 - x1)
    SLOPE2 = math.atan2(y3 - y2, x3 - x2)

    # Calculation of the angles between the two lines
    ANGLE = math.degrees(SLOPE2 - SLOPE1)

    # Adjust the ANGLE to the range of -180° to 180°
    if ANGLE > 180:
        ANGLE -= 360
    elif ANGLE < -180:
        ANGLE += 360

    return ANGLE

def angle_checker(SP):
    DIRECTION_LIST = []
    if len(SP) == 2:
        #print("Straight")
        DIRECTION_LIST.append("Straight")
        return
    for i in range(0, len(SP) - 4):
        ANGLE = calculate_angle(SP[i][0], SP[i][1], SP[i + 1][0], SP[i + 1][1], SP[i + 2][0], SP[i + 2][1])
        #print("ANGLE in degrees:", ANGLE, SP[i][0], SP[i][1], SP[i + 1][0], SP[i + 1][1], SP[i + 2][0], SP[i + 2][1])
        if (ANGLE <= 45 and ANGLE >= -45):
            DIRECTION_LIST.append("Straight")

        elif ANGLE < -45 and ANGLE >= -75:
            DIRECTION_LIST.append("Slight left")

        elif ANGLE < -75 and ANGLE >= -105:
            DIRECTION_LIST.append("Left")

        elif ANGLE < -105 and ANGLE >= -135:
            DIRECTION_LIST.append("Sharp left")

        elif ANGLE >= 45 and ANGLE <= 75:
            DIRECTION_LIST.append("Slight right")

        elif ANGLE > 75 and ANGLE <= 105:
            DIRECTION_LIST.append("Right")

        elif ANGLE < 105 and ANGLE >= 135:
            DIRECTION_LIST.append("Sharp right")

        elif ANGLE < -135 or ANGLE > 135:
            DIRECTION_LIST.append("U-Turn")

    return DIRECTION_LIST

def dist_and_turn(ANGLE_LIST, DIST_LIST):
    directions = []
    for i in range(0, len(ANGLE_LIST) - 1):
        directions.append((DIST_LIST[i], ANGLE_LIST[i]))
    directions.append((DIST_LIST[-1], 'Straight_To_Destination'))
    return directions