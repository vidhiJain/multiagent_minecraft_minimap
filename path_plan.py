import gym
import numpy as np
import random

import marlgrid
import marlgrid.envs
import matplotlib.pyplot as plt

# env = gym.make('MarlGrid-3AgentCluttered11x11-v0')
# env = gym.make("MarlGrid-4AgentEmpty18x9-v0")
env = gym.make("MarlGrid-2AgentMinecraftOneRoom-v0")
obs = env.reset()
# agent_view_size = env.agents[0].view_size
passable_map = np.zeros((env.width, env.height)) # [[0]*env.height]*env.width
victim_map = np.zeros((env.width, env.height)) # [[0]*env.height]*env.width

mapgrid = env.grid.grid
for i in range(0, mapgrid.shape[0]):
    for j in range(0, mapgrid.shape[1]):
        obj = env.grid.obj_reg.key_to_obj_map[env.grid.grid[i][j]]
        if obj is None or obj.can_overlap():
            passable_map[i][j] = 1
        if obj is not None and obj.type=='Goal':
            victim_map[i][j] = 1



# targetted value matrix; source is the target; decreasing value from source
# untargetted value matrix; source is the agent position; increasing value from source

# In both case, policy is to take action that takes to the next state with highest value.


def get_path_matrix(passable_map, index, reward, increasing=True, discount_factor=0.99, time_penalty=0.01):
    path_matrix = np.zeros(passable_map.shape)
    path_matrix[index[0], index[1]] = reward
    
    queue = [[index[0], index[1]]]
    while len(queue):
        coordinate = queue.pop(0)           
        # print('coordinate', coordinate)
        coord_z, coord_x  = coordinate
        # print('coord_z', coord_z, 'coord_x', coord_x)

        for diff in [-1, 1]:                
            if passable_map[coord_z + diff, coord_x]:
                # if path_matrix[coord_z + diff][coord_x] == 0:
                if not (path_matrix[coord_z + diff][coord_x] or 0):
                    if increasing:
                        path_matrix[coord_z + diff][coord_x] += 1
                    else:
                        path_matrix[coord_z + diff][coord_x] += max(1e-10, discount_factor * path_matrix[coord_z][coord_x] - time_penalty)
                    queue.append([coord_z + diff, coord_x])

            if passable_map[coord_z, coord_x + diff]:   
                # if path_matrix[coord_z][coord_x + diff] == 0:
                if not (path_matrix[coord_z][coord_x + diff] or 0):
                    if increasing:
                        path_matrix[coord_z][coord_x + diff] += 1
                    else:
                        path_matrix[coord_z][coord_x + diff] += max(1e-10, discount_factor * path_matrix[coord_z][coord_x] - time_penalty)
                    queue.append([coord_z, coord_x + diff])
    return path_matrix

# def get_actions_from_value_matrix(path_matrix, agent_pos):
    



# get path matrix for each victim
# whichever agent has max value to the victim, make it move to it
victims_indices = np.argwhere(victim_map == 1)
victims_path_matrices = []
for index in victims_indices:
    victims_path_matrices.append(get_path_matrix(passable_map, index, reward=2, increasing=False))

breakpoint()

index_pm = []
for agent in env.agents:
    values = [m[agent.pos[0], agent.pos[1]] for m in path_matrices]
    max_val = max(values)
    index_pm.append([i for v in values if v == max_val])
    
for agent in env.agents:
    actions = get_actions_from_value_matrix(path_matrices[index_pm[i][0]], agent.pos)

# def get_actions():

# def get_actions(path_matrix, pos=(3, 6), ori=3):
#     next_value = []
#     # position depends on ori
#     if ori == 3:
#         pos = [3, 6]
#     elif ori == 0:
#         pos = [3, 0]
#     elif ori == 1:
#         pos = [0, 3]
#     elif ori == 2:
#         pos = [3, 6]
#     for d in [1, -1]:
#         next_value.append(path_matrix[pos[0] + d, pos[1]])
#         next_value.append(path_matrix[pos[0], pos[1] + d])
#     max_value = max(next_value)
#     max_ids = [i for i, v in enumerate(next_value) if v==max_value]
#     idx = random.choice(max_ids)

#     if idx - ori < 0:
#         actions.append(agent.actions.left)
#     elif    

#     return actions


# for agent in env.agents:
#     agent.action_sequence = []

#     tx, ty, bx, by = agent.get_view_exts()
    
#     indices = np.argwhere(victim_map[tx:bx, ty:by] == 1)
    
#     # go to victim at min dist 
#     if indices.shape[0]:
#         min_dist = env.width * env.height
#         min_idx = [env.width, env.height]
#         for index in indices:
#             manhattan_dist = abs(index[0] - agent.pos[0]) + abs(index[1] - agent.pos[1])
#             min_idx = index if min_dist > manhattan_dist else min_idx
#         breakpoint()
#         path_matrix = get_path_matrix(passable_map[tx:bx, ty:by], indices[min_idx], reward=2)

#     else:
#         breakpoint()
#         # flood fill increasingly in passable_map and move to the highest value filled.
#         path_matrix = get_path_matrix(passable_map[tx:bx, ty:by], agent.pos, reward=1)

#     # Now once you have the path matrix, just move to maximize the value of the state that the agent is in.
#     get_actions(path_matrix)

# breakpoint()
# # Check if passable_map is correct!
# # plt.matshow(passable_map)
# # plt.show()


# for each agent
# select nearest victim else decide frontiers 
# check if the victim has been selected by the higher ranking agent
# select the next nearest victim

# Demo path
for i in range(100):
    action = env.action_space.sample()
    obs, _, _, _ = env.step(action)
    img = env.render('rgb_array')
    plt.imshow(img)
    plt.xticks([])
    plt.yticks([])
    plt.draw()
    plt.pause(0.5)