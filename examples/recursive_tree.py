# recursive tree
# an example to run on the turtlish app
t = Turtlish()
t.penup()
t.goto(0, -50)
t.pendown()
t.left(90)
def tree(i):
    if i < 10:
        return
    else:
        t.forward(i)    
        t.left(30)    
        tree(3*i/4)    
        t.right(60)    
        tree(3*i/4)    
        t.left(30)    
        t.backward(i)
tree(50)