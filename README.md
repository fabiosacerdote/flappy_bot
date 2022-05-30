# Flappy Bot
## [FULL BLOG ARTICLE](https://fabiosacerdote.com/en/3.html)

The goal of the project is to create an algorithm in Python able to autonomously learn how to play Flappy Bird using a simple kind of neuroevolution and a Greedy Algorithm.

![The project](https://fabiosacerdote.com/content/projects/Flappy%20Bot/1.PNG)



## The Game
In order to create the user interface, I use the module tkinter, that makes it quite manageable to handle graphical elements.

The tubes are generated on the right side of the window at a random height, and they approach the square/bird at a fixed speed. The square starts its match at mid-height and is always subject to gravity. It dies when it collides with the tubes or when it falls to the ground, but not when it reaches the upper bound of the window, as like in the original game.

The game is completely contained in the class Game.

## Learning to play
Once the game is ready, the algorithm has to learn to play with it. It will have access to two numbers: the horizontal distance from the tubes and the vertical distance from the top of the lower one. Using this information, the algorithm will have to decide whether to flap its wings or not. These two inputs will be interpreted by neural networks with two inputs and two outputs. 

The algorithm I've written is a kind of greedy algorithm applied to the weights and biases of the considered neural network. The programm will start from a neural network initialised at random, it will use it to play a fixed number of games and give it as a score the average time it survived in those games. After having tested the first neural network, the programm will create a slightly mutated copy and test it in the same way as the first. If the score improves, the new network will take the place of the first one and will be used to create new networks, otherwise another mutation of the original network will be tested.

## Mutation and selection
The neural networks are handled by a NeuralNetwork class that not only handles layers, neurons and computations, but also contains some specific methods that are useful both for greedy and genetic algorithms.

## Results
Completing this project has taken, in total, almost two years. I have changed the approach several times, I have interrupted it even more times, it took a while to spot some bugs... But I can finally be satisfied. The algorithm is able to drastically and rapidly improve its score and to find ways to survive forever.


![Some scores](https://fabiosacerdote.com/content/projects/Flappy%20Bot/4.png)
