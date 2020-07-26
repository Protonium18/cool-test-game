import math, random

class Tile():
    def __init__(self, worldX, worldY):
        global image_set
        self.type = "Generic"
        self.worldX = worldX
        self.worldY = worldY
        self.inventory = list()
        self.inventory_size = 25
        self.inventory_dim = int(math.sqrt(self.inventory_size))
        self.ents = list()
        self.environment = ""
        self.is_passable = True
        self.is_occupied = False
        self.orig_image = "tile_grass1.png"
        self.image_rotation = random.randint(1,4)*90

    def interact(self):
        return()
            
class Tile_rock(Tile):
    def __init__(self, worldX, worldY):
        super().__init__(worldX, worldY)
        self.type = "Rock"
        self.is_passable = False
        self.orig_image = "tile3.png"
