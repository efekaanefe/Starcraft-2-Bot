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
        await self.build_refinery()
        await self.assign_scv_to_refinery()
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
        if self.supply_left < 10:
            if not self.already_pending(UnitTypeId.SUPPLYDEPOT):
                command_centers = self.townhalls.ready
                if command_centers.exists:
                    if self.can_afford(UnitTypeId.SUPPLYDEPOT):
                        await self.build(UnitTypeId.SUPPLYDEPOT, near=command_centers.first)


    async def build_refinery(self):
        if self.structures(UnitTypeId.REFINERY).amount < 2:
            if self.can_afford(UnitTypeId.REFINERY):
                for command_center in self.structures(UnitTypeId.COMMANDCENTER).ready:
                    vespene_geysers = self.vespene_geyser.closer_than(15, command_center)
                    for vespene_geyser in vespene_geysers:
                        if not self.can_afford(UnitTypeId.REFINERY):
                            break
                        worker = self.select_build_worker(vespene_geyser.position)
                        if worker is None:
                            break
                        if not self.units(UnitTypeId.REFINERY).closer_than(1, vespene_geyser).exists:
                            worker.build(UnitTypeId.REFINERY, vespene_geyser)

    async def assign_scv_to_refinery(self):
        for refinery in self.structures(UnitTypeId.REFINERY).owned.ready:
            if refinery.assigned_harvesters < refinery.ideal_harvesters:
                workers = self.units(UnitTypeId.SCV).owned.idle
                if workers:
                    worker = workers.closest_to(refinery)
                    self.do(worker.gather(refinery))


    async def build_barracks(self):
        if self.structures(UnitTypeId.BARRACKS).amount < 3:
            if self.can_afford(UnitTypeId.BARRACKS):
                command_centers = self.townhalls.ready
                if command_centers.exists:
                    if self.can_afford(UnitTypeId.BARRACKS) and not self.already_pending(UnitTypeId.BARRACKS):
                        map_center = self.game_info.map_center
                        placement_position = self.start_location.towards(map_center, distance=5)
                        await self.build(UnitTypeId.BARRACKS, near=placement_position)

    async def train_marines(self):
        barracks = self.structures(UnitTypeId.BARRACKS)
        for barrack in barracks:
            if self.can_afford(UnitTypeId.MARINE) and barrack.is_idle:
                self.do(barrack.train(UnitTypeId.MARINE))

    async def attack_enemy(self):
        if self.units(UnitTypeId.MARINE).idle.amount >= 30:
            target = self.enemy_start_locations[0]
            marines = self.units(UnitTypeId.MARINE)
            for marine in marines:
                self.do(marine.attack(target))



run_game(maps.get("AcropolisLE"), [
    Bot(Race.Terran, MyDeadlyTerranBot()),
    Computer(Race.Protoss, Difficulty.Medium)
], realtime=False)

