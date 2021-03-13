from tkinter import *
from numpy import exp, array, dot
import numpy.random
import time

#random.seed(30)
tk = Tk()


class Neuron():
    def __init__(self):
        self.v = 0

    def set_value(self, new_value):
        self.v = new_value


class Layer():
    def __init__(self, size, previous_neurons_num, seed):
        self.dimensioni = size
        self.previous_neurons = previous_neurons_num
        self.w_num = self.dimensioni*previous_neurons_num
        #self.weights = [[0] * previous_neurons_num] * self.dimensioni
        self.neurons = [None] * size
        self.rand = numpy.random
        self.weights = self.rand.rand(self.dimensioni, previous_neurons_num) * 2 -1

        for x in range(0, size):
            self.neurons[x] = Neuron()
        

    def printa(self):
        print ("[")
        for x in range(0, self.dimensioni):
            #print self.neurons[x].v

            for w in range(0, self.previous_neurons):
                print (self.weights[x][w])
            print ("]")

        print ("]")
    
    def save(self):
        to_print = "["
        for x in range(0, self.dimensioni):

            for w in range(0, self.previous_neurons):
                to_print += str(self.weights[x][w]) + " "

        to_print += "]"
        print(to_print)

class NeuralNetwork():
    def __init__(self, seed, layers=None):
        if layers is None or len(layers) < 2:
            layers = [3,5,5,5,2]

        self.n_layers = len(layers)
        self.layers_sizes = layers

        self.n_inputs = self.layers_sizes[0]
        self.input = [0] * self.n_inputs
        self.n_outputs = self.layers_sizes[len(layers)-1]
        self.output = [0] * self.n_outputs


        self.layer = [None] * self.n_layers
        self.layer[0] = Layer(self.layers_sizes[0], 0, seed+1)

        for l in range(1, self.n_layers):
            self.layer[l] = Layer(self.layers_sizes[l], self.layers_sizes[l-1], seed+l+1)


        self.rand = numpy.random
        self.rand.seed = seed
        

		#trains
		#-set
		#--input
		#--output


    def printa(self):
        print ("Numero di input:", self.n_inputs)
        print ("Numero di layers:", self.n_layers)
        print ("Dimensioni dei layer:", self.layers_sizes)
        print ("Numero di output:", self.n_outputs)

    def print_network(self):
        for l in range(0,self.n_layers):
            print ("Layer ", l)
            self.layer[l].printa()

    
    def save_network(self):
        for l in range(0,self.n_layers):
            self.layer[l].save()
        print("------")

    def set_input(self, values):
        self.input = values

        for x in range(0, self.n_inputs):
            self.layer[0].neurons[x].v = self.input[x]

    def sigmoid(self, x):
        return 1 / (1 + exp(-x))

    def calc_output(self):
        for l in range(1, self.n_layers):
            for n in range(0, self.layers_sizes[l]):
                tot = 0
                for m in range(0, self.layers_sizes[l-1]):
                    tot = tot + self.layer[l-1].neurons[m].v * self.layer[l].weights[n][m]

                self.layer[l].neurons[n].set_value(self.sigmoid(tot))

        for i in range(0, self.n_outputs):
            self.output[i] = self.layer[(self.n_layers)-1].neurons[i].v

        return self.output







