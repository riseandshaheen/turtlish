# random walk
# an example to run on the turtlish app
t = Turtlish()
import random
random.seed(2)
distance = [20, 30, 40, 50]
angles = [90, 180, 270, 360]
for i in range(80):
    t.fd(random.choice(distance))
    t.left(random.choice(angles))