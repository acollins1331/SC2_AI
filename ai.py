import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.constants import NEXUS, PROBE, PYLON, ASSIMILATOR, GATEWAY, \
 CYBERNETICSCORE, ZEALOT, STALKER, STARGATE, VOIDRAY
import random


class SentdeBot(sc2.BotAI):
    def __init__(self):
        self.ITERATIONS_PER_MINUTE = 165
        self.MAX_WORKERS = 70

    async def on_step(self, iteration):
        self.iteration = iteration
        await self.distribute_workers()
        await self.build_workers()
        await self.build_pylons()
        await self.build_assimilators()
        await self.expand()
        await self.offensive_force_buildings()
        await self.build_offensive_force()
        await self.attack()

    async def build_workers(self):
        if (len(self.units(NEXUS)) * 16) > len(self.units(PROBE)) and len(self.units(PROBE)) < self.MAX_WORKERS:
            for nexus in self.units(NEXUS).ready.noqueue:
                if self.can_afford(PROBE):
                    await self.do(nexus.train(PROBE))


    async def build_pylons(self):
        if self.supply_left < 5 and not self.already_pending(PYLON):
            nexuses = self.units(NEXUS).ready
            if nexuses.exists:
                if self.can_afford(PYLON):
                    await self.build(PYLON, near=nexuses.random)
        if self.supply_left < 12 and not self.already_pending(PYLON):
            nexuses = self.units(NEXUS).ready
            if nexuses.exists and self.iteration > 500:
            	if self.can_afford(PYLON):
            		await self.build(PYLON, near=nexuses.random)


    async def build_assimilators(self):
        for nexus in self.units(NEXUS).ready:
            vaspenes = self.state.vespene_geyser.closer_than(15.0, nexus)
            for vaspene in vaspenes:
                if not self.can_afford(ASSIMILATOR):
                    break
                worker = self.select_build_worker(vaspene.position)
                if worker is None:
                    break
                if not self.units(ASSIMILATOR).closer_than(1.0, vaspene).exists:
                    await self.do(worker.build(ASSIMILATOR, vaspene))

    async def expand(self):
        if self.units(NEXUS).amount < (self.iteration / 1.3 * self.ITERATIONS_PER_MINUTE) and self.can_afford(NEXUS) and self.units(NEXUS).amount < 5:
            await self.expand_now()

    async def offensive_force_buildings(self):
        #print(self.iteration / self.ITERATIONS_PER_MINUTE)
        if self.units(PYLON).ready.exists:
            pylon = self.units(PYLON).ready.random

            if self.units(GATEWAY).ready.exists and not self.units(CYBERNETICSCORE):
                if self.can_afford(CYBERNETICSCORE) and not self.already_pending(CYBERNETICSCORE):
                    await self.build(CYBERNETICSCORE, near=pylon)

            elif len(self.units(GATEWAY)) < ((self.iteration / 2 * self.ITERATIONS_PER_MINUTE)/2):
                if self.can_afford(GATEWAY) and not self.already_pending(GATEWAY) and self.units(GATEWAY).amount < 5:
                    await self.build(GATEWAY, near=pylon)

            if self.units(CYBERNETICSCORE).ready.exists:
                if len(self.units(STARGATE)) < ((self.iteration / self.ITERATIONS_PER_MINUTE)/2):
                    if self.can_afford(STARGATE) and not self.already_pending(STARGATE) and self.units(STARGATE).amount < 4:
                        await self.build(STARGATE, near=pylon)



    async def build_offensive_force(self):

        for z in self.units(GATEWAY).ready.noqueue:
        	if self.units(ZEALOT).amount < self.units(STALKER).amount and self.supply_left > 0 and self.can_afford(ZEALOT):
        		await self.do(z.train(ZEALOT))

        for gw in self.units(GATEWAY).ready.noqueue:
            if self.can_afford(STALKER) and self.supply_left > 0 and self.units(STALKER).amount < 12:
                await self.do(gw.train(STALKER))

        for sg in self.units(STARGATE).ready.noqueue:
            if self.can_afford(VOIDRAY) and self.supply_left > 0:
                await self.do(sg.train(VOIDRAY))

    def find_target(self, state):
        if len(self.known_enemy_units) > 0:
        #    return random.choice(self.known_enemy_units)
        #elif len(self.known_enemy_structures) > 0:
        #    return random.choice(self.known_enemy_structures)
        #else:
            return self.enemy_start_locations[0]

    async def attack(self):
        # {UNIT: [n to fight, n to defend]}
        aggressive_units = {STALKER: [8, 4],
                            VOIDRAY: [6, 3],
                            ZEALOT: [8, 4]}


        for UNIT in aggressive_units:
            if self.units(UNIT).amount > aggressive_units[UNIT][0] and self.units(UNIT).amount > aggressive_units[UNIT][1]:
                for s in self.units(UNIT).idle:
                    await self.do(s.attack(self.find_target(self.state)))
                for z in self.units(ZEALOT).idle:
                    await self.do(z.attack(self.find_target(self.state)))
                for s in self.units(STALKER).idle:
                    await self.do(s.attack(self.find_target(self.state)))
                for v in self.units(VOIDRAY).idle:
                	await self.do(v.attack(self.find_target(self.state)))

            elif self.units(UNIT).amount > aggressive_units[UNIT][1]:
                if len(self.known_enemy_units) > 0:
                    for s in self.units(UNIT).idle:
                        await self.do(s.attack(random.choice(self.known_enemy_units)))


run_game(maps.get("AbyssalReefLE"), [
    Bot(Race.Protoss, SentdeBot()),
    Computer(Race.Terran, Difficulty.VeryHard)
    ], realtime=False)