
# coding: utf-8

# In[ ]:


import os
import gym
from gym_super_mario_bros.actions import SIMPLE_MOVEMENT
from keras import backend as K
from keras import optimizers
from nes_py.wrappers import BinarySpaceToDiscreteSpaceEnv
from _base import build_env, experiment_dir
from _top_level import top_level
top_level()


# In[ ]:


from src.agents import DeepQAgent
from src.base import AnnealingVariable
from src.wrappers import wrap
from src.models.losses import huber_loss
from src.callbacks import BaseCallback
from src.callbacks import JupyterCallback
from src.utils import seed


# # Environment

# In[ ]:


# set the global random number seed
seed(1)


# In[ ]:


# create the output directory for this experiment's data
output_dir = experiment_dir('../results', 'SuperMarioBros-Meta', DeepQAgent.__name__)
output_dir


# In[ ]:


def make_environment(monitor: bool=False, validation: bool=False, seed: int=1) -> gym.Env:
    """
    Make a gym environment for training, validation, or testing.

    Args:
        monitor: whether to apply a monitor to the environment
        seed: an optional random number seed for the environment

    Returns:
        a build gym environment with necessary wrappers applied

    """
    # make the environment
    if validation:
        env = gym.make('SuperMarioBros-v0')
    else:
        env = gym.make('SuperMarioBrosRandomStages-v0')
    # wrap the environment with an action space reducer
    env = BinarySpaceToDiscreteSpaceEnv(env, SIMPLE_MOVEMENT)
    # wrap the environment with transformers
    env = wrap(env,
        cache_rewards=True,
        noop_max=30,
        frame_skip=4,
        max_frame_skip=False,
        image_size=(84, 84),
        death_penalty=None,
        clip_rewards=False,
        agent_history_length=4
    )
    # monitor the video / data feed from the environment
    if monitor:
        monitor_dir = os.path.join(output_dir, 'monitor')
        env = gym.wrappers.Monitor(env, monitor_dir, force=True)
    # set the RNG seed for the environment
    if seed is not None:
        env.unwrapped.seed(seed)

    return env


# In[ ]:


env = make_environment()


# # Training

# In[ ]:


# create a file to save the weights to
weights_file = os.path.join(output_dir, 'weights.h5')


# In[ ]:


# create an agent
agent = DeepQAgent(env,
    render_mode='human',
    replay_memory_size=650000,
    prioritized_experience_replay=False,
    discount_factor=0.99,
    update_frequency=4,
    optimizer=optimizers.Adam(lr=2e-5),
    exploration_rate=AnnealingVariable(initial_value=1.0, final_value=0.01, steps=1e6),
    loss=huber_loss,
    target_update_freq=10000,
    dueling_network=False,
)
agent


# In[ ]:


agent.model.summary()


# In[ ]:


# observe random movement to pre-fill replay experience queue
agent.observe()


# In[ ]:


# create a callback for the training procedure to log weights and metrics
callback = BaseCallback(weights_file)
# create a callback for the training procedure to plot in Jupyter
# plotter = JupyterCallback()
# train the agent with given parameters and callbacks
agent.train(5e6, callback=callback)
# save the weights to disk after the training procedure
agent.model.save_weights(weights_file, overwrite=True)


# In[ ]:


# export plot data from the base callback to disk
callback.export(os.path.join(output_dir, 'training'))


# In[ ]:


# close the training environment
env.close()
# clear the keras session to remove the training model from memory
K.clear_session()


# # Validation

# In[ ]:


# create an environment for validation with a monitor attached
env = make_environment(validation=True)
# create a validation agent
agent = DeepQAgent(env, render_mode='human')
# load the trained weights into the validation agent
agent.model.load_weights(weights_file)


# In[ ]:


# run the agent through validation episodes
df = agent.play()


# In[ ]:


df.head()


# In[ ]:


df.tail()


# In[ ]:


# plot the validation results and save the tables and figures to disk
agent.plot_episode_rewards(os.path.join(output_dir, 'play'))


# In[ ]:


env.close()


#  