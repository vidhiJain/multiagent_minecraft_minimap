from ..base import MultiGridEnv, MultiGrid
from ..objects import *
from pathlib import Path

RESOURCES_DIR = (Path(__file__).parent / './resources').resolve()
# numpy_array = np.load(Path(RESOURCES_DIR, 'sparky_map.npy'))[:, 6:16, 24:34]
numpy_array = np.load(Path(RESOURCES_DIR, 'map_set_0.npy'))[:, 4:24, 18:40]

malmo_object_to_index = {
    # Basics
    'air'                       :     1, 
    'wooden_door'               :     2, 
    'dark_oak_door'             :     2,
    # 'wool' : 3, wall  : 4, 
    'lever'                     :     5, 
    # 'ball': 6,'box' : 7, 
    # 'goal': 8,
    'fire'                      :     9,
    'player'                    :     10, 

    # Walls
    'stained_hardened_clay'     :     4, 
    'clay'                      :     4,      # 42, 
    'iron_block'                :     4,      # 43, 
    'quartz_block'              :     4,      # 44,
    'redstone_wire'             :     4,      # 45,
    'gravel'                    :     4,      # 46, 
    'sticky_piston'             :     4,
    'piston_head'               :     4,
    'hardened_clay'             :     4,
    'stone'                     :     4,
    'bone_block'                :     4,
    'stained_glass_pane'        :     4,

    'bedrock'                   :     30,

    # Goals
    'redstone_block'            :     80,
    'gold_block'                :     81,
    'prismarine'                :     82,

    'wool'                      :     83,  
}
minigrid_index_mapping = {

    'object_mapping' : {
        0   :    'unseen',
        1   :    'None',
        2   :    'door',

        30  :    'wall',

        4   :    'wall',
        5   :    'key',

        80  :    'wall',
        81  :    'goal',
        82  :    'goal',
        83  :    'wall', 

        9   :    'lava',
        10  :    'agent',
        255 :    'box',
    },

    'color_mapping'  : {

        2   :    'inv_blue',

        30  :    'grey2',

        4   :    'inv_darkbrown', # 'grey',
        5   :    'yellow2',

        80  :    'inv_red',
        81  :    'inv_indianyellow', # 'red', 
        82  :    'inv_green2',
        83  :    'cyan', # 'white',

        255 :    'brown',

    },

    'toggletimes_mapping' : {

        # 80  :    0,
        81  :    5,
        82  :    2,
        # 83  :    0, 
        255 :    1,

    },

}


# breakpoint()
def fix_levers_on_same_level(same_level, above_level):
    """
    Input: 3D numpy array with malmo_object_to_index mapping

    Returns:
        3D numpy array where 3 channels represent 
        object index, color index, state index 
        for minigrid
    """
    lever_idx = malmo_object_to_index['lever']
    condition = above_level == lever_idx 
    minimap_array = np.where(condition, above_level, same_level) 
    return minimap_array


def fix_jump_locations(same_level, above_level, minigrid_index_mapping, jump_index=11):
    """
    Input: 3D numpy array with malmo_object_to_index mapping

    Returns:
        1. 3D numpy array where 3 channels represent 
        object index, color index, state index 
        for minigrid
        2. updated minigrid_index_mapping
    
    Notation for jump location 
            index = 11
            object = box
            color = grey # like walls
            toggletimes = 1

        NOTE: toggle to a box is a substitute for jump action
    """

    
    wall_idx = malmo_object_to_index['stained_hardened_clay']
    empty_idx = malmo_object_to_index['air']

    condition1 = same_level == wall_idx 
    condition2 = above_level == empty_idx

    minigrid_index_mapping['object_mapping'][jump_index] = 'box'
    minigrid_index_mapping['color_mapping'][jump_index] = 'white' #'grey0' # minigrid_index_mapping['color_mapping'][wall_idx]
    # minigrid_index_mapping['toggletimes_mapping'][jump_index] = 1

    # Elementwise product of two bool arrays for AND
    minimap_array = np.where(condition1 * condition2, jump_index, same_level) # jump_index is broadcasted!

    return minimap_array, minigrid_index_mapping


