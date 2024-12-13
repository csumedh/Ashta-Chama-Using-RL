from stable_baselines3 import DQN
from stable_baselines3.common.env_checker import check_env
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.callbacks import CheckpointCallback
from ashtachamma_env import AshtachammaEnv
from torch.utils.tensorboard import SummaryWriter

# Create and check the environment
env = AshtachammaEnv(render_mode="human")
check_env(env)

# Wrap the environment
env = DummyVecEnv([lambda: env])

# Create the model with custom hyperparameters
model = DQN(
    "MlpPolicy", 
    env, 
    verbose=1, 
    learning_rate=4.5030982985412456e-05, 
    buffer_size=1000000,  # Replay buffer size
    batch_size=256,       # Batch size for training
    gamma=0.98,           # Discount factor
    train_freq=4,         # Train every 4 steps
    target_update_interval=10000,  # Update target network every 10000 steps
    exploration_fraction=0.1,      # Fraction of total timesteps for epsilon decay
    exploration_final_eps=0.02,    # Final value of epsilon
    tensorboard_log="./dqn_tensorboard/"
)

# Define checkpoint callback
checkpoint_callback = CheckpointCallback(save_freq=10000, save_path="./checkpoints/", name_prefix="ashtachamma_model")

writer = SummaryWriter(log_dir="./dqn_ashtachamma_tensorboard/")

# Train the agent
print("Training the model...")
model.learn(total_timesteps=8000000, callback=checkpoint_callback)
print("Training completed!")

# Save and load the model
model.save("ashtachamma_dqn_agent")
model = DQN.load("ashtachamma_dqn_agent")

# Evaluate the policy
print("Evaluating the policy...")
obs = env.reset()
n_eval_episodes = 100
for episode in range(n_eval_episodes):
    done = False
    episode_reward = 0
    while not done:
        action, _ = model.predict(obs, deterministic=True)  # Deterministic policy for evaluation
        obs, reward, done, info = env.step(action)
        episode_reward += reward
        if done:
            obs = env.reset()  # Reset the environment for the next episode
            print(f"Episode {episode + 1} finished with reward: {episode_reward}")

    writer.add_scalar("Episode Reward", episode_reward, episode)

# Play a single game
print("Playing a single game...")
obs = env.reset()
done = False

while not done:
    action, _ = model.predict(obs, deterministic=False)  # Use stochastic actions
    obs, reward, done, _ = env.step(action)
    env.render()
    # pygame.time.delay(500)

    if done:
        print("Game over! Resetting environment...")
        obs = env.reset()

env.close()
print("Game finished, resources cleaned up!")
