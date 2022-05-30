# -*- coding: utf-8 -*
import numpy as np
from copy import deepcopy


class NeuralNetwork():
    def __init__(self, layers=None, seed=None):
        if layers is None or len(layers) < 2:
            raise Exception("Given shape is not valid")
        
        if seed is not None:
            np.random.seed(seed)

        self.layers_sizes = np.array(layers).astype(int)
        
        if not np.all(self.layers_sizes>0):
            raise Exception("Sizes must be positive integers")
        
        self.n_layers = len(self.layers_sizes)

        self.n_inputs = self.layers_sizes[0]
        self.n_outputs = self.layers_sizes[-1]
        
        
        '''
        I will store:
            a list self.weights which will consist in self.n_layers-1 np.arrays of floats connecting that layer to the next one.
            the dimension of each array will be equal to: as many rows as neurons in that layer, 
            as many columns as the neurons in the following layer. 
            
            a list self.values which will consist in self.n_layers np.arrays of floats, each
            will be as long as the number of neurons in that layer and contain their value at that time
        '''      
        
        self.weights = [None] * (self.n_layers-1)
        self.biases = [None] * (self.n_layers-1)
        for l in range(self.n_layers-1):
            self.weights[l] = np.zeros((self.layers_sizes[l], self.layers_sizes[l+1]))
            self.biases[l] = np.zeros((self.layers_sizes[l+1]))
        
        self.values = [None] * (self.n_layers)
        for l in range(self.n_layers):
            self.values[l]= np.zeros(self.layers_sizes[l])
    
    def randomize(self):
        for l in range(self.n_layers-1):
            self.weights[l][:,:] = np.random.rand(self.layers_sizes[l], self.layers_sizes[l+1]) * 2 - 1
            self.biases[l][:] = np.random.rand(self.layers_sizes[l+1]) * 2 - 1
            

    # def __repr__(self):
    #     print (f"Network Structure: {self.layers_sizes}")
    #     print(f"Weights: {self.weights}")
    #     print(f"Values: {self.values}")
    #     return ""

    def set_input(self, values):
        if len(values) != self.n_inputs:
            raise Exception("Size of inputs is not correct")
            
        self.values[0][:] = values
    
    def set_weights_as(self, other):
        if not isinstance(other, NeuralNetwork) or not np.all(self.layers_sizes == other.layers_sizes):
            raise Exception("This works only with another NN of same size")
        
        #if the two neural network coincide, I just don't do anything
        if self is other:
            return None
        
        for l in range(self.n_layers-1):
            self.weights[l][:,:] = other.weights[l][:,:]
            self.biases[l][:] = other.biases[l][:]
        
    def set_mutation_of(self, other, rate=0.10):
        if not isinstance(other, NeuralNetwork) or not np.all(self.layers_sizes == other.layers_sizes):
            raise Exception("This works only with another NN of same size")
        
        self.set_weights_as(other)
        
        for l in range(self.n_layers-1):
            random_ws = np.random.rand(self.layers_sizes[l], self.layers_sizes[l+1]) * 2 - 1
            mask_w = np.random.rand(self.layers_sizes[l], self.layers_sizes[l+1]) < rate
            self.weights[l][mask_w] = random_ws[mask_w]

            random_bs = np.random.rand(self.layers_sizes[l+1]) * 2 - 1
            mask_b = np.random.rand(self.layers_sizes[l+1]) < rate
            self.biases[l][mask_b] = random_bs[mask_b]
        

    def sigmoid(self, x):
        return 1 / (1 + np.exp(-x))
    
    def relu(self, x):
        return np.maximum(x,0)

    def calc_output(self):
        for l in range(1, self.n_layers):
            self.values[l] = self.relu(self.values[l-1] @ self.weights[l-1] + self.biases[l-1])
            
        return self.values[-1]
        
        #Old and slow way
        # for l in range(1, self.n_layers):
        #     for n in range(0, self.layers_sizes[l]):
        #         tot = 0.0
        #         for m in range(0, self.layers_sizes[l-1]):
        #             #i need the weight from m to n
        #             tot = tot + self.values[l-1][m] * self.weights[l-1][m, n]

        #         self.values[l][n] = self.sigmoid(tot)
        

    def copy(self):
        return deepcopy(self)