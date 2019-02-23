import os
import sys
import pygame
import time
import random
import collections
import sqlite3
from PIL import Image

__author__ = "Ahmet Tolga Erdönmez"
__version__ = "1.0"

# initiliazing pygame
pygame.init()

class init_database:
    def __init__(self):
        try:
            dir_path = '%s\\Race\\' %  os.environ['APPDATA']
        except:
            dir_path = os.getcwd()
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        file_path = '%splayer.db' % dir_path
        self.connection = sqlite3.connect(file_path)
        self.cursor = self.connection.cursor()
        try:
            self.cursor.execute('CREATE TABLE player (points REAL,unlocks TEXT,last REAL)')
            self.cursor.execute('INSERT INTO player Values(10,1,1)')
        except:
            pass
        self.connection.commit()

    # getting points from database
    def get_points(self):
        self.cursor.execute('SELECT points FROM player')
        return self.cursor.fetchall()[0][0]
    
    # getting the car indexes that player have unlocked 
    def get_unlocks(self):
        self.cursor.execute('SELECT unlocks FROM player')
        unlocks = self.cursor.fetchall()
        return unlocks[0][0].split(',')

    # first adding the old points to current collected points then write it to database
    def add_points(self,new):
        self.cursor.execute('UPDATE player SET points = ? WHERE points = ?',(new + self.get_points(),self.get_points()))
        self.connection.commit()

    #adding unlocked car indexes as a string looks like a list like:
        # "1,2,3,4" is a string but seems like list
    def add_unlock(self,index):
        #converting lists to a text seems like a list
        news_list = self.get_unlocks()
        news_text = str()
        news_list.append(str(index))

        olds_list = self.get_unlocks()
        olds_text = str()

        for i in news_list:
            news_text += i + ','
        news_text = news_text.strip(',')

        for i in olds_list:
            olds_text += i + ','
        olds_text = olds_text.strip(',')


        self.cursor.execute('UPDATE player SET unlocks = ? WHERE unlocks = ?',(news_text,olds_text) )
        self.connection.commit()

    #getting the last used car 
    def get_current(self):
        self.cursor.execute('SELECT last FROM player')
        last = self.cursor.fetchall()
        return int(last[0][0])

    #setting the last used car type to database
    def set_car_type(self,index):
        self.cursor.execute('UPDATE player SET last = ?',(index,))
        self.connection.commit()

    # resetting the database
    def reset(self):
        self.cursor.execute('UPDATE player SET points = 0, unlocks = 1')

class game_car:
    def __init__(self, window, speed):
        self.x = window.width * 0.45
        self.y = window.height * 0.8
        self.speed = speed
        self.x_change = 0
        self.type = 1
        self.width, self.height = Image.open('Img/Char/car' + str(self.type) + '.png').size

    #draws the car onto screen using current car type
    def draw(self, window):
        self.img = pygame.image.load('Img/Char/car' + str(self.type) + '.png')
        window.blit(self.img, (self.x, self.y))

    #resets car's position
    def reset_pos(self, window):
        self.x = window.width * 0.45
        self.y = window.height * 0.8
        self.speed = 5

##class block:
##    def __init__(self, x, y, w, h, color, speed):
##        self.x = x
##        self.y = y
##        self.width = w
##        self.height = h
##        self.color = color
##        self.speed = speed
##
##    #draws the block onto screen
##    def draw(self, window):
##        pygame.draw.rect(window, self.color, (self.x, self.y, self.width, self.height))

class particle:
    def __init__(self, img, x, y, color, speed, action=None, way=None,dir = 'Particles'):

        self.img = pygame.image.load('Img/'+dir+'/{}'.format(img))
        self.x = x
        self.y = y
        self.width, self.height = Image.open('Img/'+dir+'/{}'.format(img)).size
        self.color = color
        self.speed = speed
        self.action = action
        self.way = way
        self.x_change = 0

    #drawing particles like bomb arrows etc.
    def draw(self, window):
        window.blit(self.img, (self.x, self.y))
    
    def random(self, part_type, part_color):
        self.img = pygame.image.load('Img/Particles/{}'.format(part_type))
        self.color = part_color

    # moving the particles by adding the game_speed
    def move(self, game_speed):
        if self.way == '-':
            self.x_change = -game_speed
        elif self.way == '+':
            self.x_change = game_speed
        self.x += self.x_change

