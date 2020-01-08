import random, pickle, pygame, math, sys, traceback

pygame.init()
window_x = pygame.display.Info().current_w
window_y = pygame.display.Info().current_h
screen_origin_x = int(window_x/2)
screen_origin_y = int(window_y/2)

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
render_space = {}
text_space = {}
load = 0

map_x_width = 0
map_y_width = 0
static = False
selector = 2
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
tile_set = {}
game_status = 0
font_default = pygame.font.SysFont('Arial', 30)
font_title = pygame.font.SysFont('Arial', 60)


ent_sprite_set = {}
def tile_load():
    for i in range (1, 5):
        tile_set[i] = pygame.image.load("resources/tiles/tile_grass%s.png" %(i))
        tile_set[i] = pygame.transform.scale(tile_set[i],(tile_size, tile_size))
   
def ent_sprite_load():
    x=1
    ent_sprite_set[x] = pygame.image.load("resources/player.png")
    ent_sprite_set[x] = pygame.transform.scale(ent_sprite_set[x],(tile_size, tile_size))
    for ent in range(1,len(master_entity_table)+1):
        master_entity_table[ent].image = ent_sprite_set[x]
        
        
tile_load()
ent_sprite_load()

class Tile():
    def __init__(self, worldX, worldY):
        global tile_set
        self.worldX = worldX
        self.worldY = worldY
        self.inventory = list()
        self.ents = list()
        self.environment = ""
        self.randomvar = random.randint(1,4)
        self.check_passable()
        self.image = tile_set[self.randomvar]
        
    def renderTile(self):
        global screen_origin_x
        global screen_origin_y
        global tile_size
        self.screenx = screen_origin_x+(self.worldX*tile_size)+(player_x_offset*tile_size)+camera_offsetx
        self.screeny = screen_origin_y+(self.worldY*tile_size)+(player_y_offset*tile_size)+camera_offsety
        screen.blit(self.image,(self.screenx, self.screeny))
        
    def check_passable(self):
        if self.randomvar == 4:
            self.is_passable = False

        else:
            self.is_passable = True
            
            
class Entity():
    def __init__(self, worldX, worldY, image_id):
        self.worldX = worldX
        self.worldY = worldY
        self.inventory = list()
        self.hp = 100
        self.accessTile(self.worldX, self.worldY).ents.append(self)
        self.occupied_tile = self.accessTile(self.worldX, self.worldY)
        master_entity_table[len(master_entity_table)+1] = self
        self.image = ent_sprite_set[image_id]

    def entSetPos(self, x, y):
        self.worldX = x
        self.worldY = y

    def entMove(self, xChange, yChange):
        new_x = self.worldX + xChange
        new_y = self.worldY + yChange
        coords = (self.accessTile(new_x, new_y).worldX, self.accessTile(new_x, new_y).worldY)
        if self.accessTile(new_x, new_y).is_passable == True:
            self.occupied_tile.ents.remove(self)
            self.worldX = new_x
            self.worldY = new_y
            self.occupied_tile = self.accessTile(self.worldX, self.worldY)
            self.accessTile(self.worldX, self.worldY).ents.append(self)
            print(self.accessTile(self.worldX, self.worldY).ents)
            print(self.occupied_tile)
        else:
            print("Tile is inaccessible.")
            pass
        
    def accessTile(self, x, y):
        global master_tile_table
        return(master_tile_table[x][y])
        
    def renderEnt(self):
        global screen_origin_x
        global screen_origin_y
        global tile_size
        self.screenx = screen_origin_x+(self.worldX*tile_size)+(player_x_offset*tile_size)+camera_offsetx
        self.screeny = screen_origin_y+(self.worldY*tile_size)+(player_y_offset*tile_size)+camera_offsety
        if self.screenx > window_x+256 or self.screeny > window_y+256:
            pass
        else:
            screen.blit(self.image,(self.screenx, self.screeny))
        
