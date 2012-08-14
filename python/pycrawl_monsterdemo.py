# pycrawl_monsterdemo
# my very own rogulike game
# because i play far too much dungeon crawl stone soup
# 2012 by Horst JENS   horstjens@gmail.com
# license: gpl3 see http://www.gnu.org/copyleft/gpl.html
# this game is a part of http://ThePythonGameBook.com

# this is a demo where the player (@) runs around in some small rooms.
# monsters are randomly placed in the level and are also running around
# each tile (block) where the player stands should be saved and drawn again as soon as the player moves away

# 3 x 3 roooms with 8 x 8 tiles

import random


#ROOMROOT = 3
#BLOCKROOT = 6
rawlevel ="""\
XXXXXXXXXXXXXXXXXX
X.l........##....X
X......>...dd....X
Xtb....t..l##...>X
X.<........##..t.X
X..........##....X
X..........##....X
X...>......##....X
X..........##t.<.X
X..........dd....X
X..........##....X
X########d####d##X
X########d####d##X
X..........##...lX
X..b...<...##....X
X.s........##....X
X.t........##....X
XXXXXXXXXXXXXXXXXX\
"""



class Tile(object):
    """the level or map is made out of ascii tiles. the properties of the tiles are defined here"""
    tiledict = {} # a dict for all the different tiles
    def __init__(self, char, **kwargs):
        self.char = char
        self.text = ""
        #Tile.tileset.add(char) # put this new Tile into the tileset
        Tile.tiledict[char] = self # put this new Tile into the tiledict
        self.stepin = True # can the player step into this tile ? walls, fire etc: False
        #self.interact = False
        self.action = [] # possible actions on this tile
        self.description = "" # text to be displayed
        self.moveable = False
        self.monster = False
        self.blocksight = False # if the line of sight is blocked by this tile (like a wall) or not (like a trap or floor)
        self.attackable = False
        
        for attr in kwargs.keys(): 
            if attr in self.__dict__:
                self.__dict__[attr] = kwargs[attr]
                
    def showStats(object):
        """display all stats of an class instance"""
        for key in object.__dict__:
            print( key, ":", object.__dict__[key])

Tile("@", text="the player", description = "the player. that is you.", attackable = True, stepin = False, action = ["write grafitti"], blocksight=True)
Tile("X", text="an outer wall",  description = "an outer wall of the level. You can not go there", stepin = False, action = ["write grafitti"], blocksight=True)
Tile(".", text="an empty space", description = "an empty boring space. There is really nothing here.")
Tile("d", text="a door", description = "an (open) door", action=["open","close"])
Tile("m", text="a dead monster", description = "a dead monster. Did you kill it?", action=["eat","gather trophy"])
Tile("M", text="a living monster", attackable = True, stepin = False, monster=True, description = "a living monster. You can kill it. It can kill you !", action=["attack","feed","talk"])
Tile("z", text="a sleeping monster", monster=True, attackable = True, stepin = False, description = "a sleeping monster. You can kill it while it sleeps !", action=["attack","feed","talk"])
Tile("<", text="a stair up", description = "a stair up to the previous level", action = ["climb up"])
Tile(">", text="a stair down", description = "a stair down to the next deeper level", action = ["climb down"])
Tile("#", text="an inner wall", description = "an inner wall. You may destroy this wall with the right tools or spells", stepin = False, blocksight = True)
Tile("t", text="a trap", description = "a dangerous trap !", action = ["disarm", "destroy", "flag"])
Tile("l", text="a heap of loot", description = "a heap of loot. Sadly, not yet programmed. But feel yourself enriched", action=["pick up"])
Tile("b", text="a box", description = "a box. You wonder what is inside. And if it is trapped", action=["force open", "check for traps"])
Tile("s", text="a shop", descriptoin = "a shop of a friendly merchant", action=["go shopping"])