def fill_outside_with_wall(same_level, below_level):
    empty_idx = malmo_object_to_index['air']
    wall_idx = malmo_object_to_index['stained_hardened_clay']

    condition1 = below_level == empty_idx
    condition2 = same_level == empty_idx

    minimap_array = np.where(condition1 * condition2, wall_idx, same_level)

    return minimap_array


def get_minimap_from_voxel(raw_map, minigrid_index_mapping, jump_index=11):
    """
    Aggregates minimap obtained from different same_level and above_map transforms
    Input: 3D numpy array with malmo_object_to_index mapping

    Returns:
        1. 3D numpy array where 3 channels represent 
        object index, color index, state index 
        for minigrid
        2. updated minigrid_index_mapping
    
    Functioning:
        * fixes jump locations
        * fixes levers in same level

        NOTE: toggle to a box is a substitute for jump action
    """
    below_level = raw_map[0]
    same_level = raw_map[1]
    above_level = raw_map[2]
    
    minimap_array, modified_index_mapping = fix_jump_locations(
        same_level, above_level, minigrid_index_mapping, jump_index)
    minimap_array = fix_levers_on_same_level(minimap_array, above_level)
    minimap_array = fill_outside_with_wall(minimap_array, below_level)

    return minimap_array, modified_index_mapping

class MinecraftMultiGrid(MultiGridEnv):
    mission = "get to the green square"
    metadata = {}
    # def __init__(self):
        
    def _gen_grid(self, width, height):
        
        self.grid = MultiGrid((width, height))
        self.grid.wall_rect(0, 0, width, height)
        # self.put_obj(Goal(color="green", reward=1), width - 2, height - 2)
        self.index_mapping = minigrid_index_mapping
        if isinstance(numpy_array, str):
            raw_voxel_array = np.load(numpy_array)
        else:
            raw_voxel_array = numpy_array
        
        # self.put_obj(Goal(color="green", reward=1), width - 2, height - 2)
        
        minimap_array, modified_index_mapping = get_minimap_from_voxel(
            raw_voxel_array, minigrid_index_mapping, jump_index=11)
        
        self.array = minimap_array
        
        for mc_i in range(0, self.array.shape[0]):
            for mc_j in range(0, self.array.shape[1]):

                mg_i , mg_j = mc_i + 1 , mc_j + 1
                # breakpoint()
                entity_index = int(self.array[mc_i][mc_j])

                entity_name = self.index_mapping['object_mapping'].get(entity_index, None)
                if entity_name is None:
                    print("Check minigrid_index_mapping/object_mapping \
                        in utils/index_mapping.py \
                        as the entity_index {} is not found \
                        in object_mapping".format(entity_index))
                    raise KeyError

                entity_color = self.index_mapping['color_mapping'].get(entity_index, None)
                # entity_toggletime = self.index_mapping['toggletimes_mapping'].get(entity_index, None)
                # breakpoint()

                for entity_class in WorldObj.__subclasses__():
                    # the class name needs to be lowercase (not sentence case)
                    if entity_class.__name__ == 'BulkObj' and entity_name == 'wall':
                        self.put_obj(Wall(), mg_j, mg_i)
                        continue

                    if entity_name == entity_class.__name__.casefold():
                        
                        # print(entity_index, entity_name, entity_color, entity_toggletime)
                        # if entity_toggletime is not None:
                        #     self.put_obj(entity_class(
                        #         color=entity_color, 
                        #         toggletimes=entity_toggletime), mg_j, mg_i)
                        if entity_name == 'goal':
                            self.put_obj(entity_class(reward=1,
                                color=entity_color), mg_j, mg_i)

                        elif entity_color is not None:
                            self.put_obj(entity_class(
                                color=entity_color), mg_j, mg_i)
                        else:
                            self.put_obj(entity_class(), mg_j, mg_i)
        
        self.agent_spawn_kwargs = {}
        self.place_agents(**self.agent_spawn_kwargs)
        

if __name__ == "__main__":
    breakpoint()
    test = MinecraftMultiGrid()