class Game():
    def __init__(self, entities=100, network=None):
        #CREAZIONE FINESTRA
        self.width_size = 400
        self.height_size = 800
        self.w = Canvas(tk, width=self.width_size, height=self.height_size)
        self.w.pack()

        #SCRITTE
        self.scoreboard = self.w.create_text(self.width_size/2, 20, fill="grey", font="Arial", text="Flappy Bot")
        self.datas = self.w.create_text(self.width_size/2, 40, fill="grey", font="Arial", text="Score:")
        self.separatore = self.w.create_rectangle(-10, 60, self.width_size+10, 60, outline="grey")

        #TERRA E CIELO
        self.sky = self.w.create_rectangle(-10, 60, self.width_size+10, 760, fill="#4dd0e1")
        self.ground = self.w.create_rectangle(-10, 760, self.width_size+10, 800, fill="green")

        #UCCELLO
        self.bird = self.w.create_rectangle(30, 430, 60, 400, fill="red")
        self.bird_x = 30
        self.bird_y = 430
        self.bird_y0 = 430
        self.bird_speed_y = 0
        self.bird_speed_y0 = 0

        #VARIABILI PER IL GIOCO
        self.time_count=0       #Per regolare il salto
        self.time_survive=0
        self.jumping = False
        self.jump_triggered = False

        #RANDOM
        self.rand = numpy.random
        #self.rand.seed= 30
        self.generation = 1


        #OSTACOLO
        self.obs_x = self.width_size-10                 #Posizione X del bordo sinistro
        self.obs_y_up = self.rand.randint(330) + 160     #Posizione Y della fine del tubo di sopra
        self.obs_y_down = self.obs_y_up + 170           #Posizione Y della fine del tubo di sotto
        self.ostacolo_up = self.w.create_rectangle(self.obs_x, 60, self.obs_x + 40, self.obs_y_up, fill="#1b5e20")
        self.ostacolo_down = self.w.create_rectangle(self.obs_x, self.obs_y_down, self.obs_x + 40, 760, fill="#1b5e20")

        self.obs_speed = 2
        self.last_best = 0
        self.death=False


        #POPOLAZIONE
        #popolazione: 100 NN
        self.n_entities = entities

        if network is None or len(network) < 2:
            self.pop_layers = [3,2,5,2,2]
        else:
            self.pop_layers = network
        
        self.population = [None] * self.n_entities
        self.scores = [0.0] * self.n_entities

        for i in range(0, self.n_entities):
                self.population[i] = NeuralNetwork(i, self.pop_layers)

    
    def move_obstacle(self):
        if self.obs_x > 0:
            #MOVIMENTO VERSO DESTRA
            self.new_x = self.obs_x - self.obs_speed
            self.movement_x = self.new_x - self.obs_x
            self.w.move(self.ostacolo_up, self.movement_x, 0)
            self.w.move(self.ostacolo_down, self.movement_x, 0)
            self.obs_x = self.new_x
        else:
            #RIPOSIZIONAMENTO
            self.w.delete(self.ostacolo_up)
            self.w.delete(self.ostacolo_down)

            self.obs_x = self.width_size-10                 #Posizione X del bordo sinistro
            self.obs_y_up = self.rand.randint(330) + 160     #Posizione Y della fine del tubo di sopra
            self.obs_y_down = self.obs_y_up + 170           #Posizione Y della fine del tubo di sotto
            self.ostacolo_up = self.w.create_rectangle(self.obs_x, 60, self.obs_x + 40, self.obs_y_up, fill="#1b5e20")
            self.ostacolo_down = self.w.create_rectangle(self.obs_x, self.obs_y_down, self.obs_x + 40, 760, fill="#1b5e20")


    def move_bird(self):
        if self.jump_triggered == True and self.bird_speed_y < 0:
            self.bird_speed_y = 10           #cambio la velocità verticale con una positiva
            self.bird_speed_y0 = self.bird_speed_y
            self.bird_y0 = self.bird_y       #posizione verticale iniziale
            self.jump_triggered = False
        
        self.bird_speed_y -= 0.4            #considero accelerazione verso il basso di 0.8m/s^2
        self.new_y = self.bird_y0 - self.bird_speed_y0 * self.time_count + 0.2 * self.time_count * self.time_count
        #print(f"{self.new_y}, {self.bird_speed_y}, {self.bird_y}")

        if self.new_y <= 90:
            self.new_y = 90

        self.movement_y = self.new_y - self.bird_y
        self.w.move(self.bird, 0, self.movement_y)
        self.bird_y = self.new_y
        
        self.time_count+=1
    
    def die(self):
        #METTO A POSTO L'OSTACOLO
        self.w.delete(self.ostacolo_up)
        self.w.delete(self.ostacolo_down)

        self.obs_x = self.width_size-10                 #Posizione X del bordo sinistro
        self.obs_y_up = self.rand.randint(330) + 160     #Posizione Y della fine del tubo di sopra
        self.obs_y_down = self.obs_y_up + 170           #Posizione Y della fine del tubo di sotto
        self.ostacolo_up = self.w.create_rectangle(self.obs_x, 60, self.obs_x + 40, self.obs_y_up, fill="#1b5e20")
        self.ostacolo_down = self.w.create_rectangle(self.obs_x, self.obs_y_down, self.obs_x + 40, 760, fill="#1b5e20")

        #METTO A POSTO L'UCCELLO
        self.movement_y = 430 - self.bird_y
        self.w.move(self.bird, 0, self.movement_y)
        self.bird_y = 430
        self.bird_y0 = 430
        self.bird_speed_y = 0
        self.bird_speed_y0 = self.bird_speed_y
        self.jump_triggered = False
        self.w.itemconfig(self.bird, fill='red')

        self.time_count=0
        self.time_survive=0
        self.jumping = False
        self.jump_triggered = False
        self.obs_speed = 2
        


        
    def calc_score(self):
        #time.sleep(0.002)
        return self.time_survive

    

    def play(self):
        for i in range(0, self.n_entities):
            self.death=False
            count = 0
            while not self.death:
                self.move_obstacle()         #Per muovere gli ostacoli
                self.move_bird()             #Per muovere l'uccello

                self.time_survive+=0.001 + 0.0002*(1/(abs(self.bird_y-430)+0.5))

                if self.generation%5==0 or self.time_survive > 15:
                    #time.sleep(0.005)
                    pass

                self.dist_x = self.obs_x - 60                           #Distanza dell'ostacolo dall'uccello
                self.dist_y = self.obs_y_down - self.bird_y             #Distanza dell'altezza bassa del passaggio 

                #DO IN PASTO ALLA RETE GLI INPUT
                self.population[i].set_input([self.dist_x, self.dist_y, self.bird_y])
                received = self.population[i].calc_output()

                if received[0] > received[1] and not self.jump_triggered:
                    self.time_count=0
                    self.jump_triggered = True

                txt_for_datas = "G: " + str(self.generation) + " NN: " + str(i) + " BEST: " + str(round((self.last_best), 2)) + " S: " + str(round(self.time_survive, 3))
                self.w.itemconfig(self.datas, text=txt_for_datas)


                #COLLISION
                a = self.w.bbox(self.bird)
                b = self.w.bbox(self.ostacolo_up)
                c = self.w.bbox(self.ostacolo_down)

                if (b[0] in range(a[0],a[2]) or b[2] in range(a[0],a[2])) and (b[1] in range(a[1],a[3]) or b[3] in range(a[1],a[3])):
                    self.scores[i] = self.calc_score()
                    self.die()
                    self.death=True
                
                if (c[0] in range(a[0],a[2]) or c[2] in range(a[0],a[2])) and (c[1] in range(a[1],a[3]) or c[3] in range(a[1],a[3])):
                    self.scores[i] = self.calc_score()
                    self.die()
                    self.death=True
                
                if self.bird_y > 760:
                    self.scores[i] = self.calc_score()
                    self.die()
                    self.death=True

                if (i<self.n_entities and self.generation%100==0) or self.time_survive>5:
                    tk.update_idletasks()
                    tk.update()


    def evolve(self):
        self.generation += 1
        self.best_score = 0
        self.best_nn = -1
        for i in range(0, self.n_entities):
            if self.scores[i] > self.best_score:        # and self.scores[i] > self.last_best
                self.best_score = self.scores[i]
                self.best_nn = i
        

        

        if self.best_nn >=0:
            self.population[0] = self.population[self.best_nn]
        elif self.best_nn == -1:
            self.best_nn = 0
            self.best_score = self.scores[0]
            self.population[0] = self.population[self.best_nn]



        if self.best_score > self.last_best:
            self.last_best = self.best_score

        txt_for_print = "G: " + str(self.generation-1) + " NN: " + str(self.best_nn) + " BEST: " + str(round((self.last_best), 2)) + " | " + str(round((self.best_score), 2))
        print(txt_for_print)

    
        c=0

        for y in range(1, self.n_entities):

            mutation_rate = 0.15
            for l in range(1, self.population[y].n_layers):
                for n in range(0, self.population[y].layers_sizes[l]):
                    for w in range(0, self.population[y].layers_sizes[l-1]):
                        r = self.rand.rand()
                        c += 1
                        if r < mutation_rate:
                            self.population[y].layer[l].weights[n][w] = 2*self.rand.rand()-1
                        else:
                            self.population[y].layer[l].weights[n][w] = self.population[self.best_nn].layer[l].weights[n][w]


        self.population[5] = NeuralNetwork(self.generation*(-15), self.pop_layers)
        self.population[15] = NeuralNetwork(self.generation*(15), self.pop_layers)


game = Game(entities=100, network=[3,2,5,2,2])
#tk.update_idletasks()
#tk.update()


count=0
while True:
    game.play()
    game.evolve()