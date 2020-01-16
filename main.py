import random, pickle, pygame, math, sys, traceback, os

pygame.init()
window_x = pygame.display.Info().current_w
window_y = pygame.display.Info().current_h
screen_origin_x = int(window_x/2)
screen_origin_y = int(window_y/2)
screen_h_multiplier = round(window_x/1080, 2)
screen_w_multiplier = round(window_y/1920, 2)


screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
pygame.display.set_icon(pygame.image.load("resources/tiles/tile1.png"))
pygame.display.set_caption("Felt")

player_x_offset = 0
player_y_offset = 0
camera_offsetx = 0
camera_offsety = 0
camera_offset_changex = 0
camera_offset_changey = 0

master_entity_table = {}
master_tile_table = {}
unloaded_tile_table = {}
render_space_bg = {}
render_space = {}
render_space_1 = {}
text_space = {}
load = 0
inv_open = False
turn_count = 0

map_x_width = 0
map_y_width = 0
static = False
selector = 0
tile_sizes = {}
tile_sizes[0] = 128
tile_sizes[1] = 64
tile_sizes[2] = 32
tile_sizes[3] = 16
tile_sizes[4] = 8
tile_sizes[5] = 4
tile_sizes[6] = 2
tile_sizes[7] = 1
tile_size = tile_sizes[selector]
game_status = 0
font_default = pygame.font.SysFont('Calibri', 30)
font_2 = pygame.font.SysFont('Calibri', 30)
font_title = pygame.font.SysFont('Arial', 60)

image_set = {}

def images_load():
    global image_set
    del image_set
    image_set = {}
    for folders in os.listdir(".//resources"):
        if folders == "extra":
            pass
        
        else:
            for images in os.listdir(".//resources/%s" %(folders)):
                image_set[images] = pygame.image.load(".//resources/%s/%s" %(folders, images))
                image_set[images] = pygame.transform.scale(image_set[images],(tile_size, tile_size))
            
        
    for x in master_tile_table:
        for y in master_tile_table[x]:
            master_tile_table[x][y].reload_image()
            
    for x in master_entity_table:
        master_entity_table[x].reload_image()
        
images_load() 


#Base Classes
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
        self.image = image_set[self.orig_image]
        self.screenx = screen_origin_x+(self.worldX*tile_size)+(player_x_offset*tile_size)+camera_offsetx
        self.screeny = screen_origin_y+(self.worldY*tile_size)+(player_y_offset*tile_size)+camera_offsety
        self.collision = pygame.Rect(self.screenx, self.screeny, tile_size, tile_size)

    def renderTile(self):
        global screen_origin_x
        global screen_origin_y
        global tile_size
        self.screenx = screen_origin_x+(self.worldX*tile_size)+(player_x_offset*tile_size)+camera_offsetx
        self.screeny = screen_origin_y+(self.worldY*tile_size)+(player_y_offset*tile_size)+camera_offsety
        self.collision = pygame.Rect(self.screenx, self.screeny, tile_size, tile_size)
        try:
            screen.blit(self.image,(self.screenx, self.screeny))
        except:
            pass

    def reload_image(self):
        self.image = image_set[self.orig_image]
        self.image = pygame.transform.rotate(self.image, 90*random.randint(1,4))

    def interact(self):
        return()
            
            
