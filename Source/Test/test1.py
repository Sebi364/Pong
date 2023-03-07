# define vectors
vec1_start = (-10, 0)  # starting point of vector 1
vec1_end = (10, 0)  # ending point of vector 1
vec2_start = (5, -10)  # starting point of vector 2
vec2_end = (5, 10)  # ending point of vector 2

# calculate direction vectors of both vectors
vec1_dir = (vec1_end[0] - vec1_start[0], vec1_end[1] - vec1_start[1])
vec2_dir = (vec2_end[0] - vec2_start[0], vec2_end[1] - vec2_start[1])

# calculate the denominator of the equation to find x-coordinate
denom = vec1_dir[0] * vec2_dir[1] - vec1_dir[1] * vec2_dir[0]

# check if the two vectors are parallel or collinear
if denom == 0:
    print("The two vectors are parallel or collinear.")
else:
    # calculate the x-coordinate of the crossing point
    t = ((vec2_start[0] - vec1_start[0]) * vec2_dir[1] - (vec2_start[1] - vec1_start[1]) * vec2_dir[0]) / denom
    x = vec1_start[0] + t * vec1_dir[0]
    y = vec1_start[1] + t * vec1_dir[1]
    print(f"The crossing point is ({x}, {y}).")
