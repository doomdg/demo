from BaseTrackableComp import *
from StaticData.Achievement import Achievement
import PLAYER_ACHIEVEMENT
import time


class PlayerAchievementComp(BaseTrackableComp):
	def __init__(self):
		super().__init__()
		self.player_stats = None

	def onAttached(self, owner):
		self.SetupPlayerAchievementList()
		self.UpdateAchievements()
	
	# slow. Do not call on update
	def SetupPlayerAchievementList(self):
		player_stats = self.getPlayerStats()
		achievement_master_list = Achievement.getAll()

		for ach_uid, ach_data in achievement_master_list.items():
			if self.checkEligible(ach_data):
				tracked_stat, target_value = self.getTrackedStat(ach_data)
				tracked_stat_value = player_stats.parseAndReturnStat(tracked_stat)
				current_value = tracked_stat_value if tracked_stat_value is not None else 0
				if ach_data.is_cumulative:
					start_value = 0
				else:
					start_value = current_value
					target_value = start_value + current_value
				
				data = {
					"uid"  				: ach_uid,
					"is_cumulative"		: ach_data.is_cumulative,
					"tracked_stat"		: tracked_stat,
					"start_value"		: int(start_value),
					"cur_value"			: int(current_value),
					"target_value" 		: int(target_value)
				}
				
				ach_info = PLAYER_ACHIEVEMENT.player_achievement_instance.createObjFromDict(data)
				self.appendAchievement(ach_data, ach_info)
		self.UpdateAchievements()


	def UpdateAchievements(self):
		player_stats = self.owner.player_stats_comp
		assert(player_stats is not None)
		for player_achievement in self.achievement_list:
			tracked_stat_value = player_stats.parseAndReturnStat(player_achievement["tracked_stat"])
			player_achievement["cur_value"] = tracked_stat_value if tracked_stat_value is not None else 0
			self.CompleteAchievement(player_achievement)
		
		for player_achievement in self.hidden_achievement_list:
			tracked_stat_value = player_stats.parseAndReturnStat(player_achievement["tracked_stat"])
			player_achievement["cur_value"] = tracked_stat_value if tracked_stat_value is not None else 0
			self.CompleteAchievement(player_achievement)

		self.owner.writeToDB()

	def CompleteAchievement(self, player_achievement):
		if (player_achievement["cur_value"] != player_achievement["target_value"]):
			return

		achievement = Achievement.getByUID(player_achievement["uid"])
		if not achievement:
			return
		rewards = achievement.reward

		detail = {"name": "achievement_" + str(achievement.uid)}
		for key, value in rewards.items():
			self.ApplyRewards(key, value, detail)

		self.UpdateNamedBonus(achievement.uid)

		# If this achievement has a chain, then we want to set up the next part of the chain here
		# instead of using the expensive SetupPlayerAchievementList
		if achievement.next_chain is not None:
			next_ach = Achievement.getByUID(achievement.next_chain)
			# chain achievements will start where the previous achievement left off
			start_value = player_achievement["cur_value"]
			current_value = player_achievement["cur_value"]
			tracked_stat, target_value = self.getTrackedStat(next_ach)
			target_value = target_value - player_achievement["target_value"]
			target_value = current_value + target_value
			data = {
				"uid"  				: next_ach.uid,
				"is_cumulative"		: next_ach.is_cumulative,
				"tracked_stat"		: tracked_stat,
				"start_value"		: int(start_value),
				"cur_value"			: int(current_value),
				"target_value" 		: int(target_value)
			}
			ach_info = PLAYER_ACHIEVEMENT.player_achievement_instance.createObjFromDict(data)
			self.appendAchievement(next_ach, ach_info)
		if player_achievement in self.achievement_list:
			self.achievement_list.remove(player_achievement)
		elif player_achievement in self.hidden_achievement_list:
			self.hidden_achievement_list.remove(player_achievement)

	def appendAchievement(self, achievement, ach_info):
		if achievement.is_hidden:
			self.hidden_achievement_list.append(ach_info)
		else:
			self.achievement_list.append(ach_info)

	def checkEligible(self, ach_data):
		if not ach_data.is_enabled:
			return

		player_stats = self.getPlayerStats()
		if ach_data.uid in player_stats.named_bonuses:
			return
			
		if ach_data.requirements is not None:
			for requirement in ach_data.requirements:
				if requirement not in player_stats.named_bonuses:
					return False
		
		return True

	def getPlayerStats(self):
		if self.player_stats is None:
			self.player_stats = self.owner.player_stats_comp
			assert(self.player_stats is not None)
		
		return self.player_stats
		

	def onDetached(self, owner):
		pass