class Player(Entity):
    def __init__(self, worldX, worldY, image_id):
        super().__init__(worldX, worldY, image_id)
        self.last_unloaded_pos_x = self.worldX
        self.last_unloaded_pos_y = self.worldY
        self.old_unloaded_pos_x = self.worldX
        self.old_unloaded_pos_y = self.worldY
            
    def entMove(self, xChange, yChange):
        new_x = self.worldX + xChange
        new_y = self.worldY + yChange
        coords = (self.accessTile(new_x, new_y).worldX, self.accessTile(new_x, new_y).worldY)
        if self.accessTile(new_x, new_y).is_passable == True:
            self.occupied_tile.ents.remove(self)
            self.worldX = new_x
            self.worldY = new_y
            self.occupied_tile = self.accessTile(self.worldX, self.worldY)
            self.accessTile(self.worldX, self.worldY).ents.append(self)
            print(self.accessTile(self.worldX, self.worldY).ents)
            global static
            if static == False:
                global player_x_offset
                global player_y_offset
                player_x_offset = -self.worldX
                player_y_offset = -self.worldY
        else:
            print("Tile is inaccessible.")
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
        screen.blit(self.image,(self.screenx, self.screeny))

    
        
class Item():
    def __init__(self):
        self.id = 1

class Button():
    def __init__(self, pos_x, pos_y, size_x, size_y, R,G,B, text, func_name, args):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.size_x = size_x
        self.size_y = size_y
        self.collision = pygame.Rect(pos_x, pos_y, size_x, size_y)
        self.collision.center = (pos_x, pos_y)
        self.color = [R,G,B]
        self.default_color = [R,G,B]
        self.text = text
        self.font = font_default
        self.func_name = func_name
        self.args = args

    def render_text(self):
        text_surf = self.font.render(self.text, False, (0, 0, 0))
        screen.blit(text_surf, (self.pos_x - text_surf.get_width() // 2, self.pos_y - text_surf.get_height() // 2))

    def clicked(self):
        #globals()["%s" %self.func_name]()
        if self.args == "":
            getattr(sys.modules[__name__], "%s" %self.func_name)()
        else:
            getattr(sys.modules[__name__], "%s" %self.func_name)(self.args)
        
        
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



        
def tileGen(sizeX, sizeY):
    global master_tile_table
    global tileID
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
    with open('map_data.pkl', 'rb') as input:
        master_tile_table = pickle.load(input)    
    searchrange = int(len(master_tile_table)/2)    
    for x in range(-searchrange, searchrange):
        for y in range(-searchrange, searchrange):
            global tile_set
            openTile = master_tile_table[x][y]
            openTile.image = tile_set[openTile.randomvar]

def saveData():
    global master_tile_table
    searchrange = int(len(master_tile_table)/2)
    for x in range(-searchrange, searchrange):
        for y in range(-searchrange, searchrange):
            openTile = master_tile_table[x][y]
            openTile.image = ""
            
    with open('map_data.pkl', 'wb') as output:
        pickle.dump(masterTileTable, output, pickle.HIGHEST_PROTOCOL) 

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
                open_tile = master_tile_table[x][y]
                dist = math.hypot(open_tile.worldX - player.occupied_tile.worldX, open_tile.worldY - player.occupied_tile.worldY)
                unloaded_tile_table[x][y] = master_tile_table[x][y]
                del master_tile_table[x][y]
            except:
                pass
    player.last_unloaded_pos_x = player.occupied_tile.worldX
    player.last_unloaded_pos_y = player.occupied_tile.worldY
    print("Tiles unloaded")

def load_all_tiles():
    for x in unloaded_tile_table:
        for y in unloaded_tile_table:
            try:
                open_tile = unloaded_tile_table[x][y]
                dist = math.hypot(open_tile.worldX - player.occupied_tile.worldX, open_tile.worldY - player.occupied_tile.worldY)
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
    

def button_render():
    try:
        for button in render_space:
            pygame.draw.rect(screen, render_space[button].color, render_space[button].collision)
            render_space[button].render_text()
    except(RuntimeError):
        return
    except:
        pass

def text_render():
    try:
        for text in text_space:
            text_space[text].render()
    except:
        pass

def render_clear():
    render_space.clear()
    text_space.clear()

def start_menu():
    global game_status
    game_clean()
    game_status = 0
    render_clear()
    start_button = Button(screen_origin_x, screen_origin_y/2, screen_origin_x/2, screen_origin_x/16, 255, 0, 0, "Start", "load_game", "")
    load_button =  Button(screen_origin_x, screen_origin_y/2+100, screen_origin_x/2, screen_origin_x/16, 255, 0, 0, "Load", "", "")
    options_button =  Button(screen_origin_x, screen_origin_y/2+200, screen_origin_x/2, screen_origin_x/16, 255, 0, 0, "Options", "options_menu", "" )
    quit_button =  Button(screen_origin_x, screen_origin_y/2+300, screen_origin_x/2, screen_origin_x/16, 255, 0, 0, "Quit", "quit_game", "" )
    render_space[1] = start_button
    render_space[2] = load_button
    render_space[3] = options_button
    render_space[4] = quit_button
    title = Text(screen_origin_x, screen_origin_y/2-100, "Cool Test Game", 5)
    text_space[1] = title
    bg = Image("resources/title_bg.png", window_x, window_y, screen_origin_x, screen_origin_y)
    text_space[2] = bg

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
    map_options_button = Button(screen_origin_x, screen_origin_y/2, screen_origin_x/2, screen_origin_x/16, 255, 0, 0, "Map Size", "map_options_menu", "")
    render_space[1] = map_options_button
    title = Text(screen_origin_x, screen_origin_y/2-100, "Options", 5)
    back =  Button(screen_origin_x, screen_origin_y/2+600, screen_origin_x/4, screen_origin_x/16, 255, 0, 0, "Back", "start_menu", "")
    text_space[1] = title
    render_space[2] = back
    pygame.mouse.set_visible(True)

def map_options_menu():
    render_clear()
    func = "set_map_size"
    
    title = Text(screen_origin_x, screen_origin_y/2-100, "Map Size", 5)
    map_size_50 = Button(screen_origin_x, screen_origin_y/2, screen_origin_x/4, screen_origin_x/16, 255, 0, 0, "50x50", "set_map_size", 50)
    map_size_100 =  Button(screen_origin_x, screen_origin_y/2+100, screen_origin_x/4, screen_origin_x/16, 255, 0, 0, "100x100", "set_map_size", 100)
    map_size_200 =  Button(screen_origin_x, screen_origin_y/2+200, screen_origin_x/4, screen_origin_x/16, 255, 0, 0, "200x200", "set_map_size", 200)
    back =  Button(screen_origin_x, screen_origin_y/2+600, screen_origin_x/4, screen_origin_x/16, 255, 0, 0, "Back", "options_menu", "")
    render_space[1] = map_size_50
    render_space[2] = map_size_100
    render_space[3] = map_size_200
    render_space[4] = back
    text_space[1] = title
    pygame.mouse.set_visible(True)    

def resume_game():
    global game_status
    render_clear()
    game_status = 1
    pygame.mouse.set_visible(False)

def game_start():
    global start_game
    start_game = True
    tileGen(map_x_width, map_y_width)
    global player
    global enemy
    pygame.mouse.set_visible(False)
    player = Player(0,0,1)
    enemy = Entity(4,0,1)
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
    screen.fill((255,255,255))
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
                    player.entMove(0,0)
                    camera_offsetx = 0
                    camera_offsety = 0

                if event.key == pygame.K_f:
                    unload_tiles()

                if event.key == pygame.K_r:
                    load_tiles()

                if event.key == pygame.K_l:
                    map_gen()

                if event.key == pygame.K_o:
                    load_all_tiles()

                if event.key == pygame.K_p:
                    print(player.occupied_tile.image)

                if event.key == pygame.K_x:
                    try:
                        selector += 1
                        tile_size = tile_sizes[selector]
                        print(tile_size)
                        tile_load()
                        ent_sprite_load()
                        reload_tile_image()
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
                        tile_load()
                        ent_sprite_load()
                        reload_tile_image()
                        load_tiles()
                        render_screen()
                    except:
                        pass
                        print("Key error!")
                    

                if event.key == pygame.K_ESCAPE:
                    pause_menu()
                    
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

        if game_status == 0 or 2:
            if event.type == pygame.MOUSEBUTTONDOWN:
                for button in list(render_space):
                    try:
                        if render_space[button].collision.collidepoint(event.pos):
                            render_space[button].clicked()
                    except:
                        traceback.print_exc()
                        pass
                
        
            if event.type == pygame.MOUSEMOTION:
                for button in list(render_space):
                    if render_space[button].collision.collidepoint(pygame.mouse.get_pos()):
                        render_space[button].color = [0, 255, 0]
                    else:
                        render_space[button].color =  render_space[button].default_color

    if game_status != 0:     
        render_screen()
    
    text_render()
    button_render()
    camera_offsetx += camera_offset_changex
    camera_offsety += camera_offset_changey
    pygame.display.update()


