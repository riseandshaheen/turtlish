# conical circles
# an example to run on the turtlish app
t = Turtlish()
for i in range(40):
    t.circle(100-i*2, 360)
    t.rt(90)
    t.penup()
    t.fd(3)
    t.pendown()
    t.lt(90)