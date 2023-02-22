import chesster as cs
import time
import random
import pygame

pygame.init()
clock = pygame.time.Clock()
main = cs.new(scale=80, debug_mode=True)

def make_move() :
    if main.legal_moves == [] or main.animating:
        return
    time.sleep(0.5)
    print(len(main.legal_moves))
    random_move = main.legal_moves[random.randint(0, len(main.legal_moves) - 1)]
    main.move(*random_move)

while True:
    main.update()
    pygame.display.flip()
    
    if main.turn == "b":
        make_move()
    
    clock.tick(main.refresh_rate_cap)