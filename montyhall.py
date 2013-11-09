
# monty hall problem
from random import randint

ndoors = 3
pickdoor = lambda: randint(0, ndoors - 1)
CAR, GOAT = range(2)
games = 100000
dont = 0
do = 0

for _ in xrange(games):
    doors = [GOAT] * ndoors
    doors[pickdoor()] = CAR

    player = pickdoor()
    host = pickdoor()
    while host == player or doors[host] == CAR:
        host = pickdoor()

    newdoor = pickdoor()
    while host == newdoor or player == newdoor:
        newdoor = pickdoor()

    dont += doors[player] == CAR
    do += doors[newdoor] == CAR

print 'dont change door: %s (%.2f%%)' % (dont, dont / float(games))
print 'do change door: %s (%.2f%%)' % (do, do / float(games))
