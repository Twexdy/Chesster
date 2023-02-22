import chesster as cs
import random
import pygame

pygame.init()
clock = pygame.time.Clock()
main = cs.new(scale=80, debug_mode=True)

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