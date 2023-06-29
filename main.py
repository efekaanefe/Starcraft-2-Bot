# https://github.com/BurnySc2/python-sc2

from sc2 import maps
from sc2.player import Bot, Computer
from sc2.main import run_game
from sc2.data import Race, Difficulty
from sc2.bot_ai import BotAI

from sc2.ids.ability_id import AbilityId
from sc2.ids.unit_typeid import UnitTypeId

import random

SCV = UnitTypeId.SCV

class MyDeadlyTerranBot(BotAI):

    def __init__(self):
        self.ITERATIONS_PER_MINUTE = 165
        self.MAX_WORKERS = 50

    async def on_step(self, iteration):
        self.iteration = iteration
        await self.distribute_workers()
        await self.build_workers()
        await self.assign_idle_scv_to_minerals() 
        await self.build_supply_depots()
        await self.build_refinery()
        await self.expand()
        await self.assign_scv_to_refinery()
        await self.build_barracks()
        await self.train_marines()
        await self.build_factory()
        await self.train_hellions()
        await self.build_starport()
        await self.train_vikings()
        await self.attack_enemy()

    async def build_workers(self):
        needed_workers = self.structures(UnitTypeId.COMMANDCENTER).amount*16
        if self.can_afford(UnitTypeId.SCV) and self.units(UnitTypeId.SCV).amount < min(needed_workers,self.MAX_WORKERS):
            command_centers = self.townhalls.ready
            for cc in command_centers:
                if self.can_afford(UnitTypeId.SCV) and cc.is_idle:
                    self.do(cc.train(UnitTypeId.SCV))

    async def assign_idle_scv_to_minerals(self):
        command_centers = self.structures(UnitTypeId.COMMANDCENTER).owned
        idle_workers = self.units(UnitTypeId.SCV).owned.idle

        for worker in idle_workers:
            assigned_command_center = None
            for cc in command_centers:
                if cc.assigned_harvesters < cc.ideal_harvesters:
                    assigned_command_center = cc
                    break

            if assigned_command_center is None:
                await self.create_new_command_center(worker.position)
                return

            if assigned_command_center:
                mineral_field = self.mineral_field.closest_to(assigned_command_center)

            if mineral_field.assigned_harvesters > mineral_field.ideal_harvesters:
                excessive_workers = self.workers.filter(lambda w: w.is_gathering and w.gathering.target == mineral_field)
                if excessive_workers:
                    self.do(excessive_workers.random.stop())
                    self.do(worker.gather(mineral_field))
                else:
                    self.do(worker.gather(mineral_field))
            else:
                self.do(worker.gather(mineral_field))


    async def create_new_command_center(self, position):
        if self.can_afford(UnitTypeId.COMMANDCENTER):
            await self.build(UnitTypeId.COMMANDCENTER, near=position)

    async def build_supply_depots(self):
        if self.supply_left < 10:
            if not self.already_pending(UnitTypeId.SUPPLYDEPOT):
                command_centers = self.townhalls.ready
                if command_centers.exists:
                    if self.can_afford(UnitTypeId.SUPPLYDEPOT):
                        position = command_centers.first.position.towards_with_random_angle(self.game_info.map_center, 16)
                        await self.build(UnitTypeId.SUPPLYDEPOT, near=position)

    async def build_refinery(self):
        ccs_amount = self.structures(UnitTypeId.COMMANDCENTER).ready.amount
        if self.structures(UnitTypeId.REFINERY).amount < ccs_amount*2:
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

    async def expand(self):
        if (self.structures(UnitTypeId.COMMANDCENTER).amount < 4 # (self.iteration / self.ITERATIONS_PER_MINUTE) 
            and self.can_afford(UnitTypeId.COMMANDCENTER)):
            await self.expand_now()

    async def build_barracks(self):
        if self.structures(UnitTypeId.BARRACKS).amount < 3:
            if self.can_afford(UnitTypeId.BARRACKS):
                command_centers = self.townhalls.ready
                if command_centers.exists:
                    if self.can_afford(UnitTypeId.BARRACKS) and not self.already_pending(UnitTypeId.BARRACKS):
                        position = command_centers.first.position.towards_with_random_angle(self.game_info.map_center, 16)
                        await self.build(UnitTypeId.BARRACKS, near=position)

    async def build_factory(self):
        if self.structures(UnitTypeId.BARRACKS).ready:
            if self.structures(UnitTypeId.FACTORY).amount < 3 and not self.already_pending(UnitTypeId.FACTORY):
                cc = self.townhalls.ready.first
                if self.can_afford(UnitTypeId.FACTORY):
                    position = cc.position.towards_with_random_angle(self.game_info.map_center, 16)
                    await self.build(UnitTypeId.FACTORY, near=position)

    async def build_starport(self):
        if self.structures(UnitTypeId.STARPORT).amount < 3 and not self.already_pending(UnitTypeId.STARPORT):
            cc = self.townhalls.ready.first
            if self.can_afford(UnitTypeId.STARPORT):
                position = cc.position.towards_with_random_angle(self.game_info.map_center, 16)
                await self.build(UnitTypeId.STARPORT, near=position)


    async def train_marines(self):
        barracks = self.structures(UnitTypeId.BARRACKS)
        for barrack in barracks:
            if self.can_afford(UnitTypeId.MARINE) and barrack.is_idle:
                self.do(barrack.train(UnitTypeId.MARINE))


    async def train_hellions(self):
        factories = self.structures(UnitTypeId.FACTORY)
        for factory in factories:
            if self.can_afford(UnitTypeId.HELLION) and factory.is_idle:
                self.do(factory.train(UnitTypeId.HELLION))

    async def train_vikings(self):
        starports = self.structures(UnitTypeId.STARPORT)
        for starport in starports:
            if self.can_afford(UnitTypeId.VIKINGASSAULT) and starport.is_idle:
                self.do(starport.train(UnitTypeId.VIKINGASSAULT))


    async def attack_enemy(self):
        def attack(target):
            for marine in marines:
                self.do(marine.attack(target))
            for hellion in hellions:
                self.do(hellion.attack(target))
            for viking in vikings:
                self.do(viking.attack(target))

        marines = self.units(UnitTypeId.MARINE)
        hellions = self.units(UnitTypeId.HELLION)
        vikings = self.units(UnitTypeId.VIKING)

        if len(self.enemy_units) > 0:
            target = random.choice(self.enemy_units)
            attack(target)
            
        if self.units(UnitTypeId.MARINE).idle.amount >= 50:
            target = self.enemy_start_locations[0]
            attack(target)

        



run_game(maps.get("AcropolisLE"), [
    Bot(Race.Terran, MyDeadlyTerranBot()),
    Computer(Race.Terran, Difficulty.Hard)
], realtime=False)

