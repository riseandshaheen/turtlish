# Code Art with Turtlish [WIP]

This application lets you code in turtle-like environment that runs inside the Cartesi machine. As a user, you can submit code that contains turtle-like commands to generate a base64 image string.

## Build and run
Make sure you have cartesi-cli installed before you proceed ahead. Inside the root of the project directory, open terminal and hit:
```
cartesi build
```

To run the node:
```
cartesi run
```

## Send inputs
Open another terminal and try sending variety of inputs to test the backend logic.
```
cartesi send generic
```
Backend accepts inputs in a JSON format as shown below
```
{"method":"draw", "code":"<input turtle commands>"}
```

Example JSON input string:
```
{"method":"draw", "code": "for i in range(50): \n\tturtle.circle(100,360) \n\tturtle.left(5)"}
```

## Available commands
- Simple Movement - `forward(value)` `backward(value)`  `right(degrees)`  `left(degrees)`  `penup`  `pendown`  `goto`  `home`  `setheading` 
- Advance Movement -
 `goto(x-value, y-value)` `setx(value)` `sety(value)`

- Shapes - `circle(radius, degrees)`

- Drawing - `begin_fill`  `end_fill`  

- Pen - `pensize(value)`

## Samples
![sample01](./sample01.png)
![sample02](./sample02.png)