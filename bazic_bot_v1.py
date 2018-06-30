# Libraries

import random
import sc2
from sc2 import Race, Difficulty
from sc2.constants import *
from sc2.player import Bot, Computer, Human

# Main

class BazicBot(sc2.BotAI):
	async def on_step(self, iteration):
		await self.distribute_workers()
		await self.build_workers()
		await self.build_supply_depot()
		await self.first_expansion()
		await self.first_barracks()

	async def build_workers(self):
		for cc in self.units(COMMANDCENTER).ready:
			if self.can_afford(SCV) and cc.noqueue and self.has_ideal_workers(cc):
				await self.do(cc.train(SCV))

	async def build_supply_depot(self):
		if self.supply_left < 3 and self.can_afford(SUPPLYDEPOT) and not self.already_pending(SUPPLYDEPOT):
			await self.build(SUPPLYDEPOT, near=self.units(COMMANDCENTER).ready.random.position.towards(self.game_info.map_center, 8))

	# First actions

	async def first_expansion(self):
		if self.units(COMMANDCENTER).amount == 1:
			if self.can_afford(COMMANDCENTER):
				await self.expand_now()

	async def first_barracks(self):
		if self.units(COMMANDCENTER).amount == 2 and self.units(BARRACKS).amount == 0:
			if self.can_afford(BARRACKS):
				await self.build(BARRACKS, near=self.units(COMMANDCENTER).random.position.towards(self.game_info.map_center, 3))

	# Non-asyncs

	def has_ideal_workers(self, cc):
		vespenes = self.units(REFINERY).ready.closer_than(10, cc.position)
		ideal_vespenes = vespenes.amount * 3
		assigned_vespenes = 0
		for vespene in vespenes:
			assigned_vespenes += vespene.assigned_harvesters
		
		ideal = cc.ideal_harvesters + ideal_vespenes
		
		if ideal > cc.assigned_harvesters + assigned_vespenes:
			return True
		else:
			return False

def main():
	sc2.run_game(
		sc2.maps.get("Abyssal Reef LE"),
		[
			Bot(Race.Terran, BazicBot()),
			Computer(Race.Zerg, Difficulty.Easy),
		],
		realtime=True,
	)

if __name__ == '__main__':
	main()