from BikeShareEnvironments.UniformTiles.UniformTileWrapper import UniformTile_Wrapper
import matplotlib.pyplot as plt
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import Adam
from collections import deque
import numpy as np
import random

class DQN:
    def __init__(self, environment):
        self.env = environment

        self.memory = deque(maxlen=2000)

        self.gamma = 0.95
        self.epsilon = 1.0
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = 0.01
        self.model = self.buildModel()
        self.targ_model = self.buildModel()

    def remember(self, state, action, reward):
        self.memory.append([state, action, reward])

    def replay(self):
        batch_size = 32
        if len(self.memory) < batch_size:
            return
        samples = random.sample(self.memory, batch_size)
        for sample in samples:
            state, action, reward = sample
            target = self.targ_model.predict(state)

            self.model.fit(state, target, epochs=1, verbose=0)

    def act(self, state):
        self.epsilon *= self.epsilon_decay
        self.epsilon = max(self.epsilon_min, self.epsilon)
        if np.random.random() < self.epsilon:
            return np.array([[np.random.randint(5), np.random.randint(5), np.random.randint(5), np.random.randint(5)]])
        return np.multiply(self.model.predict(state), 5)

    def target_train(self):
        weights = self.model.get_weights()
        target_weights = self.targ_model.get_weights()
        for i in range(len(target_weights)):
            target_weights[i] = weights[i]
        self.targ_model.set_weights(target_weights)

    def buildModel(self):
        model = Sequential()
        model.add(Dense(24,
                        activation="relu", input_shape=(5,)))
        model.add(Dense(20))
        model.add(Dense(20))
        model.add(Dense(4, activation="sigmoid"))
        model.compile(loss="mean_squared_error",
                      optimizer=Adam(lr=self.learning_rate),
                      )
        return model

    def genSubState(self, station):
        subState = self.env.getSubState(station)
        state = self.env.getState()[0]
        out = [subState[0].getPercentCapacity()]
        for i in range(4):
            if subState[1][i] != None:
                out.append(state[subState[1][i]].getPercentCapacity())
            else:
                out.append(-1.0)
        return np.array([out])

    def run(self, games, stepsPerGame):
        allUnservice = []
        allExpenses = []
        for _ in range(games):
            print(_)
            self.env.reset()
            incentive = []
            for i in range(stepsPerGame):
                print("\t" + str(i))
                '''
                '''
                nextInterest = self.env.getState()[1]
                vectorSubState = self.genSubState(nextInterest[0])
                beforeActionLose = self.genLossofSubState(nextInterest[0])
                action = self.act(vectorSubState)[0]
                nextMove, expense, lastDir, done = self.env.step([0,1,2,3], action)
                if done:
                    break
                afterActionLose = self.genLossofSubState(nextInterest[0])
                reward = beforeActionLose - afterActionLose

                self.remember(vectorSubState, action, reward)
                self.replay()
                self.target_train()
                '''
                '''
                if i > 100 and i %100 == 0:
                    print(self.env.getUnserviceRatios()[-1])
            allExpenses.append(self.env.getExpenses())
            allUnservice.append(self.env.getUnserviceRatios())

        return allUnservice, allExpenses

    def genLossofSubState(self, sId):
        subState = self.env.getSubState(sId)

        state = self.env.getState()[0]
        out = [subState[0].computeLoss()]
        for i in range(4):
            if subState[1][i] != None:
                out.append(state[subState[1][i]].computeLoss())
        return sum(out)/len(out)

def _generateCostMatrix(length, width):
    outMatrix = np.zeros((4, length, width))
    for d in [0, 1, 2, 3]:
        for l in range(length):
            for w in range(width):
                outMatrix[d][l][w] = np.random.randint(5)

    return outMatrix
