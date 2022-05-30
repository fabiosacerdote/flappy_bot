# -*- coding: utf-8 -*
from tkinter import *
import numpy as np
import time
from copy import deepcopy
import NeuralNetwork as nn
import matplotlib.pyplot as plt

#random.seed(30)
tk = Tk()

class FlappyBot():
    def __init__(self, n_tests=100, network=None):
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
        self.time_survive=0.0
        self.jumping = False
        self.jump_triggered = False
        self.received = np.zeros(2)



        #OSTACOLO
        self.obs_x = self.width_size-10                 #Posizione X del bordo sinistro
        self.obs_y_up = np.random.randint(330) + 145     #Posizione Y della fine del tubo di sopra
        self.obs_y_down = self.obs_y_up + 200           #Posizione Y della fine del tubo di sotto
        self.ostacolo_up = self.w.create_rectangle(self.obs_x, 60, self.obs_x + 40, self.obs_y_up, fill="#1b5e20")
        self.ostacolo_down = self.w.create_rectangle(self.obs_x, self.obs_y_down, self.obs_x + 40, 760, fill="#1b5e20")

        self.obs_speed = 1.7
        self.death=False


        #GREEDY VERSION
        self.num_move = 1
        self.accepted_moves = 0
        self.n_tests = n_tests

        if network is None or len(network) < 2:
            self.pop_layers = [2,2,5,2,2]
        else:
            self.pop_layers = network
        
        self.config = nn.NeuralNetwork(self.pop_layers)
        self.config_test = nn.NeuralNetwork(self.pop_layers)

        self.config.randomize()
        self.config_test.set_weights_as(self.config)

        self.test_score = np.zeros(n_tests)
        self.best_score = 0.0
        self.move_attempt = 0

        self.clip = False
        self.found = False
        self.finito = False


    
    def move_obstacle(self):
        if self.obs_x > -40:
            #MOVIMENTO VERSO DESTRA
            self.new_x = self.obs_x - self.obs_speed
            self.movement_x = self.new_x - self.obs_x
            self.w.move(self.ostacolo_up, self.movement_x, 0)
            self.w.move(self.ostacolo_down, self.movement_x, 0)
            self.obs_x = self.new_x
        else:
            '''
            #RIPOSIZIONAMENTO
            self.w.delete(self.ostacolo_up)
            self.w.delete(self.ostacolo_down)

            self.obs_x = self.width_size-10                 #Posizione X del bordo sinistro
            self.obs_y_up = self.rand.randint(330) + 160     #Posizione Y della fine del tubo di sopra
            self.obs_y_down = self.obs_y_up + 170           #Posizione Y della fine del tubo di sotto
            self.ostacolo_up = self.w.create_rectangle(self.obs_x, 60, self.obs_x + 40, self.obs_y_up, fill="#1b5e20")
            self.ostacolo_down = self.w.create_rectangle(self.obs_x, self.obs_y_down, self.obs_x + 40, 760, fill="#1b5e20")
            '''
            self.new_x = self.width_size-10  
            self.movement_x = self.new_x - self.obs_x
            self.obs_x = self.new_x

            self.new_obs_y_up = np.random.randint(330) + 145     #Posizione Y della fine del tubo di sopra
            self.new_obs_y_down = self.new_obs_y_up + 200           #Posizione Y della fine del tubo di sotto

            self.movement_y_up = self.new_obs_y_up - self.obs_y_up
            self.movement_y_down = self.new_obs_y_down - self.obs_y_down

            self.obs_y_up = self.new_obs_y_up
            self.obs_y_down = self.new_obs_y_down

            self.w.coords(self.ostacolo_up, self.obs_x, 60, self.obs_x + 40, self.obs_y_up)
            self.w.coords(self.ostacolo_down, self.obs_x, self.obs_y_down, self.obs_x + 40, 760)

            '''

            self.w.move(self.ostacolo_up, self.movement_x, self.movement_y_up)
            self.w.move(self.ostacolo_down, self.movement_x, self.movement_y_down)'''



    def move_bird(self):
        if self.jump_triggered == True and self.bird_speed_y < 0: #inizio nuovo salto
            self.time_count=0
            self.bird_speed_y = 10           #cambio la velocità verticale con una positiva
            self.bird_speed_y0 = self.bird_speed_y
            self.bird_y0 = self.bird_y       #posizione verticale iniziale
            self.jump_triggered = False
        else: #è già in un salto
            self.jump_triggered = False
        
        self.bird_speed_y -= 0.4            #considero accelerazione verso il basso di 0.8m/s^2
        self.new_y = self.bird_y0 - self.bird_speed_y0 * self.time_count + 0.2 * self.time_count * self.time_count

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
        self.obs_y_up = np.random.randint(330) + 145     #Posizione Y della fine del tubo di sopra
        self.obs_y_down = self.obs_y_up + 200           #Posizione Y della fine del tubo di sotto
        self.ostacolo_up = self.w.create_rectangle(self.obs_x, 60, self.obs_x + 40, self.obs_y_up, fill="#1b5e20")
        self.ostacolo_down = self.w.create_rectangle(self.obs_x, self.obs_y_down, self.obs_x + 40, 760, fill="#1b5e20")

        #METTO A POSTO IL QUADRATO
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
        cnt=0
        self.test_score[:] = 0.0
        for i in range(0, self.n_tests):
            self.death=False
            cnt += 1
            while not self.death:
                self.move_obstacle()         #Per muovere gli ostacoli
                self.move_bird()             #Per muovere l'uccello

                self.time_survive+=0.001 

                self.dist_x = self.obs_x - 20                           #Distanza dell'ostacolo dall'uccello
                self.dist_y = self.obs_y_down - self.bird_y             #Distanza dell'altezza bassa del passaggio 

                #DO IN PASTO ALLA RETE GLI INPUT
                #self.config_test.set_input([self.dist_x, self.dist_y, self.bird_y])
                self.config_test.set_input([self.dist_x, self.dist_y])
                self.received[:] = self.config_test.calc_output()

                if self.received[0] > self.received[1] and not self.jump_triggered:
                    #self.time_count=0
                    self.jump_triggered = True

                


                #COLLISION
                #(self.clip and self.num_move%20 == 0 and i < 3) or self.time_survive > 10 or self.num_move==1:
                condition = self.clip and (((self.num_move<=1 or self.num_move%5==0) and i < 1) or self.finito)
                if condition:
                    txt_for_datas = "NN: " + str(self.num_move) + " T: " + str(i) + " BEST: " + str(round((self.best_score), 2)) + " S: " + str(round(self.time_survive, 3))
                    self.w.itemconfig(self.datas, text=txt_for_datas)

                    tk.update_idletasks()
                    tk.update()
                    #time.sleep(0.0005)
                    if self.time_survive > 25 + int(game.found)*25:
                        time.sleep(0.002)
                    

                a = self.obs_x + 40 - 30
                b = self.bird_y - 30 - self.obs_y_up

                if (self.bird_y > 760) or (self.time_survive > 50 and not game.found) or ((0 < a < 70) and (b < 0 or b > 170)):
                    self.test_score[i] = self.calc_score()
                    if self.time_survive > 50:
                        self.found=True
                    self.die()
                    self.death=True
                    
                
        self.last_score = np.mean(self.test_score)
        

    def check_score(self):
        if self.num_move % 30 == 0:
            txt_for_print = "NN: " + str(self.num_move) + " [" + str(self.accepted_moves+1)+  "] BEST: " + str(round((self.best_score), 4)) + " | " + str(round((self.last_score), 4))
            print(txt_for_print)

        if self.last_score >= self.best_score:
            self.best_score = self.last_score
            self.accept_move()
            self.propose_move()
        
        else:
            self.move_attempt += 1
            self.propose_move()


                
    def accept_move(self):
        self.move_attempt = 0
        self.accepted_moves += 1
        self.config.set_weights_as(self.config_test)


    def propose_move(self):
        self.num_move += 1

        mutation_rate = 0.02  
        
        if np.random.rand() > 0.05:
            self.config_test.set_mutation_of(self.config, rate=mutation_rate)
        else:
            self.config_test.randomize()
    
    def get_best_score(self):
        return self.best_score
        

    

    


