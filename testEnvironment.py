'''
This script shows how to use a call back with the bikeshare environment
'''

import shutil
import os
import numpy as np
import matplotlib.pyplot as plt
import gym
from Environments.BikeShare.FreeformLayout.StationList_Env import StationListEnv
from stable_baselines import A2C, PPO1, PPO2, ACER, ACKTR, TRPO
from stable_baselines.common.policies import MlpPolicy
#from stable_baselines.deepq import MlpPolicy
from stable_baselines import results_plotter
from stable_baselines.bench import Monitor
from stable_baselines.results_plotter import load_results, ts2xy
from stable_baselines.common.callbacks import BaseCallback


class LogResultsCallback(BaseCallback):
    """
    Callback for saving a model (the check is done every ``check_freq`` steps)
    based on the training reward (in practice, we recommend using ``EvalCallback``).

    :param check_freq: (int)
    :param log_dir: (str) Path to the folder where the model will be saved.
      It must contains the file created by the ``Monitor`` wrapper.
    :param verbose: (int)
    """
    def __init__(self, check_freq: int, log_dir: str, verbose=1):
        super(LogResultsCallback, self).__init__(verbose)
        self.check_freq = check_freq
        self.log_dir = log_dir
        self.save_path = os.path.join(log_dir, 'best_model')
        self.best_mean_reward = -np.inf

    def _init_callback(self) -> None:
        # Create folder if needed
        if self.save_path is not None:
            os.makedirs(self.save_path, exist_ok=True)

    def _on_step(self) -> bool:
        if self.n_calls % self.check_freq == 0:

          # Retrieve training reward
          x, y = ts2xy(load_results(self.log_dir), 'timesteps')
          if len(x) > 0:
              # Mean training reward over the last 100 episodes
              mean_reward = np.mean(y[-100:])
              if self.verbose > 0:
                print("Num timesteps: {}".format(self.num_timesteps))
                print("Best mean reward: {:.2f} - Last mean reward per episode: {:.2f}".format(self.best_mean_reward, mean_reward))

              # New best model, you could save the agent here
              if mean_reward > self.best_mean_reward:
                  self.best_mean_reward = mean_reward
                  # Example for saving best model
                  if self.verbose > 0:
                    print("Saving new best model to {}".format(self.save_path))
                  self.model.save(self.save_path)

        return True

# Create and wrap the environment
env = StationListEnv(
    2000,
    np.array([3,7,12,13,8,14,13,10,5,15]),
    np.array([10,10,10,10,10,10,10,10,10,10])
)


# Check environment
print(env)
print(env.action_space.sample())

for dir in ["A2C", "PPO1", "PPO2"]:
    os.makedirs(dir + "_MlpPolicy/")
# Agents
agentsToTest = {
     "A2C_MlpPolicy": A2C(MlpPolicy, Monitor(env, "A2C_MlpPolicy/"), verbose=0),
     "PPO1_MlpPolicy": PPO1(MlpPolicy, Monitor(env, "PPO1_MlpPolicy/"), verbose=0),
     "PPO2_MlpPolicy": PPO2(MlpPolicy, Monitor(env, "PPO2_MlpPolicy/"), verbose=0)
}

# Run each agent
for agent in agentsToTest.keys():
    print(agent)
    # Get model
    model = agentsToTest[agent]
    # Prepare environment
    env.reset()
    log_dir = agent + "/"
    # Clean up and create log directory


    # Train agent, every 1000 steps log results
    callback = LogResultsCallback(check_freq=1000, log_dir=log_dir, verbose=1)
    # Train the agent
    time_steps = 100000
    model.learn(total_timesteps=time_steps, callback=callback)
    results_plotter.plot_results([log_dir], time_steps, results_plotter.X_TIMESTEPS, agent)
    plt.savefig(agent + ".png")
    