class Entity():
    def __init__(self, worldX, worldY, orig_image):
        self.name = "Entity"
        self.worldX = worldX
        self.worldY = worldY
        self.inventory = list()
        self.hp = 100
        self.inventory_size = 9
        self.inventory_dim = int(math.sqrt(self.inventory_size))
        self.loot_table = "entity_generic.txt"
        self.ID = random.randint(10000, 25000)
        self.accessTile(self.worldX, self.worldY).ents.append(self)
        self.occupied_tile = self.accessTile(self.worldX, self.worldY)
        self.occupied_tile.is_occupied = True
        master_entity_table[self.ID] = self
        self.orig_image = orig_image
        self.image = image_set[orig_image]
        self.loot_table_gen(4)
        self.equipped_weapon = self.inventory[0]

    def entSetPos(self, x, y):
        self.worldX = x
        self.worldY = y

    def entMove(self, xChange, yChange):
        new_x = self.worldX + xChange
        new_y = self.worldY + yChange
        try:
            if self.accessTile(new_x, new_y).is_passable == True and self.accessTile(new_x, new_y).is_occupied == False:
                self.occupied_tile.ents.remove(self)
                self.occupied_tile.is_occupied = False
                self.worldX = new_x
                self.worldY = new_y
                self.occupied_tile = self.accessTile(self.worldX, self.worldY)
                self.occupied_tile(self.worldX, self.worldY).ents.append(self)
                self.occupied_tile(self.worldX, self.worldY).is_occupied = True

            elif self.accessTile(new_x, new_y).is_passable == True and self.accessTile(new_x, new_y).is_occupied == True:
                self.attack(self.accessTile(new_x, new_y))

            else:
                print("Tile is inaccessible.")
                pass
        except:
            print("Tile is unable to be accessed.")
            pass
        
    def accessTile(self, x, y):
        global master_tile_table
        try:
            return(master_tile_table[x][y])
        except:
            print("Tile data is unable to be accessed.")
            pass
        
    def renderEnt(self):
        global screen_origin_x
        global screen_origin_y
        global tile_size
        self.screenx = screen_origin_x+(self.worldX*tile_size)+(player_x_offset*tile_size)+camera_offsetx
        self.screeny = screen_origin_y+(self.worldY*tile_size)+(player_y_offset*tile_size)+camera_offsety
        if self.screenx > window_x+256 or self.screeny > window_y+256:
            pass
        else:
            try:
                screen.blit(self.image,(self.screenx, self.screeny))
            except:
                pass

    def reload_image(self):
        self.image = image_set[self.orig_image]

    def attack(self, targetted_tile):
        target = targetted_tile.ents[0]
        damage = self.equipped_weapon.damage+random.randint(0, self.equipped_weapon.damage_range)
        target.take_damage(damage)
        print("{} attacked {} for {} damage using {}!".format(self.name, target.name, damage, self.equipped_weapon.item_name))

    def take_damage(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            self.delete()

    def delete(self):
        try:
            self.occupied_tile.inventory += self.inventory
            self.occupied_tile.is_occupied = False
            print("{} died!".format(self.name))
            del master_entity_table[self.ID]
        except:
            pass
        
    def pick_up_item(self, list_pos):
        if len(self.inventory) > self.inventory_size:
            pass
        else:
            self.inventory.append(self.occupied_tile.inventory[list_pos])
            self.occupied_tile.inventory.remove(self.occupied_tile.inventory[list_pos])

    def take_item(self, target_ent, item_slot):
        if len(self.inventory) > self.inventory_size:
            pass
        else:
            self.inventory.append(target_ent.inventory[item_slot])
            target_ent.inventory.remove(target_ent.inventory[item_slot])

    def drop_item(self, target_ent, item_slot):
        self.occupied_tile.inventory.append(target_ent.inventory[item_slot])
        target_ent.inventory.remove(target_ent.inventory[item_slot])

    def item_equip(self, item):
        self.equipped_weapon = item
            
    def loot_table_gen(self, passes):
        if os.path.exists(".\\loot_tables/{}".format(self.loot_table)):
            with open(".\\loot_tables/{}".format(self.loot_table)) as file:
                loot_list = file.read().splitlines()
                for i in range(passes):
                    self.inventory.append(Item.from_txt(loot_list[random.randint(0, len(loot_list)-1)]))

        else:
            print("Error! Invalid loot table.")
        
class Player(Entity):
    def __init__(self, worldX, worldY, image_id):
        super().__init__(worldX, worldY, image_id)
        self.name = "Player"
        self.last_unloaded_pos_x = self.worldX
        self.last_unloaded_pos_y = self.worldY
        self.old_unloaded_pos_x = self.worldX
        self.old_unloaded_pos_y = self.worldY
            
    def entMove(self, xChange, yChange):
        new_x = self.worldX + xChange
        new_y = self.worldY + yChange
        try:
            if self.accessTile(new_x, new_y).is_passable == True and self.accessTile(new_x, new_y).is_occupied == False:
                self.occupied_tile.ents.remove(self)
                self.occupied_tile.is_occupied = False
                self.worldX = new_x
                self.worldY = new_y
                self.occupied_tile = self.accessTile(self.worldX, self.worldY)
                self.occupied_tile.ents.append(self)
                self.occupied_tile.is_occupied = True
                global static
                if static == False:
                    global player_x_offset
                    global player_y_offset
                    player_x_offset = -self.worldX
                    player_y_offset = -self.worldY

            elif self.accessTile(new_x, new_y).is_passable == True and self.accessTile(new_x, new_y).is_occupied == True:
                self.attack(self.accessTile(new_x, new_y))

            else:
                print("Tile is inaccessible.")
                pass
        except:
            pass
    
    def renderEnt(self):
        global screen_origin_x
        global screen_origin_y
        global static
        global tile_size
        if static == False:
            self.screenx = screen_origin_x+camera_offsetx
            self.screeny = screen_origin_y+camera_offsety
        else:
            self.screenx = screen_origin_x+(self.worldX*tile_size)+(player_x_offset*tile_size)+camera_offsetx
            self.screeny = screen_origin_y+(self.worldY*tile_size)+(player_y_offset*tile_size)+camera_offsety
        try:
            screen.blit(self.image,(self.screenx, self.screeny))
        except:
            pass

class Item():
    def __init__(self, item_name, damage=1, damage_range=5, category="Generic", weight=1, icon="resources/tiles/tile1.png"):
        self.item_name = item_name
        self.damage = damage
        self.damage_range = damage_range
        self.id = 1
        self.category = category
        self.weight = weight
        self.icon = icon

    @classmethod
    def from_txt(cls, name):
        if os.path.exists("items/{}.txt".format(name)) == True:
            with open("items/{}.txt".format(name)) as file:
                lines = file.read().splitlines()
                item_name = lines[0]
                damage = int(lines[1])
                damage_range = int(lines[2])
                category = lines[3]
                weight = int(lines[4])
                icon = lines[5]
                return cls(item_name, damage, damage_range, category, weight, icon)
        else:
            print("Error! Invalid item name.")
            

class Button():
    def __init__(self, pos_x, pos_y, size_x, size_y, R,G,B, text, func_name, args):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.size_x = size_x
        self.size_y = size_y
        self.collision = pygame.Rect(pos_x, pos_y, size_x, size_y)
        self.collision.center = (pos_x, pos_y)
        self.color = (R,G,B)
        self.default_color = (R,G,B)
        self.text = text
        self.font = font_default
        self.func_name = func_name
        self.args = args
    def render(self):
        pygame.draw.rect(screen, self.color, self.collision)
        
    def render_text(self):
        text_surf = self.font.render(self.text, True, (255, 255, 255))
        screen.blit(text_surf, (self.pos_x - text_surf.get_width() // 2, self.pos_y - text_surf.get_height() // 2))

    def clicked(self):
        #globals()["%s" %self.func_name]()
        if self.func_name != "":
            if self.args == "":
                getattr(sys.modules[__name__], "%s" %self.func_name)()
            else:
                getattr(sys.modules[__name__], "%s" %self.func_name)(self.args)
        else:
            pass
        
        
class Text():
    def __init__(self, pos_x, pos_y, text, size):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.text = text
        self.size = size
        self.font = font_title

    def render(self):
        text_surf = self.font.render(self.text, False, (0, 0, 0))
        screen.blit(text_surf, (self.pos_x - text_surf.get_width() // 2, self.pos_y - text_surf.get_height() // 2))

class Image():
    def __init__(self, image_path, size_x, size_y, pos_x, pos_y):
        self.image = pygame.image.load(image_path)
        self.size_x = size_x
        self.size_y = size_y
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.image = pygame.transform.scale(self.image,(size_x, size_y))

    def render(self):
        screen.blit(self.image, (self.pos_x - self.image.get_width() // 2, self.pos_y - self.image.get_height() // 2))


#Tile Subclasses
class Tile_rock(Tile):
    def __init__(self, worldX, worldY):
        super().__init__(worldX, worldY)
        self.type = "Rock"
        self.is_passable = False
        self.orig_image = "tile3.png"
        
        
        
def tileGen(sizeX, sizeY):
    global master_tile_table
    sizeX = int(sizeX/2)
    sizeY = int(sizeY/2)
    for x in range(-sizeX, sizeX):
        master_tile_table[x] = {}
        unloaded_tile_table[x] = {}
        for y in range(-sizeY, sizeY):
            unloaded_tile_table[x][y] = ""
            master_tile_table[x][y] = Tile(x, y)
                        
def loadData():
    global master_tile_table
    global master_entity_table
    global unloaded_tile_table
    global player
    game_clean()
    with open('map_data.pkl', 'rb') as input:
        master_tile_table = pickle.load(input)
        master_entity_table = pickle.load(input)
        unloaded_tile_table = pickle.load(input)
        player = pickle.load(input)
        
        for x in master_tile_table:
            for y in master_tile_table[x]:
                master_tile_table[x][y].reload_image()

        for x in unloaded_tile_table:
            for y in unloaded_tile_table[x]:
                unloaded_tile_table[x][y].reload_image()

        for x in master_entity_table:
            master_entity_table[x].reload_image()

    player.entMove(0,0)
    dyn_unload()
    print("Data loaded!")

def saveData():
    global master_tile_table
    global unloaded_tile_table
    load_all_tiles()

    for x in master_tile_table:
        for y in master_tile_table[x]:
            master_tile_table[x][y].image = ""

    for x in unloaded_tile_table:
        for y in unloaded_tile_table[x]:
            unloaded_tile_table[x][y].image = ""

    for x in master_entity_table:
        master_entity_table[x].image = ""

            
    with open('map_data.pkl', 'wb') as output:
        pickle.dump(master_tile_table, output, pickle.HIGHEST_PROTOCOL)
        pickle.dump(master_entity_table, output, pickle.HIGHEST_PROTOCOL)
        pickle.dump(unloaded_tile_table, output, pickle.HIGHEST_PROTOCOL)
        pickle.dump(player, output, pickle.HIGHEST_PROTOCOL)
        
    print("Data saved!")

def render_screen():
    for x in master_tile_table:
        for y in master_tile_table:
            try:
                open_tile = master_tile_table[x][y]
                open_tile.renderTile()
            except:
                pass
            
    for ent in master_entity_table:
        open_ent = master_entity_table[ent]
        open_ent.renderEnt()

def unload_tiles():
    for x in master_tile_table:
        for y in master_tile_table:
            try:
                unloaded_tile_table[x][y] = master_tile_table[x][y]
                del master_tile_table[x][y]
            except:
                traceback.print_exc()
                pass
    player.last_unloaded_pos_x = player.occupied_tile.worldX
    player.last_unloaded_pos_y = player.occupied_tile.worldY
    print("Tiles unloaded")

def load_all_tiles():
    for x in unloaded_tile_table:
        for y in unloaded_tile_table:
            try:
                master_tile_table[x][y] = unloaded_tile_table[x][y]
                del unloaded_tile_table[x][y]
            except:
                pass
    print("Tiles loaded")

def dyn_unload():
    for x in master_tile_table:
        for y in master_tile_table:
            try:
                open_tile = master_tile_table[x][y]
                if open_tile.screenx > window_x+1024 or open_tile.screeny > window_y+1024 or open_tile.screenx < -1024 or open_tile.screeny < -1024:
                    unloaded_tile_table[x][y] = master_tile_table[x][y]
                    del master_tile_table[x][y]
            except:
                pass

                    
    player.old_unloaded_pos_x = player.occupied_tile.worldX
    player.old_unloaded_pos_y = player.occupied_tile.worldY
    print("Dynamic unload")
    
def load_tiles():
    global tile_size
    searchdist = 30
    for x in range(player.occupied_tile.worldX-searchdist, player.occupied_tile.worldX+searchdist):
        for y in range(player.occupied_tile.worldY-searchdist, player.occupied_tile.worldY+searchdist):
            try:
                master_tile_table[x][y] = unloaded_tile_table[x][y]
                del unloaded_tile_table[x][y]
                master_tile_table[x][y].reload_image()
            except:
                pass
    player.last_unloaded_pos_x = player.occupied_tile.worldX
    player.last_unloaded_pos_y = player.occupied_tile.worldY
    print("Tiles loaded.")
    
def check_if_load():
    dist = math.hypot(player.last_unloaded_pos_x - player.occupied_tile.worldX, player.last_unloaded_pos_y - player.occupied_tile.worldY)
    dist2 = math.hypot(player.old_unloaded_pos_x - player.occupied_tile.worldX, player.old_unloaded_pos_y - player.occupied_tile.worldY)
    if tile_size == 4 or tile_size == 2 or tile_size == 1 or tile_size == 8:
        travelled_dist = 5
    elif tile_size == 16:
        travelled_dist = 5
    elif tile_size == 32:
        travelled_dist = 5
    elif tile_size == 64:
        travelled_dist = 8
    elif tile_size == 128:
        travelled_dist = 4
    if dist > travelled_dist:
        load_tiles()
        if dist2 > travelled_dist*4:
            dyn_unload()

def load_game():
    global game_status
    game_status = 1
    render_clear()
    game_start()
    
def quit_game():
    pygame.quit()

def set_map_size(x):
    global map_x_width
    global map_y_width
    map_x_width = x
    map_y_width = x

def set_map_size_to_game(x):
    global map_x_width
    global map_y_width
    map_x_width = x
    map_y_width = x
    load_game()

def set_tile_size(passed_selector):
    global selector
    global tile_size
    selector = passed_selector
    tile_size = tile_sizes[passed_selector]

    images_load()
    

def text_render():
    try:
        for text in text_space:
            text_space[text].render()
    except:
        pass

def button_render():
    try:        
        for button in render_space:
            render_space[button].render()
            render_space[button].render_text()
            
    except(RuntimeError):
        return
    except:
        pass

def button_render_1():
    try:
        for button in render_space_1:
            render_space_1[button].render()
            render_space_1[button].render_text()
            
    except(RuntimeError):
        return
    except:
        pass

def render_clear():
    render_space.clear()
    render_space_1.clear()
    text_space.clear()

def start_menu():
    global game_status
    if map_x_width == 0:
        func = "map_options_menu"
        arg = True
    else:
        func = "load_game"
        arg = ""
        
    game_clean()
    game_status = 0
    render_clear()
    render_space[1] = Button(screen_origin_x, screen_origin_y/2, screen_origin_x/2, screen_origin_x/16, 255, 0, 0, "Start", func, arg)
    render_space[2] =  Button(screen_origin_x, screen_origin_y/2+100, screen_origin_x/2, screen_origin_x/16, 255, 0, 0, "Load", "", "")
    render_space[3] =  Button(screen_origin_x, screen_origin_y/2+200, screen_origin_x/2, screen_origin_x/16, 255, 0, 0, "Options", "options_menu", "" )
    render_space[4] =  Button(screen_origin_x, screen_origin_y/2+300, screen_origin_x/2, screen_origin_x/16, 255, 0, 0, "Quit", "quit_game", "" )
    text_space[1] = Text(screen_origin_x, screen_origin_y/2-100, "Cool Test Game", 5)
    text_space[2] = Image("resources/extra/title_bg.png", window_x, window_y, screen_origin_x, screen_origin_y)

def pause_menu():
    global game_status
    render_clear()
    quit_button =  Button(screen_origin_x, screen_origin_y/2+300, screen_origin_x/2, screen_origin_x/16, 255, 0, 0, "Quit", "start_menu", "" )
    resume_button =  Button(screen_origin_x, screen_origin_y/2+200, screen_origin_x/2, screen_origin_x/16, 255, 0, 0, "Resume", "resume_game", "" )

    render_space[1] = quit_button
    render_space[2] = resume_button
    game_status = 2
    pygame.mouse.set_visible(True)

def options_menu():
    render_clear()
    render_space[1] = Button(screen_origin_x, screen_origin_y/2, screen_origin_x/2, screen_origin_x/16, 255, 0, 0, "Map Size", "map_options_menu", "False")
    render_space[2] = Button(screen_origin_x, screen_origin_y/2+100, screen_origin_x/2, screen_origin_x/16, 255, 0, 0, "Tile Size", "tile_size_menu", "")
    render_space[3] =  Button(screen_origin_x, screen_origin_y/2+600, screen_origin_x/4, screen_origin_x/16, 255, 0, 0, "Back", "start_menu", "")    
    text_space[1] = Text(screen_origin_x, screen_origin_y/2-100, "Options", 5)

    pygame.mouse.set_visible(True)

def map_options_menu(start_game):
    render_clear()
    if start_game == True:
        func = "set_map_size_to_game"
        func2 = "start_menu"
    else:
        func = "set_map_size"
        func2 = "options_menu"
    
    text_space[1] = Text(screen_origin_x, screen_origin_y/2-100, "Map Size", 5)
    render_space[0] = Button(screen_origin_x, screen_origin_y/2, screen_origin_x/4, screen_origin_x/16, 255, 0, 0, "10x10", func, 10)
    render_space[1] = Button(screen_origin_x, screen_origin_y/2+100, screen_origin_x/4, screen_origin_x/16, 255, 0, 0, "50x50", func, 50)
    render_space[2] =  Button(screen_origin_x, screen_origin_y/2+200, screen_origin_x/4, screen_origin_x/16, 255, 0, 0, "100x100", func, 100)
    render_space[3] =  Button(screen_origin_x, screen_origin_y/2+300, screen_origin_x/4, screen_origin_x/16, 255, 0, 0, "200x200", func, 200)
    render_space[4] =  Button(screen_origin_x, screen_origin_y/2+400, screen_origin_x/4, screen_origin_x/16, 255, 0, 0, "500x500", func, 500)
    render_space[5] =  Button(screen_origin_x, screen_origin_y/2+700, screen_origin_x/4, screen_origin_x/16, 255, 0, 0, "Back", func2, "")
    pygame.mouse.set_visible(True)

def tile_size_menu():
    render_clear()
    text_space[1] = Text(screen_origin_x, screen_origin_y/2-100, "Tile Size", 5)
    render_space[1] = Button(screen_origin_x, screen_origin_y/2, screen_origin_x/4, screen_origin_x/16, 255, 0, 0, "128x128", "set_tile_size", 0)
    render_space[2] =  Button(screen_origin_x, screen_origin_y/2+100, screen_origin_x/4, screen_origin_x/16, 255, 0, 0, "64x64", "set_tile_size", 1)
    render_space[3] =  Button(screen_origin_x, screen_origin_y/2+200, screen_origin_x/4, screen_origin_x/16, 255, 0, 0, "32x32", "set_tile_size", 2)
    render_space[4] =  Button(screen_origin_x, screen_origin_y/2+600, screen_origin_x/4, screen_origin_x/16, 255, 0, 0, "Back", "options_menu", "")
    
    pygame.mouse.set_visible(True)

def open_inventory(target):
    render_clear()
    dim = target.inventory_dim
    v = 0
    x = 0
    global inv_open
    inv_open = True
    
    for column in range(0, dim):
        for line in range(0, dim):
            v += 1
            render_space[v] = Button(screen_origin_x+(68*line), screen_origin_y+(68*column), 64, 64, 50 ,50, 50, "", "inventory_actions", (v, target))
    v-=1
    for item in target.inventory:
        x += 1
        pos_x = render_space[x].pos_x
        pos_y = render_space[x].pos_y
        text_space[x] = Image(item.icon, 58, 58, pos_x, pos_y)

def inventory_actions(data):
    if text_space[data[0]]:
        print("ee")
        render_space_1[-5] =  Button(render_space[data[0]].pos_x-40, render_space[data[0]].pos_y-25, 70, 30, 255, 0, 0, "{}".format(data[1].inventory[data[0]-1].item_name), "", "")
        if isinstance(data[1], Player) != True:
            render_space_1[-1] =  Button(render_space[data[0]].pos_x-40, render_space[data[0]].pos_y+10, 70, 30, 255, 0, 0, "Take", "inventory_take", data)
            
        if isinstance(data[1], Entity):
            render_space_1[-2] =  Button(render_space[data[0]].pos_x-40, render_space[data[0]].pos_y+45, 70, 30, 255, 0, 0, "Drop", "inventory_drop", data)

        if isinstance(data[1], Player):
            render_space_1[-3] =  Button(render_space[data[0]].pos_x-40, render_space[data[0]].pos_y+80, 70, 30, 255, 0, 0, "Equip", "inventory_equip", data)
    else:
        pass

def inventory_take(data):
    try:
        text_space.pop(data[0])
        render_space_1.pop(-1)
        player.take_item(data[1], data[0]-1)
        open_inventory(data[1])
    except:
        traceback.print_exc()
        pass

def inventory_drop(data):
    try:
        text_space.pop(data[0])
        render_space_1.pop(-2)
        player.drop_item(data[1], data[0]-1)
        open_inventory(data[1])
    except:
        traceback.print_exc()
        pass

def inventory_equip(data):
    player.item_equip(data[1].inventory[data[0]-1])
    render_space_1.pop(-3)

def resume_game():
    global game_status
    render_clear()
    game_status = 1

def game_start():
    global start_game
    start_game = True
    tileGen(map_x_width, map_y_width)
    global player
    global enemy
    images_load()
    player = Player(0,0,"player.png")
    enemy = Entity(4,0,"player.png")
    render_screen()
    unload_tiles()
    load_tiles()

def game_clean():
    global master_entity_table
    global master_tile_table
    global unloaded_tile_table
    global player_x_offset
    global player_y_offset 
    global camera_offsetx
    global camera_offsety
    global camera_offset_changex
    global camera_offset_changey
    master_entity_table.clear()
    master_tile_table.clear()
    unloaded_tile_table.clear()
    player_x_offset = 0
    player_y_offset = 0
    camera_offsetx = 0
    camera_offsety = 0
    camera_offset_changex = 0
    camera_offset_changey = 0
    
start_menu()
running = True
while running:
    screen.fill((0,0,0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()

        if game_status == 1:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    player.entMove(-1, 0)
                    
                if event.key == pygame.K_RIGHT:
                    player.entMove(1, 0)

                if event.key == pygame.K_UP:
                    player.entMove(0, -1)

                if event.key == pygame.K_DOWN:
                    player.entMove(0, 1)

                if event.key == pygame.K_LSHIFT:
                    static = True

                if event.key == pygame.K_RSHIFT:
                    static = False
                    camera_offsetx = 0
                    camera_offsety = 0
                    player.entMove(0,0)

                if event.key == pygame.K_f:
                    unload_tiles()

                if event.key == pygame.K_r:
                    load_all_tiles()

                if event.key == pygame.K_l:
                    saveData()

                if event.key == pygame.K_o:
                    loadData()

                if event.key == pygame.K_i:
                    if inv_open == True:
                        render_clear()
                        inv_open = False

                    else:
                        open_inventory(player)
                    
                if event.key == pygame.K_g:
                    if inv_open == True:
                        render_clear()
                        inv_open = False

                    else:
                        open_inventory(player.occupied_tile)

                if event.key == pygame.K_m:
                    print(master_entity_table)
                    print(len(master_tile_table))
                    print(master_tile_table)

                if event.key == pygame.K_u:
                    print(turn_count)

                if event.key == pygame.K_p:
                    print(player.occupied_tile.image)

                if event.key == pygame.K_x:
                    try:
                        selector += 1
                        tile_size = tile_sizes[selector]
                        print(tile_size)
                        images_load()
                        load_tiles()
                        render_screen()
                    except:
                        pass
                        print("Key error!")
                    
                if event.key == pygame.K_z:
                    try:
                        selector -= 1
                        tile_size = tile_sizes[selector]
                        print(tile_size)
                        images_load()
                        load_tiles()
                        render_screen()
                    except:
                        pass
                        traceback.print_exc()
                        print("Key error!")
                    

                if event.key == pygame.K_ESCAPE:
                    pause_menu()
                    
                turn_count+=1
                check_if_load()
                    
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    camera_offset_changex += 10
                    
                if event.key == pygame.K_d:
                    camera_offset_changex -= 10

                if event.key == pygame.K_w:
                    camera_offset_changey += 10

                if event.key == pygame.K_s:
                    camera_offset_changey -= 10
            
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_a or event.key == pygame.K_d:
                    camera_offset_changex = 0
                if event.key == pygame.K_s or event.key == pygame.K_w:
                    camera_offset_changey = 0
                    
        if game_status == 1:
            if event.type == pygame.MOUSEBUTTONDOWN:
                for x in master_tile_table:
                    for y in master_tile_table[x]:    
                        try:
                            if master_tile_table[x][y].collision.collidepoint(event.pos):
                                pass
                        except:
                            traceback.print_exc()
                            pass

        if game_status == 3:
            if event.type == pygame.MOUSEBUTTONDOWN:
                pass
                
                    
        if game_status == 0 or 2:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                
                for button in list(render_space_1):
                    try:
                        if render_space_1[button].collision.collidepoint(event.pos):
                            render_space_1[button].clicked()
                    except:
                        traceback.print_exc()
                        pass
                    
                for button in list(render_space):
                    try:
                        if render_space[button].collision.collidepoint(event.pos):
                            render_space[button].clicked()
                    except:
                        traceback.print_exc()
                        pass
                
        
            if event.type == pygame.MOUSEMOTION:
                for button in list(render_space):
                    try:
                        if render_space[button].collision.collidepoint(pygame.mouse.get_pos()):
                            render_space[button].color = [0, 255, 0]
                        else:
                            render_space[button].color =  render_space[button].default_color
                    except:
                        pass

                for button in list(render_space_1):
                    try:
                        if render_space_1[button].collision.collidepoint(pygame.mouse.get_pos()):
                            render_space_1[button].color = [0, 255, 0]
                        else:
                            render_space_1[button].color =  render_space_1[button].default_color
                    except:
                        pass


    if game_status != 0:     
        render_screen()
        
    button_render()
    text_render()
    button_render_1()
    camera_offsetx += camera_offset_changex
    camera_offsety += camera_offset_changey
    pygame.display.update()