class button:
    def __init__(self, window, text, x, y, width, height, normalc, hoverc, action=None):
        self.window = window
        self.text = text
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.normalc = normalc
        self.hoverc = hoverc
        self.action = action
        self.rect = pygame.Rect(self.x,self.y,self.width,self.height)
        click_sound = pygame.mixer.Sound('Sounds/button_clicked.wav')
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        # if self.x + self.width > mouse[0] > self.x and self.y + self.height > mouse[1] > self.y:
        #     pygame.draw.rect(self.window.display, hoverc, (self.x, self.y, self.width, self.height))
        if self.rect.collidepoint(mouse):
            pygame.draw.rect(self.window.display, hoverc, self.rect)
            if click[0] == 1 and action is not None:
                pygame.mixer.Sound.play(click_sound)
                time.sleep(0.2)
                try:
                    action(self.normalc)
                except:
                    action()
        else:
            pygame.draw.rect(self.window.display, normalc, self.rect)

        smallText = pygame.font.Font(fonts['roboto_medium'], 20)
        textSurf, textRect = self.window.text_objects(self.text, smallText, black)
        textRect.center = ((self.x + (self.width / 2)), (self.y + (self.height / 2)))
        self.window.display.blit(textSurf, textRect)

class switch_button:
    def __init__(self, window, text, x, y, width, height, normalc, hoverc):
        self.window = window
        self.text = text
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.normalc = normalc
        self.hoverc = hoverc
        #when button clicked become Truete
        smallText = pygame.font.Font(fonts['roboto_medium'], 20)
        click_sound = pygame.mixer.Sound('Sounds/button_clicked.wav')

        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        clicked = False
        if self.x + self.width > mouse[0] > self.x and self.y + self.height > mouse[1] > self.y:

            pygame.draw.rect(self.window.display, hoverc, (self.x, self.y, self.width, self.height))
            if click[0] == 1 and not clicked:
                clicked = True
                # pygame.mixer.Sound.play(click_sound)
                if window.bg_state == "OFF":
                    window.bg_state = "ON"
                elif window.bg_state == "ON":
                    window.bg_state = "OFF"
                pygame.mixer.Sound.play(click_sound)
                time.sleep(0.2)
        else:
            clicked = False
            pygame.draw.rect(self.window.display, normalc, (self.x, self.y, self.width, self.height))


        textSurf, textRect = self.window.text_objects(self.text + ': ' + window.bg_state, smallText, black)
        textRect.center = ((self.x + (self.width / 2)), (self.y + (self.height / 2)))
        self.window.display.blit(textSurf, textRect)

class showcase_car:
    def __init__(self, window, img, x, y, price):
        self.window = window
        self.img = pygame.image.load(img)
        self.lock = pygame.image.load('Img/Char/locked2.png')
        self.selected = pygame.image.load('Img/Char/selected.png')
        self.x = x
        self.y = y
        self.status = False
        self.price = price
        self.width, self.height = Image.open(img).size
        self.rect = pygame.Rect(self.x,self.y,self.width,self.height)


    def draw(self,window):
        window.display.blit(self.img,(self.x,self.y))
        if not self.status:
            window.display.blit(self.lock, (self.x, self.y))

