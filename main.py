# https://github.com/BurnySc2/python-sc2

from sc2 import maps
from sc2.player import Bot, Computer
from sc2.main import run_game
from sc2.data import Race, Difficulty
from sc2.bot_ai import BotAI

from sc2.ids.ability_id import AbilityId
from sc2.ids.unit_typeid import UnitTypeId


SCV = UnitTypeId.SCV

class MyDeadlyTerranBot(BotAI):
    async def on_step(self, iteration):
        await self.build_workers()
        await self.build_supply_depots()
        await self.build_barracks()
        await self.train_marines()
        await self.attack_enemy()

    async def build_workers(self):
        if self.can_afford(UnitTypeId.SCV) and self.units(UnitTypeId.SCV).amount < 16:
            command_centers = self.townhalls.ready
            for cc in command_centers:
                if self.can_afford(UnitTypeId.SCV) and cc.is_idle:
                    self.do(cc.train(UnitTypeId.SCV))

    async def build_supply_depots(self):
        if self.supply_left < 5 and not self.already_pending(UnitTypeId.SUPPLYDEPOT):
            command_centers = self.townhalls.ready
            if command_centers.exists:
                if self.can_afford(UnitTypeId.SUPPLYDEPOT):
                    await self.build(UnitTypeId.SUPPLYDEPOT, near=command_centers.first)

    async def build_barracks(self):
        if self.can_afford(UnitTypeId.BARRACKS) and self.units(UnitTypeId.BARRACKS).amount < 3:
            command_centers = self.townhalls.ready
            if command_centers.exists:
                if self.can_afford(UnitTypeId.BARRACKS):
                    await self.build(UnitTypeId.BARRACKS, near=command_centers.first)

    async def train_marines(self):
        barracks = self.units(UnitTypeId.BARRACKS).ready
        for barrack in barracks:
            if self.can_afford(UnitTypeId.MARINE) and barrack.is_idle:
                self.do(barrack.train(UnitTypeId.MARINE))

    async def attack_enemy(self):
        if self.units(UnitTypeId.MARINE).amount >= 10:
            target = self.enemy_start_locations[0]
            marines = self.units(UnitTypeId.MARINE)
            for marine in marines:
                self.do(marine.attack(target))






    

run_game(maps.get("AcropolisLE"), [
    Bot(Race.Terran, MyDeadlyTerranBot()),
    Computer(Race.Protoss, Difficulty.Medium)
], realtime=False)

