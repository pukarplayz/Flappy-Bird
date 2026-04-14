import pygame
import random
import sys


#pygame Setup
pygame.init()
pygame.mixer.init()

score_sound = pygame.mixer.Sound("audio/point.wav")
death_sound = pygame.mixer.Sound("audio/die.wav")
wings_sound = pygame.mixer.Sound("audio/wing.wav")

score_sound.set_volume(0.5)
death_sound.set_volume(0.5)
wings_sound.set_volume(0.1)

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
clock = pygame.time.Clock()


#Textures
base = pygame.image.load("assets/base.png")
digits = [ 
    pygame.image.load("assets/0.png").convert_alpha(),
    pygame.image.load("assets/1.png").convert_alpha(),
    pygame.image.load("assets/2.png").convert_alpha(),
    pygame.image.load("assets/3.png").convert_alpha(),
    pygame.image.load("assets/4.png").convert_alpha(),
    pygame.image.load("assets/5.png").convert_alpha(),
    pygame.image.load("assets/6.png").convert_alpha(),
    pygame.image.load("assets/7.png").convert_alpha(),
    pygame.image.load("assets/8.png").convert_alpha(),
    pygame.image.load("assets/9.png").convert_alpha()
] 
gameover = pygame.image.load("assets/gameover.png").convert_alpha()
gameover_rect = gameover.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

#Bird Textures
bird_midflap = pygame.image.load("assets/yellowbird-midflap.png").convert_alpha()
bird_downflap = pygame.image.load("assets/yellowbird-downflap.png").convert_alpha()
bird_upflap = pygame.image.load("assets/yellowbird-upflap.png").convert_alpha()


#Backgrounds
day_background = pygame.transform.scale( pygame.image.load("assets/background-day.png").convert_alpha(), (1280,720) )
night_background = pygame.transform.scale(pygame.image.load("assets/background-night.png").convert_alpha(),(1280,720))

# pipes

pipe_list = []
pipe_gap = 200
pipe_speed = 300

PIPESPAWN = pygame.USEREVENT
pygame.time.set_timer(PIPESPAWN, 1200)

pipe_red = pygame.image.load("assets/pipe-red.png")
pipe_green = pygame.image.load("assets/pipe-green.png")

dt = 0
bird = bird_midflap.get_rect(center=(640,360))

# Timer
bg_timer = 0
bg_state = "day"

# Velocity
velocity_y = 0
gravity = random.randint(1000,1500)
jump_force = random.randint(-500,-300)

ground_y = 650

bird_frames = [bird_upflap,bird_midflap,bird_downflap]
bird_index = 0
bird_anim_timer = 0

# Score
score = 0
passed_pipes = set()


# Game State
START, PLAYING, GAMER_OVER = 0,1,2
state = START

def reset():
    global bird, velocity_y, pipe_list, score, passed_pipes , state
    bird.center = (300,360)
    velocity_y = 0
    pipe_list = []
    score = 0
    passed_pipes = set()
    state = PLAYING

def get_bird_rect():
    rect = bird.copy()
    rect.inflate_ip(-20,-20)
    return rect


while True:
    dt = clock.tick(60)/1000
    bg_timer += dt
        
    if bg_timer > 120:
        bg_state = "night" if bg_state == "day" else "day"
        bg_timer = 0
        
    
    #Event
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            
        if state == START:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                reset()
        elif state == PLAYING:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                velocity_y = jump_force
                wings_sound.play()
            # Pipe Event
            if event.type == PIPESPAWN:
                height = random.randint(180,500)
                
                top_pipe = pipe_green.get_rect(midbottom=(1400,height - pipe_gap // 2 ))
                bottom_pipe = pipe_green.get_rect(midtop=(1400,height + pipe_gap // 2 ))
                
                pipe_list.append({
                    "top": top_pipe,
                    "bottom": bottom_pipe,
                    "scored": False
                })
        elif state == GAMER_OVER:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                state = START
            screen.blit(gameover,gameover_rect)

    if state == START:
        screen.blit(day_background if bg_state == "day" else night_background, (0,0))
        txt = pygame.font.SysFont(None,50).render("PRESS SPACE TO START", True, (255,255,255))
        screen.blit(txt,(400,320))
        pygame.display.flip()
        continue
    if state == PLAYING:
        bird_anim_timer += dt
        if bird_anim_timer > 0.1:
            bird_index = (bird_index + 1) % len(bird_frames)
            bird_anim_timer = 0
    
        velocity_y += gravity * dt
        bird.y += velocity_y * dt
        
        # Adding Pipes to the scren
        for pipe in pipe_list:
            pipe["top"].x -= pipe_speed * dt
            pipe["bottom"].x -= pipe_speed * dt

        pipe_list = [p for p in pipe_list if p["top"].right > 0]

        # collision
        for pipe in pipe_list:
            if bird.colliderect(pipe["top"]) or bird.colliderect(pipe["bottom"]):
                death_sound.play()
                state = GAMER_OVER

        # scoring
        for pipe in pipe_list:
            if not pipe["scored"] and pipe["top"].centerx < bird.centerx:
                score += 1
                score_sound.play()
                pipe["scored"] = True
        
        
        # Border
        if bird.top < 0:
            bird.top = 0
            velocity_y = 0
    
        if bird.bottom > ground_y:
            bird.bottom = ground_y
            velocity_y = 0
            death_sound.play()
            state = GAMER_OVER
    
        #Draw 
        screen.fill(("black"))
        if bg_state == "day":
            screen.blit(day_background,(0,0))
        else:
            screen.blit(night_background,(0,0))
    
        for pipe in pipe_list:
            screen.blit(pipe_green,pipe["bottom"])
            flipped = pygame.transform.flip(pipe_green,False,True)
            screen.blit(flipped,pipe["top"])
            
        screen.blit(bird_frames[bird_index],bird)
        
        score_str = str(score)
        x_offset = SCREEN_WIDTH // 2 - (len(score_str) * 20)
            
        for i, digit in enumerate(score_str):
            num = int(digit)
            screen.blit(digits[num], (x_offset + i * 40,50))
        pygame.display.flip()
    if state == GAMER_OVER:
        screen.blit(gameover,gameover_rect)
        pygame.display.flip()

pygame.quit()
sys.exit()