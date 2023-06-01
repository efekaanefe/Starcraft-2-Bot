# https://github.com/BurnySc2/python-sc2

from sc2 import maps
from sc2.player import Bot, Computer
from sc2.main import run_game
from sc2.data import Race, Difficulty
from sc2.bot_ai import BotAI

from sc2.ids.ability_id import AbilityId
from sc2.ids.unit_typeid import UnitTypeId

class MyDeadlyBot(BotAI):
    async def on_step(self, iteration: int):
        print("Iteration: ", iteration)

        if iteration == 0:
            for worker in self.workers:
                worker.attack(self.enemy_start_locations[0])
        self.make_drone()
        self.build_spawning_pool()


    def make_drone(self):
        print(f"You have{len(self.larva)}")
        print(f"Army: {self.army_count}")
        for loop_larva in self.larva:
            if self.can_afford(UnitTypeId.DRONE):
                loop_larva.train(UnitTypeId.DRONE)
                # Add break statement here if you only want to train one
            else:
                # Can't afford drones anymore
                break

    async def build_spawning_pool(self):
        if self.can_afford(UnitTypeId.SPAWNINGPOOL) and self.already_pending(UnitTypeId.SPAWNINGPOOL) + self.structures.filter(lambda structure: structure.type_id == UnitTypeId.SPAWNINGPOOL and structure.is_ready).amount == 0:
            worker_candidates = self.workers.filter(lambda worker: (worker.is_collecting or worker.is_idle) and worker.tag not in self.unit_tags_received_action)
    # Worker_candidates can be empty
            if worker_candidates:
                map_center = self.game_info.map_center
                position_towards_map_center = self.start_location.towards(map_center, distance=5)
                placement_position = await self.find_placement(UnitTypeId.SPAWNINGPOOL, near=position_towards_map_center, placement_step=1)
        # Placement_position can be None
                if placement_position:
                    build_worker = worker_candidates.closest_to(placement_position)
                build_worker.build(UnitTypeId.SPAWNINGPOOL, placement_position)
    

run_game(maps.get("AcropolisLE"), [
    Bot(Race.Zerg, MyDeadlyBot()),
    Computer(Race.Protoss, Difficulty.Medium)
], realtime=False)
