import gym
from ashta_chamma_env import AshtaChammaEnv

# Register the environment
gym.envs.register(
    id='AshtaChamma-v0',
    entry_point='ashta_chamma_env:AshtaChammaEnv',
)

env = gym.make('AshtaChamma-v0')

# Test the environment
obs = env.reset()
done = False
while not done:
    action = env.action_space.sample()  # Random action
    obs, reward, done, truncated, info = env.step(action)
    env.render()
    if done:
        print("Game finished!")
        break