class display:
    def __init__(self, w, h):

        self.width = w
        self.height = h
        self.display = pygame.display.set_mode((self.width, self.height))
        self.paused = False
        self.bg_img = pygame.image.load('Img/Bg/road2.png').convert()
        self.bg_y = -600
        self.bg_state = 'ON'

        self.db = init_database()


        pygame.display.set_caption('Race')
        pygame.display.set_icon(pygame.image.load('Img/icon.png'))

    def draw_bg(self, game_speed):

        if self.bg_y > 0:
            self.bg_y = -600
        self.bg_y += game_speed
        self.display.blit(self.bg_img, (0, self.bg_y))

    def text_objects(self, text, font, color):
        textSurface = font.render(text, True, color)
        return textSurface, textSurface.get_rect()

    def message_display(self, text, second):
        largeText = pygame.font.Font(fonts['roboto_black'], 100)
        TextSurf, TextRect = self.text_objects(text, largeText, red)
        TextRect.center = ((self.width / 2), (self.height / 2))
        self.display.blit(TextSurf, TextRect)
        pygame.display.update()
        time.sleep(second)

    def crash(self, level, points):
        pygame.mixer.music.stop()
        pygame.mixer.Sound.play(crash_sound)
        y = self.height / 2 - 100
        written = 1
        while True:
            largeText = pygame.font.Font(fonts['roboto_black'], 50)
            for i in ['Game Over !', 'Your Score: {}'.format(points), 'You lost in wave: {}'.format(level)]:
                if written <= 3:
                    TextSurf, TextRect = self.text_objects(i, largeText, black)
                    TextRect.center = ((self.width / 2), (y))
                    self.display.blit(TextSurf, TextRect)
                    y += 50
                    written += 1
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    try:
                        quit()
                    except:
                        sys.exit()

            replay_btn = button(self, 'Replay!', 180, 450, 100, 50, green, bright_green, game_loop)
            mainmenu_btn = button(self, 'Main Menu', 330, 450, 150, 50, blue, bright_blue, self.game_intro)
            quit_btn = button(self, 'QUIT!', 530, 450, 100, 50, red, bright_red, self.quit_game)

            pygame.display.update()
            clock.tick(15)

    def quit_game(self):
        pygame.quit()
        try:
            quit()
        except:
            sys.exit()

    def unpause_game(self):
        click_sound = pygame.mixer.Sound('Sounds/button_clicked.wav')
        self.paused = False
        i = 3
        while True:
            if i == 0:
                break
            self.display.fill(white)
            if i != 3:
                pygame.mixer.Sound.play(click_sound)
            self.message_display(str(i), 1)
            pygame.display.update()
            clock.tick(1)
            i -= 1

    def pause_game(self):
        while self.paused:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    try:
                        quit()
                    except:
                        sys.exit()
            self.display.fill(white)
            largeText = pygame.font.Font(fonts['roboto_black'], 100)
            TextSurf, TextRect = self.text_objects('Paused !', largeText, black)
            TextRect.center = ((self.width / 2), (self.height / 2))
            self.display.blit(TextSurf, TextRect)
            # buttons
            # object --> button(window,text, x, y, width, height, normalc, hoverc, action = None)
            resume_btn = button(self, 'Resume!', 150, 450, 100, 50, green, bright_green, self.unpause_game)
            if self.paused == False:
                break
            replay_btn = button(self, 'Replay!', 350, 450, 100, 50, blue, bright_blue, game_loop)
            quit_btn = button(self, 'QUIT!', 550, 450, 100, 50, red, bright_red, self.quit_game)
            setting_btn = button(self, 'SETTINGS', 240, 520, 150, 50, blue, bright_blue, self.settings)
            mainmenu_btn = button(self, 'Main Menu', 410, 520, 150, 50, blue, bright_blue, self.game_intro)
            pygame.display.update()
            clock.tick(15)

    def back_home(self):
        self.in_settings = False

    def stop_asking(self,color):
        self.asking = False
        if color == green:
            self.cur_answer = True
        elif color == red:
            self.cur_answer = False

    def settings(self):
        self.in_settings = True
        while self.in_settings:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    try:
                        quit()
                    except:
                        sys.exit()

            self.display.fill(white)
            #SETTING HEADER
            largeText = pygame.font.Font(fonts['roboto_black'], 100)
            TextSurf, TextRect = self.text_objects('Settings', largeText, black)
            TextRect.center = ((self.width / 2), (self.height / 5))
            self.display.blit(TextSurf, TextRect)
            #BUTTONS
            road_btn = switch_button(self, 'Road Bg',300,250,200,50,green,bright_green)
            back_home = button(self,'Back',350,500,100,50,red,bright_red,self.back_home)
            reset_game = button(self, 'Reset Game', 300, 350, 200, 50, red, bright_red,self.db.reset)
            pygame.display.update()
            clock.tick(30)

    # writes whatever you want to top left
    def game_status(self, *args, **kwargs):
        kwargs = collections.OrderedDict(sorted(kwargs.items()))
        y = 3
        font = pygame.font.Font(fonts['roboto_medium'], 20)
        color_count = 0
        for i, j in kwargs.items():
            text = font.render(i[1:] + ': ' + str(j), True, args[color_count])
            self.display.blit(text, (3, y))
            y += 25
            color_count += 1

    def ask_yes_no(self):
        self.asking = True
        while self.asking:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
            pygame.draw.rect(self.display,black,(200,100,400,200))

            largeText = pygame.font.Font(fonts['roboto_black'], 40)
            TextSurf, TextRect = self.text_objects('Are you sure ?', largeText, white)
            TextRect.center = (400,150)
            self.display.blit(TextSurf, TextRect)

            #YES NO BUTTONS
            yes = button(self, 'YES', 270, 210, 100, 50, green, bright_green, self.stop_asking)
            no = button(self, 'NO', 420, 210, 100, 50, red, bright_red, self.stop_asking)

            pygame.display.update()
            clock.tick(30)

    def warning(self):
        self.asking = True
        while self.asking:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
            pygame.draw.rect(self.display,black,(170,100,470,200))

            largeText = pygame.font.Font(fonts['roboto_black'], 35)
            TextSurf, TextRect = self.text_objects("You can't afford this car :(", largeText, white)
            TextRect.center = (400,150)
            self.display.blit(TextSurf, TextRect)

            okay = button(self, 'OKAY', 350, 210, 100, 50, (0,235,0), bright_green, self.stop_asking)

            pygame.display.update()
            clock.tick(30)

    def customize(self):
        car_selected_sound = pygame.mixer.Sound('Sounds/car_selected.wav')
        #creating car imgs
        cars = dict()
        x = self.width / 5 + 15
        y = self.height / 3
        unlocks = self.db.get_unlocks()
        cur_price = 10
        self.cur_answer = False
        for count in range(1,11):
            if count == 6:
                y += 160
                x = self.width / 5 + 15
            if count == 5:
                cur_price = 20
            if count == 8:
                cur_price = 30
            car = showcase_car(self, 'Img/Char/car' + str(count) + '.png', x, y, cur_price)
            cars[count] = car
            x += 100
        for z in unlocks:

            cars[int(z)].status = True
        #will be the index number of the car that we clicked

        self.in_settings = True
        while self.in_settings:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for i,cur_car in cars.items():
                        if cur_car.rect.collidepoint(event.pos) and event.button == 1:
                            if cur_car.status:
                                self.db.set_car_type(i)

                                pygame.mixer.music.stop()
                                pygame.mixer.Sound.play(car_selected_sound)
                            else:
                                #asking the user permission to buy the car
                                time.sleep(0.3)
                                self.ask_yes_no()
                                if self.cur_answer:
                                    if self.db.get_points() - cur_car.price < 0:
                                        self.warning()
                                    else:
                                        self.db.add_points(-cur_car.price)
                                        self.db.add_unlock(i)
                                        cur_car.status = True

            self.display.fill(white)
            #SETTING HEADER
            largeText = pygame.font.Font(fonts['roboto_black'], 65)
            largeText1 = pygame.font.Font(fonts['roboto_black'], 40)
            TextSurf, TextRect = self.text_objects('CUSTOMIZE YOUR CAR !', largeText, black)
            TextRect.center = ((self.width / 2), (self.height / 7))

            TextSurf1, TextRect1 = self.text_objects('Your Points: ' + str(int(self.db.get_points())), largeText1, black)
            TextRect1.center = ((self.width / 2), (self.height / 4))

            self.display.blit(TextSurf, TextRect)
            self.display.blit(TextSurf1, TextRect1)

            for i,j in cars.items():
                j.draw(gameDisplay)
                if not j.status:
                    largeText = pygame.font.Font(fonts['roboto_black'], 15)
                    TextSurf, TextRect = self.text_objects(str(j.price) + 'Pts', largeText, black)
                    TextRect.center = (j.x + 25,(j.y + j.height + 20))
                    self.display.blit(TextSurf, TextRect)

            selected_car = cars[self.db.get_current()]
            self.display.blit(selected_car.selected, (selected_car.x, selected_car.y))

            #BUTTONS
            back_home = button(self,'Back',350,520,100,50,red,bright_red,self.back_home)

            pygame.display.update()
            clock.tick(60)

    def game_intro(self):

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    try:
                        quit()
                    except:
                        sys.exit()
            self.display.fill(white)
            largeText = pygame.font.Font(fonts['roboto_black'], 100)
            smallText = pygame.font.Font(fonts['roboto_medium'], 25)
            TextSurf, TextRect = self.text_objects('Race !', largeText, black)
            TextRect.center = ((self.width / 2), (self.height / 3))
            self.display.blit(TextSurf, TextRect)
            TextSurf2, TextRect2 = self.text_objects('by Tolga Erdonmez', smallText, black)
            TextRect2.center = ((self.width / 2), (self.height / 6 * 5.5))
            self.display.blit(TextSurf2, TextRect2)
            # buttons
            # object --> button(window,text, x, y, width, height, normalc, hoverc, action = None)

            go_btn = button(self, 'GO!', 350, 300, 100, 50, green, bright_green, game_loop)
            quit_btn = button(self, 'QUIT!', 350, 375, 100, 50, red, bright_red, self.quit_game)
            setting_btn = button(self, 'SETTINGS', 410, 450, 150 ,50, blue, bright_blue, self.settings)
            customize_btn = button(self, 'CUSTOMIZE !',250,450,150,50,blue,bright_blue,self.customize)
            pygame.display.update()
            clock.tick(15)

    def lives(self,left):
        x = 3
        y = 105
        for i in range(left):
            lives = particle('heart.png', x, y, None, 0)
            lives.draw(gameDisplay.display)
            x += 42

