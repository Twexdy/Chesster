# This is an example of a chess bot that makes random moves

import chesster as cs
import random
import pygame

pygame.init()
clock = pygame.time.Clock()
main = cs.new(scale=140, debug_mode=True, refresh_rate_cap=100)

def make_random_move() :
    if main.legal_moves == [] or main.animating:
        return
    random_move = main.legal_moves[random.randint(0, len(main.legal_moves) - 1)]
    main.move(*random_move)

while True:
    main.update()
    pygame.display.flip()
    
    if main.turn == "b":
        make_random_move()
    
    clock.tick(main.refresh_rate_cap)
