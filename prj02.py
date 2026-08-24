##########import##########
import pygame
##########basic settings##########
width = 800
height = 600
fps = 60
background = (0, 0, 0)
##########initial settings##########
pygame.init()
##########game window settings##########
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("GAME")
clock = pygame.time.Clock()
##########main code##########
running = True
while running:
    clock.tick(fps)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False
    screen.fill(background)
    pygame.display.flip()
##########game over settings##########
pygame.quit()