class Level(object):
    """the Level object is created with a map string and has elegant methods
    to get an specific tile (at position x,y) or set an specific tile or
    to return the whole level"""
    number = 0
    book = {}
    def __init__(self, level):
        Level.number += 1
        self.number = Level.number
        Level.book[self.number] = self # store itself into Level.book
        self.level_map = list(map(list, level.split()))

    def __getitem__(self, xy):
        """get the char at position x,y (x,y start with 0)"""
        x, y = xy
        return self.level_map[y][x] # row, col 

    def __setitem__(self, xy, item):
        """ x (col) and y (row) position of char to set. (x and y start with 0)"""
        x, y = xy
        self.level_map[y][x] = item # row, col

    def __iter__(self):
        """iterating over the lines of the level"""
        return ("".join(row) for row in self.level_map)

    def __str__(self):
        """calling __iter__ (row for row) to produce one big output string"""
        return "\n".join(row for row in self)

class MovingObject(object):
    """anything that moves, like a player, a monster or an arrow"""
    number = 0 # unique number for each  moving object
    book = {} # the big book of moving objects where each monster/player instance will be stored
    
    def __init__(self, char, x, y, levelnumber):
        """create moveable object"""
        MovingObject.number += 1                # get unique number from class variable
        self.number = MovingObject.number
        MovingObject.book[self.number] = self   # store yourself into class dict ( book )
        self.char = char
        self.x = x
        self.y = y
        self.levelnumber = levelnumber
        self.original = Level.book[self.levelnumber][self.x,self.y] # the char of the tile where i was standing on
        self.paint()
     
    def update(self):
        pass # this method is only here to be overwritten by child objects. 
        
    def clear(self):
        """clear myself and restore the original char of the level map on my position"""
        Level.book[self.levelnumber][self.x,self.y] = self.original
        
    def paint(self):
        Level.book[self.levelnumber][self.x,self.y] = self.char
        
    def checkmove(self, dx, dy):
        """test if moving into direction dx and dy is possible (not a wall). if yes, return True, else, return False"""
        if dx == 0 and dy == 0:
            #no move, that is always allowed:
            return True
        else:
            targetchar = Level.book[self.levelnumber][self.x + dx, self.y + dy] # the char where i want to go into (hopefully not a wall)
            if Tile.tiledict[targetchar].stepin: # allowed move
                return True
            else:
                return False
    
    def move(self, dx, dy):
        if dx == 0 and dy == 0:
            #no move, don't do anything
            return
        self.clear() # restore floor of old position
        self.x += dx
        self.y += dy
        self.original = Level.book[self.levelnumber][self.x,self.y] # save the char of the tile where i was standing on
        self.paint() # update level map with my new position
    
    
    
class Monster(MovingObject):
    """Monster class. monster have hitpoints and a state ( attack, roam, sleep, flee)"""
    #number = 0 # unique number for each monster
    #book = {} # the big book of monsters where each monster instance will be stored
    def __init__(self, char, x, y, levelnumber, **kwwargs):
        MovingObject.__init__(self, char, x, y, levelnumber) # calling parent object method)
        #self.char = char # char is already stored in MovingObject !
        self.shortname = "a monster"
        self.hitpoints = 10
        self.moods = ["sleep", "roam", "attack", "flee", "dead"]
        self.mood = random.choice(self.moods[0:2])
        self.sensorradius = 4 # aggro. how close the player must come to get the monster's attention
        self.energy = random.randint(1,100) # below 30, monster want to sleep, above 50, monster is awake
    
    def update(self):
        # loose hitpoints if on a trap
        if self.hitpoints <= 0:
            # monster is dead
            self.char = "m"
            self.dx = 0
            self.dy = 0
        else:
            # alive monster
            if self.original == "t":
                # i'm on a trap !
                self.hitpoints -= 1
                self.mood = "roam" # force roaming so that monster does not sleep on traps
                
            if self.mood == "sleep": # monster is sleeping
                self.char = "z"
                self.dx = 0
                self.dy = 0
                self.energy += 1 # sleeping regains energy
                if self.energy > 50:
                    self.mood = "roam"
            else:                     # monster is awake
                self.char = "M"
                while True:
                    self.dx = random.choice((-1,1)) 
                    self.dy = random.choice((-1,1))
                    if self.checkmove(self.dx, self.dy):
                        break
                self.move(self.dy, self.dy) # ???
                self.energy -= 1 # to be active makes the monster tired
                if self.energy < 30:
                    self.mood = "sleep" 