# FONTS
fonts = {'roboto_black': 'Fonts/Roboto-Black_0.ttf', 'roboto_medium': 'Fonts/Roboto-Medium_0.ttf'}

# SOUNDS
crash_sound = pygame.mixer.Sound('Sounds/crash.wav')
score_sound = pygame.mixer.Sound('Sounds/point.wav')
wave_sound = pygame.mixer.Sound('Sounds/next_wave.wav')
speedup_sound = pygame.mixer.Sound('Sounds/speed.wav')
slowdown_sound = pygame.mixer.Sound('Sounds/slow.wav')
tyre_wheep_sound = pygame.mixer.Sound('Sounds/tyre.wav')

# COLORS
black = (0, 0, 0)
white = (255, 255, 255)
red = (200, 0, 0)
bright_red = (240, 0, 0)
blue = (0, 0, 220)
bright_blue = (0, 0, 255)
green = (0, 200, 0)
bright_green = (0, 240, 0)
color_palette = [white, black, red, green, blue]

# SETTING CLOCK
clock = pygame.time.Clock()

# CREATING DISPLAY
gameDisplay = display(800, 600)

# SETTING FPS
fps = 60

# CREATING CAR
car = game_car(gameDisplay, 5)

def game_loop():
    # setting speed of the game
    game_speed = 7
    # points
    cur_points = 0
    # setting level
    level = 1
    # reseting car's position and setting the current car tpye
    car.reset_pos(gameDisplay)
    car.type = gameDisplay.db.get_current()
    #setting players lives
    lives = 3

    # PARTICLE OPTIONS
    particle_amount = 4
    particles = dict()
    set_particle = False
    particles_added = False
    part_types = {'bomb.png': black, 'point.png': green, 'point.png': green, 'speed.png': blue, 'slow.png': red}
    part_type_list = list()
    for i, j in part_types.items():
        part_type_list.append(i)

    gameExit = False
    # The first parameter delay is the number of milliseconds before the first repeated pygame.KEYDOWN will be sent.
    # After that another pygame.KEYDOWN will be sent every interval milliseconds. If no arguments are passed
    # the key repeat is disabled.

    pygame.key.set_repeat(5,5)
    while not gameExit:

        # KEY EVENTS & QUITTING
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                try:
                    quit()
                except:
                    sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    car.x_change = -car.speed
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    car.x_change = car.speed
                elif event.key == pygame.K_SPACE:
                    car.x_change = 0
                    gameDisplay.paused = True
                    gameDisplay.pause_game()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT or event.key == pygame.K_a or event.key == pygame.K_d:
                    car.x_change = 0

        # LOOKING IF THE PLAYER IS OUT OF LIVES if out of CRASHES THE GAME
        if lives == 0:
            car.x_change = 0
            gameDisplay.db.add_points(cur_points)
            gameDisplay.crash(level, cur_points)

        #DRAWING OBJECTS

        # setting background
        if gameDisplay.bg_state == "ON":
            gameDisplay.draw_bg(game_speed)
        else:
            gameDisplay.display.fill((56, 56, 56))

        # drawing particles
        if not set_particle or (cur_points % 10 == 0 and cur_points > 0 and particles_added):
            for x in range(particle_amount):
                cur_x = random.randrange(0, gameDisplay.width)
                cur_y = random.randrange(-700, -500)

                # picks a random particle
                cur_type = part_type_list[random.randrange(len(part_type_list))]
                cur_color = part_types[cur_type]
                cur_action = None
                cur_way = None
                # gives bomb particles moving action and the way of the moving action
                if cur_color == black:
                    cur_action = 'exist'
                    if cur_x < (gameDisplay.width / 3):
                        cur_way = '+'
                    elif cur_x > (gameDisplay.width / 3):
                        cur_way = '-'

                particles[x] = particle(cur_type, cur_x, cur_y, cur_color, game_speed, cur_action, cur_way)
            set_particle = True
            particles_added = False
        else:
            for x, cur_part in particles.items():
                # detects if particles go out from display
                if cur_part.y > gameDisplay.height + cur_part.height:
                    cur_part.y = -cur_part.height * 1.2
                    cur_part.x = random.randrange(0, gameDisplay.width)
                    new_type = part_type_list[random.randrange(len(part_type_list))]
                    cur_part.random(new_type, part_types[new_type])
                cur_part.y += cur_part.speed
                cur_part.draw(gameDisplay.display)
        for x, cur_part in particles.items():
            if cur_part.color == black and car.y - cur_part.y < 350 and level > 1:
                cur_part.move(game_speed)
                cur_part.draw(gameDisplay.display)
        # drawing CAR
        if car.x > gameDisplay.width - car.width:
            car.x = 0
        elif car.x < 0:
            car.x = gameDisplay.width - car.width
        car.x += car.x_change
        car.draw(gameDisplay.display)

        # DETECTING THAT IF CAR HITS A PARTICLE OR GOES NEAR PARTICLE
        for x, cur_part in particles.items():
            # if ((car.y >= cur_part.y and car.y <= cur_part.y + cur_part.height) or
            #     (cur_part.y <= car.y + car.height <= cur_part.y + cur_part.height)) and (
            #     (car.x >= cur_part.x and car.x <= cur_part.x + cur_part.width) or
            #     (car.x + car.width >= cur_part.x and car.x + car.width <= cur_part.x + cur_part.width)):
            if ((car.y >= cur_part.y and car.y <= cur_part.y + cur_part.height) or (cur_part.y >= car.y and cur_part.y <= car.y + car.height)) and (
                (car.x >= cur_part.x and car.x <= cur_part.x + cur_part.width) or (cur_part.x >= car.x and cur_part.x <= car.x + car.width)):
                # green scores a point
                if cur_part.color == green:
                    pygame.mixer.music.stop()
                    pygame.mixer.Sound.play(score_sound)
                    cur_part.y = gameDisplay.height + cur_part.height + 1
                    cur_points += 1
                    if cur_points % 3 == 0 and cur_points > 0 and game_speed < 15:
                        game_speed += 0.5
                    # next wave starts
                    elif cur_points % 10 == 0 and cur_points > 0:
                        # setting new particles
                        particle_amount += 2
                        particles_added = True
                        # playing next wave effects
                        gameDisplay.display.fill(white)
                        level += 1
                        pygame.mixer.music.stop()
                        pygame.mixer.Sound.play(wave_sound)
                        gameDisplay.message_display('Wave {} !'.format(level), 2)
                elif cur_part.color == blue:
                    pygame.mixer.music.stop()
                    pygame.mixer.Sound.play(speedup_sound)
                    cur_part.y = gameDisplay.height + cur_part.height + 1
                    if car.speed < 12:
                        car.speed += 0.5
                elif cur_part.color == red:
                    pygame.mixer.music.stop()
                    pygame.mixer.Sound.play(slowdown_sound)
                    cur_part.y = gameDisplay.height + cur_part.height + 1
                    car.speed -= 1.5
                    if car.speed < 3:
                        car.speed = 3
                elif cur_part.color == black:
                    # lives - 1
                    pygame.mixer.music.stop()
                    pygame.mixer.Sound.play(tyre_wheep_sound)
                    lives -= 1
                    cur_part.y = gameDisplay.height + cur_part.height + 1


        gameDisplay.game_status(white, white, white, white, aPoints=cur_points, bSpeed=car.speed, cWave=level,
                                dPause="SPACE")

        gameDisplay.lives(lives)


        pygame.display.update()
        clock.tick(fps)



if __name__ == '__main__':
    gameDisplay.game_intro()
    pygame.quit()
    quit()
