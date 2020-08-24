import gym
import marlgrid
import marlgrid.envs
import matplotlib.pyplot as plt

# env = gym.make('MarlGrid-3AgentCluttered11x11-v0')
# env = gym.make("MarlGrid-4AgentEmpty18x9-v0")
env = gym.make("MarlGrid-4AgentMinecraftSparky-v0")
obs = env.reset()
# breakpoint()
for i in range(100):
    action = env.action_space.sample()
    obs, _, _, _ = env.step(action)
    img = env.render('rgb_array')
    plt.imshow(img)
    plt.xticks([])
    plt.yticks([])
    plt.draw()
    plt.pause(0.5)
    breakpoint()
