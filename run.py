import simpy
from advertiser import Advertiser
from scanner import Scanner

env = simpy.Environment()

ps = Scanner(env)
for i in range(1000):
    adv = Advertiser(env, i, scanner=ps)

env.run(100000)

print(ps.received / (ps.received + ps.lost))