it = 1000
n_tests = 30
#[2,7,5,5,2]
game = FlappyBot(n_tests, network=[2,7,5,5,2])
final_i = it

iterations = np.arange(it)
all_scores = np.zeros((it, n_tests))
avg_scores = np.zeros(it) 
max_scores = np.zeros(it) 
min_scores = np.zeros(it) 

game.clip = True

for i in range(it):
    game.play()
    all_scores[i][:] = game.test_score
    avg_scores[i], max_scores[i], min_scores[i] = np.mean(game.test_score), np.max(game.test_score), np.min(game.test_score)
    if not game.found:
        game.check_score()
    else:
        final_i = i+1
        print("Allenamento completato")
        break


print(f"Final best score: {str(game.get_best_score())}")
print(f"Total moves accepted: {str(game.accepted_moves)}")

plt.plot(iterations[:final_i], avg_scores[:final_i],"-b")
plt.plot(iterations[:final_i], min_scores[:final_i],"--r", alpha=0.3)
plt.plot(iterations[:final_i], max_scores[:final_i],"--g", alpha=0.3)
plt.legend(["Avg Score", "Min Score", "Max Score"], loc="upper left")
plt.xlabel("Iteration")
plt.ylabel("Score")
plt.title("Scores over time")

plt.show()

game.finito = True
game.clip = True
for i in range(100):
    game.play()