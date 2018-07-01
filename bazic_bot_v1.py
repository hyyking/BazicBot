# Libraries

import random
import sc2
from math import fabs
from sc2 import Race, Difficulty
from sc2.position import Point2
from sc2.constants import *
from sc2.player import Bot, Computer, Human
from sc2.helpers import ControlGroup

# Main

class BazicBot(sc2.BotAI):

	async def on_step(self, iteration):
		await self.distribute_workers()
		await self.build_workers()
		await self.build_marines()
		await self.build_supply_depot()
		await self.add_marines_to_cg(iteration)
		await self.attack_with_marines()
		await self.regroup_marines()
		await self.build_expansion()
		await self.build_barracks()
		await self.build_vespene()

	async def build_workers(self):
		for cc in self.units(COMMANDCENTER).ready:
			if self.can_afford(SCV) and cc.noqueue and not self.has_ideal_workers(cc):
				await self.do(cc.train(SCV))

	async def build_supply_depot(self):
		if self.supply_left < 3 + self.units(BARRACKS).amount and self.can_afford(SUPPLYDEPOT) and not self.already_pending(SUPPLYDEPOT):
			await self.build(SUPPLYDEPOT, near=self.units(COMMANDCENTER).ready.random.position.towards(self.game_info.map_center, 8))

	async def build_marines(self):
		for barrack in self.units(BARRACKS).ready:
			if self.can_afford(MARINE) and barrack.noqueue:
				await self.do(barrack.train(MARINE))

	async def add_marines_to_cg(self, iteration):
		if self.units(MARINE).idle.amount > 15 + (2 * self.units(BARRACKS).ready.amount) and iteration % 42 == 0:
			idle_marines = ControlGroup(self.units(MARINE).idle)
			self.attack_groups.add(idle_marines)

	async def attack_with_marines(self):
		for ag in list(self.attack_groups):
			alive_units = ag.select_units(self.units)
			if alive_units.exists and alive_units.idle.exists:
				target = self.known_enemy_structures.random_or(self.enemy_start_locations[0]).position
				for marine in ag.select_units(self.units):
					 await self.do(marine.attack(target))
			else:
				self.attack_groups.remove(ag)

	async def regroup_marines(self):
		marines = self.units(MARINE).idle
		for marine in marines:
			cc = self.units(COMMANDCENTER).ready.closest_to(self.game_info.map_center)
			if marine.position.distance_to(cc) > 10:
				near = Point2((cc.position.x - 1, cc.position.y))
				await self.do(marine.move(near))
				break

	"""
	async def attack_seen_enemies(self):
		try:
			target = self.known_enemy_units.not_structure.random
			in_range = False
			for structure in self.units().structure:
				if target.position.distance_to(structure) > 10:
					in_range = True
			if not in_range:
				return
		except:
			return
		defence_force = ControlGroup(self.units(MARINE).idle)
		for marine in defence_force.select_units(self.units):
			await self.do(marine.attack(target))
	"""

	# Expension actions

	async def build_expansion(self):
		if self.units(COMMANDCENTER).amount == 1:
			if self.can_afford(COMMANDCENTER):
				await self.expand_now()
		else:
			for cc in self.units(COMMANDCENTER).ready:
				if not self.has_ideal_workers(cc):
					return
			if self.can_afford(COMMANDCENTER):
				await self.expand_now()

	async def build_barracks(self):
		if self.units(COMMANDCENTER).amount == 2 and self.units(BARRACKS).amount == 0:
			if self.can_afford(BARRACKS):
				await self.build(BARRACKS, near=self.units(COMMANDCENTER).random.position.towards(self.game_info.map_center, 3))
		elif self.units(COMMANDCENTER).ready.amount >= 2 and self.already_pending(BARRACKS) < 2 and not self.has_ideal_unit_structure(BARRACKS, 3):
			if self.can_afford(BARRACKS):
				await self.build(BARRACKS, near=self.units(COMMANDCENTER).random.position.towards(self.game_info.map_center, 3))

	async def build_vespene(self):
		for cc in self.units(COMMANDCENTER).ready:
			if self.has_ideal_workers(cc) and not self.already_pending(REFINERY) and self.can_afford(REFINERY):
				for vg in self.state.vespene_geyser.closer_than(10.0, cc):
					if self.units(REFINERY).closer_than(1.0, vg).exists:
						break
					worker = self.select_build_worker(vg.position)
					if worker is None:
						break
					await self.do(worker.build(REFINERY, vg))
					break

	# Non-asyncs

	def has_ideal_unit_structure(self, unit, limit):
		if self.units(unit).amount < limit * self.units(COMMANDCENTER).amount:
			return False
		else:
			return True

	def has_ideal_workers(self, cc):
		vespenes = self.units(REFINERY).ready.closer_than(10, cc.position)
		ideal_vespenes = vespenes.amount * 3
		assigned_vespenes = 0
		for vespene in vespenes:
			assigned_vespenes += vespene.assigned_harvesters
		
		ideal = cc.ideal_harvesters + ideal_vespenes
		
		if ideal > cc.assigned_harvesters + assigned_vespenes:
			return False
		else:
			return True

	# Add has_ideal_supply_depot function

	def __init__(self):
		self.attack_groups = set()

def main():
	sc2.run_game(
		sc2.maps.get("Abyssal Reef LE"),
		[
			Bot(Race.Terran, BazicBot()),
			Computer(Race.Zerg, Difficulty.Hard),
		],
		realtime=True,
	)

if __name__ == '__main__':
	main()