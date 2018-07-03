import sc2
from sc2 import Race, Difficulty
from sc2.position import Point2
from sc2.constants import *
from sc2.player import Bot, Computer, Human
from sc2.helpers import ControlGroup



class Territory(sc2.BotAI):

	def __init__(self):
		self.territory_cc_list = list()
		self.proxy_cc_list = list()


	async def on_step(self, iteration):
		await self.update_territory(iteration)
		await self.defend_territory()
		await self.proxy_expand()

		print(self.territory_cc_list)
		print(self.proxy_cc_list)


	async def update_territory(self, iteration):
		#First cc
		if iteration == 0:
			self.territory_cc_list.append(self.units(COMMANDCENTER)[0])
		
		#cc update
		territory_tag_list = {x.tag for x in self.territory_cc_list}
		proxy_tag_list = {x.tag for x in self.proxy_cc_list}
		for cc in self.units(COMMANDCENTER):
			if self.in_territory_range(cc.position) and cc.tag not in territory_tag_list:
				return self.territory_cc_list.append(cc)
			elif (cc.tag not in territory_tag_list) and (cc.tag not in proxy_tag_list):
				return self.proxy_cc_list.append(cc)


		#In case of cc destruction
		cc_tag_list = [x.tag for x in self.units(COMMANDCENTER)]
		for cc in self.proxy_cc_list:
			if cc.tag not in cc_tag_list:
				return self.proxy_cc_list.remove(cc)

		for cc in self.territory_cc_list:
			if cc.tag not in cc_tag_list:
				return self.territory_cc_list.remove(cc)

	async def defend_territory(self):
		try:
			target = self.known_enemy_units.not_structure.closest_to(self.territory_cc_list[-1])
		except:
			return

		if self.in_territory_range(target.position):
			for unit in self.units(MARINE).idle:
				if self.in_territory_range(unit.position):
					await self.do(unit.attack(target))


	#BUILD CHEESE BASE
	async def proxy_expand(self):
		if self.can_afford(COMMANDCENTER) and len(self.proxy_cc_list) == 0 and len(self.territory_cc_list) == 1:
			for exp in self.expansion_locations:
				if self.object_in_range(exp, self.enemy_start_locations[0].position, 100, 40):
					await self.build(COMMANDCENTER, near=exp)


	#EXPAND FROM
	async def expand_from(self, start_building, building=None, max_distance=10, location=None):
		if not building:
			building = self.townhalls.first.type_id

		assert isinstance(building, UnitTypeId)

		if not location:
			location = await self.get_from_expansion(start_building)

		await self.build(building, near=location, max_distance=max_distance, random_alternative=False, placement_step=1)

	async def get_from_expansion(self, start_building):
		"""Find next expansion location."""
		closest = None
		distance = 50
		for el in self.expansion_locations:
			def is_near_to_expansion(t):
				return t.position.distance_to(el) < self.EXPANSION_GAP_THRESHOLD
			
			if any(map(is_near_to_expansion, self.townhalls)):
				# already taken
				continue
			
			th = self.townhalls.first
			d = await self._client.query_pathing(th.position, el)
			if d is None:
				continue
			
			if d < distance and self.object_in_range(el.position, start_building.position, 45): #added range to building
				distance = d
				closest = el
		return closest


	#NON ASYNC
	def in_territory_range(self, object_position, lf_range=40):
		ox, oy = object_position
		for cc in self.territory_cc_list:
			ccx, ccy = cc.position
			if 0 < (ox-ccx)**2 + (oy-ccy)**2 < lf_range**2:
				return True
			else:
				continue
		return False

	def object_in_range(self, in_range, from_building, max_range, min_range=0):
		fx, fy = from_building
		sx, sy = in_range
		if min_range**2 < (sx-fx)**2 + (sy-fy)**2 < max_range**2:
			return True
		else:
			return False

def main():
	sc2.run_game(
		sc2.maps.get("Abyssal Reef LE"),
		[
			Bot(Race.Terran, Territory()),
			Computer(Race.Zerg, Difficulty.Easy),
		],
		realtime=True,
	)

if __name__ == '__main__':
	main()


'''
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
'''