class Player(MovingObject):
    """The player is much like a monster also a moving object"""
    def __init__(self, char, x, y, levelnumber):
        MovingObject.__init__(self, char, x, y, levelnumber)
        # i'm sexy and i know it - all my core values like x, y are already stored in MovingObjects
        self.hitpoints = 100
            
    def update(self):    
        # change stats like hungry, healing etc here
        #pass # as none of that is coded i need at least a pass statement or the update method would not work
        if self.original == "t":
            # i'm on a trap !
            self.hitpoints -= 1
            
    
    def postext(self):
        return  "You (@) are at position %i, %i on %s with %i hitpoints. press:" % ( self.x, self.y, Tile.tiledict[self.original].text, self.hitpoints)
    
    def badmove(self, dx, dy):
        return "Bad idea! you can not walk into %s" % Tile.tiledict[Level.book[self.levelnumber][self.x + dx, self.y + dy]].text
    
    
def main():
    """ a demo to move the player in an ascii level map"""
    #print(' the "raw" level without player and monsters')
    #print(rawlevel)
    #print( " now the player comes into the level at pos row 9 col 9")
    firstlevel = Level(rawlevel) # creating the level from raw file
    # coordinates of player (x,y)
    player = Player("@", 14,14,1) # create the player
    # create 7 monsters:
    for littlemonster in range(7):
        # set random monsterpos and check if that is not a wall or a trap or the player pos
        monsterset = set()
        while True:
            x = random.randrange(1,18) # 0 is left outer wall, 18 is right outer wall
            y = random.randrange(1,18)
            if x == player.x and y== player.y:
                continue # no monster on top of player !
            if (x,y) in monsterset:
                continue # this position is taken by an monster already
            if firstlevel[x,y] in "X#t":
                continue # wall or trap
            monsterset.add((x,y))
            Monster("M",x,y,1) # create Monster
            print("i created Monster number %i at (%i,%i)" % (littlemonster, x, y))
            break
    
    
    
    print(firstlevel) # first time printing
    
    showtext = True # for inside the while loop
    while True: # game loop
        # output situation text
        #postext = player.postext()
        actions = Tile.tiledict[player.original].action # get the actionlist for this tile
        if len(actions) == 0:
            actiontext = "(no action possible)\n"
        else:
            actiontext = "for action: a and ENTER\n"
        # input
        inputtext = "to move (wait): numpad 84269713 (5) and ENTER\n" \
                  "%sto get more a more detailed description: d and ENTER\nto quit: q and ENTER] :" % actiontext
        if showtext: # avoid printing the whole text again for certain answers (action, description etc.)
            print(player.postext())
            print(inputtext)
        i = input(">")
        i = i.lower()
        if "q" in i:
            break
        elif i == "4" : # west
            dx = -1
            dy = 0
        elif i  =="6": # east
            dx = 1
            dy = 0
        elif i == "8": # north
            dx = 0
            dy = -1
        elif i == "2": #south
            dx = 0
            dy = 1
        elif i == "1": # south-west
            dx = -1
            dy = 1
        elif i == "7": # north-west
            dx = -1
            dy = -1
        elif i == "9": # north-east
            dx = 1
            dy = -1
        elif i =="3": # south-east
            dx = 1
            dy = 1
        elif i == "5": # wait
            dx = 0
            dy = 0

        # ------- non-moving actions ---------
        elif i == "d":
            showtext = False
            print("--------- more detailed description -------")
            print("This is",Tile.tiledict[original].description)
            print("------ ----- -------- --------- -----------")
            continue # go to the top of the while loop
        elif len(actions) > 0 and i =="a":
            showtext = False
            print("Those are the possible actions (not yet coded, you can only look at it:)")
            print("------ list of possible actions -------")
            for action in actions:
                print(actions.index(action), action)
            print("------ ----- -------- --------- -------")
            continue # go to the top of the while loop
        else:
            print("unknown input. please enter q for quit or numpad 84261379 for moving")
            continue
        # --------- move the player --------------
        if player.checkmove(dx,dy):
            player.move(dx,dy)
        else:
            print( player.badmove(dx,dy))
            showtext = False
            continue
        showtext = True
        # update (move) all moveableobjects (monsters)
        for mo in MovingObject.book.keys():
            Monster.book[mo].update()
        # output level
        print(firstlevel)
if __name__ == '__main__':
    main()
