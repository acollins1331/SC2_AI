import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer

class ZaitaBot(sc2.BotAI):
  async def on_step(self, iteration):
    return
    #await self.distribute_workers()

  
  async def check_supply_for_overlords(self):
    return
    
    

run_game(maps.get("AbyssalReefLE"), [Bot(Race.Zerg, ZaitaBot()), Computer(Race.Terran, Difficulty.Easy)],
  realtime=True)
