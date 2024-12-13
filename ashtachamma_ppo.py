from stable_baselines3 import PPO
from stable_baselines3.common.env_checker import check_env
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.callbacks import CheckpointCallback
from ashtachamma_env import AshtachammaEnv
from torch.utils.tensorboard import SummaryWriter
import pygame

# Create and check the environment
env = AshtachammaEnv(render_mode="human")  # Initialize the custom environment with human-rendering mode
check_env(env)  # Validate the environment for compatibility with Stable-Baselines3

# Wrap the environment
env = DummyVecEnv([lambda: env])  # Wrap the environment to make it compatible with vectorized operations

# Create the model with custom hyperparameters
model = PPO(
    "MlpPolicy",  # Use a multi-layer perceptron policy
    env,  # Pass the environment
    verbose=1,  # Enable verbose logging
    learning_rate=1.4401226335484468e-05,  # Learning rate for the optimizer
    n_steps=6144,  # Number of steps per update
    batch_size=128,  # Batch size for optimization
    n_epochs=10,  # Number of epochs per update
    gamma=0.96,  # Discount factor for future rewards
    gae_lambda=0.9500000000000001,  # GAE lambda for advantage estimation
    clip_range=0.35,  # Clipping range for PPO
    ent_coef=0.0004724873659303969,  # Entropy coefficient for exploration
    tensorboard_log="./ppo_tensorboard/"  # Path for tensorboard logs
)

# Define checkpoint callback
checkpoint_callback = CheckpointCallback(
    save_freq=10000,  # Save model every 10,000 steps
    save_path="./checkpoints/",  # Directory to save checkpoints
    name_prefix="ashtachamma_model"  # Prefix for checkpoint filenames
)

# Initialize TensorBoard writer
writer = SummaryWriter(log_dir="./ppo_ashtachamma_tensorboard/")

# Train the agent
print("Training the model...")
model.learn(total_timesteps=7500000, callback=checkpoint_callback)  # Train the model for 7.5M timesteps
print("Training completed!")

# Save and load the model
model.save("ashtachamma_ppo_agent")  # Save the trained model to disk
model = PPO.load("ashtachamma_ppo_agent")  # Load the model back for evaluation

# Evaluate the policy
print("Evaluating the policy...")
obs = env.reset()  # Reset the environment
n_eval_episodes = 500  # Number of episodes for evaluation
for episode in range(n_eval_episodes):
    done = False
    episode_reward = 0
    while not done:
        action, _ = model.predict(obs, deterministic=False)  # Predict action using the model (non-deterministic)
        obs, reward, done, info = env.step(action)  # Take a step in the environment
        episode_reward += reward  # Accumulate the reward
        if done:
            obs = env.reset()  # Reset the environment for the next episode
            print(f"Episode {episode + 1} finished with reward: {episode_reward}")

    # Log the episode reward to TensorBoard
    writer.add_scalar("Episode Reward", episode_reward, episode)

# Play a single game
print("Playing a single game...")
obs = env.reset()  # Reset the environment
done = False

while not done:
    action, _ = model.predict(obs, deterministic=False)  # Predict action (non-deterministic)
    obs, reward, done, _ = env.step(action)  # Step through the environment
    env.render()  # Render the environment
    pygame.time.delay(500)  # Delay for better visual effect

    if done:
        print("Game over! Resetting environment...")
        obs = env.reset()  # Reset the environment when the game is over

# Close the environment
env.close()  # Clean up resources
print("Game finished, resources cleaned up!")
