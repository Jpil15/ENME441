import math
from RPi import GPIO
from shifter import Shifter
import time



class Turrets: 
    def __init__(self, ident, rval, theta_deg): 
        self.ident = ident
        self.rval = rval
        self.theta_deg = theta_deg   # store degrees for readability
        self.theta_rad = math.radians(theta_deg)  # also store radians
        

class NewTurrets: 
    def __init__(self, ident, x, y, z):
        self.ident = ident
        self.x = x
        self.y = y
        self.z = z


ident_example = [1, 2, 3, 4, 5]
rval_example = [3, 3, 3, 3, 3]
theta_example = [75, 45, 180, 135, 270]  # degrees


# Create list of polar turrets
turrets = []

for i in range(len(ident_example)):
    turret_id = f"{i+1}"
    new_turret = Turrets(turret_id, rval_example[i], theta_example[i])
    turrets.append(new_turret)

# Print polar data
print("Polar Coordinates of Turrets")
for obj in turrets:
    print(f"id: {obj.ident}, r: {obj.rval}, theta_deg: {obj.theta_deg}")

    
# Centering our Turret at the origin.

our_Turret_id = input("Enter our turret ID: ")

for i in turrets:
    if(our_Turret_id == i.ident):
        our_theta_deg = i.theta_deg
       

rotate_deg = 270 - our_theta_deg




rotated_Turrets = []

for i in turrets:
    new_turret = Turrets(i.ident, i.rval, i.theta_deg + rotate_deg)
    rotated_Turrets.append(new_turret)

print("Polar Coordinates of Rotated Turrets")
for obj in rotated_Turrets:
    print(f"id: {obj.ident}, r: {obj.rval}, theta_deg: {obj.theta_deg}")


# Polar to Rect transformation
cartesian_turrets = []

for t in rotated_Turrets:
    # use radians for trig
    x = t.rval * math.cos(t.theta_rad) 
    y = t.rval * math.sin(t.theta_rad) + 3
    z = 0  # given

    new_turret = NewTurrets(t.ident, x, y, z)
    cartesian_turrets.append(new_turret)


 

print("Cartesian Turrets")




# Print Cartesian data
for obj in cartesian_turrets:
    print(f"id: {obj.ident}")
    print(f"  x: {round(obj.x, 3)}")
    print(f"  y: {round(obj.y,3)}")
    print(f"  z: {round(obj.z,3)}")

# Convert coordinates of each turret into angles

xyangles = []

for obj in cartesian_turrets:
    if(obj.y > 0.0):
        angle = math.degrees(math.atan(obj.x / obj.y))
        xyangles.append(angle)
        


print("raw angles to rotate to")
print(xyangles)

curr_pos = 0

holder = xyangles
holder.insert(0, curr_pos) 
print(holder)

movement = []

for x in range(len(holder)-1):
    newstep = (holder[x+1] - holder[x]) * 512/180
    movement.append(newstep)

print("degrees to move")
print(movement)

dir = []
for i in range(len(movement)):
    x = abs(movement[i]) / movement[i]
    dir.append(x)


print(dir)

#NOW WE MOVIN THE MOTOR

s = Shifter(data=17,clock=27,latch=22)   # Set up shifter

cycle = [0b0001,
         0b0011,
         0b0010,
         0b0110,
         0b0100,
         0b1100,
         0b1000,
         0b1001]

# track position within m_seq:
pos = 0

delay = 1400/1e6  # delay between steps [us]
# Make a full rotation of the output shaft:
def loop(dir, dis): # dir = rotation direction (1=cww, -1=cw)
    global pos
    for i in range(dis): # 4096 steps/rev
        pos += dir
        pos %= 8 
        s.shiftByte(cycle[pos]<<4)
        time.sleep(delay)

try:
    for i in range(len(movement)):
        loop(dir[i], movement[i])


except Exception as e:

    print(e)
