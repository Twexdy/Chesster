import chesster as cs
from pygame import *

init()
clock = time.Clock()
main = cs.new()

while True:
    main.update()
    display.flip()
    clock.tick(main.refresh_rate_cap)