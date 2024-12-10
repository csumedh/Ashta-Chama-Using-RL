from stable_baselines3 import PPO
from stable_baselines3.common.env_checker import check_env
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.callbacks import CheckpointCallback
from ashtachamma_env import AshtachammaEnv
import pygame

# Create and check the environment
env = AshtachammaEnv(render_mode="human")
check_env(env)

# Wrap the environment
env = DummyVecEnv([lambda: env])

# Create the model with custom hyperparameters
model = PPO("MlpPolicy", env, verbose=1, learning_rate=2e-4, n_steps=4096, batch_size=124, n_epochs=10, gamma=0.99, gae_lambda=0.95,
            clip_range=0.2, ent_coef=0.03)

# Define checkpoint callback
checkpoint_callback = CheckpointCallback(save_freq=10000, save_path="./checkpoints/", name_prefix="ashtachamma_model")

# # Train the agent
# print("Training the model...")
# model.learn(total_timesteps=2000000, callback=checkpoint_callback)
# print("Training completed!")

# Save and load the model
# model.save("ashtachamma_ppo_agent")
model = PPO.load("ashtachamma_ppo_agent")

# Evaluate the policy
# print("Evaluating the policy...")
# obs = env.reset()
# n_eval_episodes = 100
# for episode in range(n_eval_episodes):
#     done = False
#     episode_reward = 0
#     while not done:
#         action, _ = model.predict(obs, deterministic=False)  # Deterministic policy for evaluation
#         obs, reward, done, info = env.step(action)
#         episode_reward += reward
#         if done:
#             obs = env.reset()  # Reset the environment for the next episode
#             print(f"Episode {episode + 1} finished with reward: {episode_reward}")

# Play a single game
print("Playing a single game...")
obs = env.reset()
done = False
while not done:
    action, _ = model.predict(obs, deterministic=False)  # Use deterministic actions
    obs, reward, done, _ = env.step(action)
    env.render()
    pygame.time.delay(1000)

    if done:
        print("Game over! Resetting environment...")
        obs = env.reset()

env.close()
print("Game finished, resources cleaned up!")