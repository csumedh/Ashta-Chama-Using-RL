# Import necessary libraries
from stable_baselines3 import DQN
from stable_baselines3.common.env_checker import check_env
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.callbacks import CheckpointCallback
from ashtachamma_env import AshtachammaEnv
from torch.utils.tensorboard import SummaryWriter

# Create and check the environment
env = AshtachammaEnv(render_mode="human")  # Custom environment
check_env(env)  # Ensure environment is valid

# Wrap the environment for batch processing
env = DummyVecEnv([lambda: env])

# Define and configure the DQN model
model = DQN(
    "MlpPolicy",
    env,
    verbose=1,
    learning_rate=4.5030982985412456e-05,
    buffer_size=1000000,
    batch_size=256,
    gamma=0.98,
    train_freq=4,
    target_update_interval=10000,
    exploration_fraction=0.1,
    exploration_final_eps=0.02,
    tensorboard_log="./dqn_tensorboard/"
)

# Checkpoint callback to save model periodically
checkpoint_callback = CheckpointCallback(save_freq=10000, save_path="./checkpoints/", name_prefix="ashtachamma_model")

# Initialize TensorBoard writer for logging
writer = SummaryWriter(log_dir="./dqn_ashtachamma_tensorboard/")

# Start training
print("Training the model...")
model.learn(total_timesteps=8000000, callback=checkpoint_callback)
print("Training completed!")

# Save and load the trained model
model.save("ashtachamma_dqn_agent")
model = DQN.load("ashtachamma_dqn_agent")

# Evaluate the policy over multiple episodes
print("Evaluating the policy...")
obs = env.reset()
n_eval_episodes = 100
for episode in range(n_eval_episodes):
    done = False
    episode_reward = 0
    while not done:
        action, _ = model.predict(obs, deterministic=True)  # Use deterministic policy
        obs, reward, done, info = env.step(action)
        episode_reward += reward
        if done:
            obs = env.reset()
            print(f"Episode {episode + 1} finished with reward: {episode_reward}")
    writer.add_scalar("Episode Reward", episode_reward, episode)

# Play a single game using the trained agent
print("Playing a single game...")
obs = env.reset()
done = False

while not done:
    action, _ = model.predict(obs, deterministic=False)  # Stochastic actions for exploration
    obs, reward, done, _ = env.step(action)
    env.render()  # Render the environment

    if done:
        print("Game over! Resetting environment...")
        obs = env.reset()

env.close()  # Clean up environment after game
print("Game finished, resources cleaned up!")
