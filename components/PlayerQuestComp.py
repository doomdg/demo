
from BaseTrackableComp import *
from QuestMgr import QuestMgr
from StaticData.Quest import Quest
import time
import random
import PLAYER_QUEST


class PlayerQuestComp(BaseTrackableComp):
	def __init__(self):
		super().__init__()
		self.player_quest_max = 3
		self.quest_manager = QuestMgr.getInstance()
		self.queued_alerts = {"new_quest" : 0, "complete_quest" : 0}
		self.quest_timers = []

	def onAttached(self, owner):
		# call only once
		if self.first_login:
			self.setupQuestSlots()

		self.UpdateQuestProgress()
		self.updateEligibleQuest()
		self.updatePlayerQuests()
	
	def onDetached(self, owner):
		self.clearQuestTimers()
		self.delTimer(self.timerID)
		self.time_manager.onDestroy()

	def setupQuestSlots(self):
		for _ in range(self.player_quest_max):
			data = {
				"uid"  				: "",
				"is_active"			: False,
				"start_time"		: 0,
				"complete_time"		: 0,
				"tracked_stat"		: "",
				"start_value"		: 0,
				"cur_value"			: 0,
				"target_value" 		: 0
			}
			
			quest_info = PLAYER_QUEST.player_quest_instance.createObjFromDict(data)
			self.quest_list.append(quest_info)
		self.first_login = False

	def setupQuestTimers(self):
		self.clearQuestTimers()
		for i in range(self.player_quest_max):
			player_quest = self.quest_list[i]
			if player_quest["is_active"]:
				continue

			time_since = time.time() - player_quest["complete_time"]
			countdown = self.quest_manager.refresh_timer - time_since
			if countdown > 0:
				self.quest_timers.append(self.registTimer(self.getNewQuestHelper, countdown, 0, 1))

	def clearQuestTimers(self):
		for i in range(len(self.quest_timers)):
			self.unregistTimer(self.quest_timers[i])

	def getNewQuestHelper(self, deltaTime):
		self.updatePlayerQuests()

	def UpdateQuestProgress(self):
		player_stats = self.owner.player_stats_comp
		assert(player_stats is not None)
		for player_quest in self.quest_list:
			if player_quest["is_active"]:
				tracked_stat_value = player_stats.parseAndReturnStat(player_quest["tracked_stat"])
				if tracked_stat_value:
					player_quest["cur_value"] = tracked_stat_value
				print(player_quest)
		self.setupQuestTimers()
		self.quest_list = self.quest_list
		self.owner.writeToDB()

	def CompleteQuest(self, index):
		player_quest = self.quest_list[index]
		if player_quest["is_active"] is False:
			return
		if (player_quest["cur_value"] < player_quest["target_value"]):
			return

		quest = Quest.getByUID(player_quest["uid"])
		rewards = quest.reward
		for key, value in rewards.items():
			self.ApplyRewards(key, value)

		self.UpdateNamedBonus(quest.uid)

		player_quest["is_active"] = False
		player_quest["complete_time"] = int(time.time())
		self.owner.player_stats_comp.total_quests_completed += 1
		self.quest_cooldowns.append(player_quest)
		self.updateEligibleQuest()
		self.updatePlayerQuests()

		if self.owner.client and self.client:
			self.client.rspQuestCompleted()

	def checkEligible(self, quest_data):
		player_stats = self.owner.player_stats_comp
		assert(player_stats is not None)
		if quest_data.is_enabled is False:
			return False
		if quest_data.requirements is not None:
			for requirement in quest_data.requirements:
				if requirement not in player_stats.named_bonuses:
					return False
			
		for player_quest in self.quest_cooldowns:
			if player_quest["uid"] == quest_data.uid:
				return False

		for player_quest in self.quest_list:
			if player_quest["uid"] == quest_data.uid:
				return False
		
		return True

	def addQuest(self, index, quest_uid):
		player_stats = self.owner.player_stats_comp
		assert(player_stats is not None)
		newQuest = Quest.getByUID(quest_uid)
		tracked_stat, target_value = self.getTrackedStat(newQuest)
		tracked_stat_value = player_stats.parseAndReturnStat(tracked_stat)
		start_value = tracked_stat_value if tracked_stat_value is not None else 0
		start_timer = int(time.time())
		data = {
			"uid"  				: newQuest.uid,
			"is_active"			: True,
			"start_time"		: start_timer,
			"complete_time"		: 0,
			"tracked_stat"		: tracked_stat,
			"start_value"		: int(start_value),
			"cur_value"			: int(start_value),
			"target_value" 		: int(target_value) + int(start_value)
		}
		
		quest_info = PLAYER_QUEST.player_quest_instance.createObjFromDict(data)
		self.last_quest_time = int(time.time())
		self.quest_list[index] = quest_info
		self.quest_list = self.quest_list
		if quest_uid in self.eligible_quests:
			self.eligible_quests.remove(quest_uid)
		self.owner.writeToDB()
		if self.client_initialized and self.owner.client and self.client:
			self.client.rspNewQuestAlert()
		else:
			self.queued_alerts["new_quest"] += 1

	def replaceQuest(self, index, quest_uid, override_time):
		player_stats = self.owner.player_stats_comp
		assert(player_stats is not None)
		newQuest = Quest.getByUID(quest_uid)
		tracked_stat, target_value = self.getTrackedStat(newQuest)
		tracked_stat_value = player_stats.parseAndReturnStat(tracked_stat)
		start_value = tracked_stat_value if tracked_stat_value is not None else 0
		start_timer = int(override_time)
		data = {
			"uid"  				: newQuest.uid,
			"is_active"			: True,
			"start_time"		: start_timer,
			"complete_time"		: 0,
			"tracked_stat"		: tracked_stat,
			"start_value"		: int(start_value),
			"cur_value"			: int(start_value),
			"target_value" 		: int(target_value) + int(start_value)
		}
		
		quest_info = PLAYER_QUEST.player_quest_instance.createObjFromDict(data)
		self.quest_list[index] = quest_info
		self.quest_list = self.quest_list
		self.owner.writeToDB()
	
	def updateEligibleQuest(self):
		all_quests = Quest.getAll()

		for player_quest in self.quest_cooldowns:
			quest = Quest.getByUID(player_quest["uid"])
			if time.time() > player_quest["complete_time"] + quest.cooldown:
				self.quest_cooldowns.remove(player_quest)

		for quest_uid, quest_data in all_quests.items():
			quest_eligible = self.checkEligible(quest_data)
			if quest_eligible and quest_uid not in self.eligible_quests:
				self.eligible_quests.append(quest_uid)
			elif not quest_eligible and quest_uid in self.eligible_quests:
				self.eligible_quests.remove(quest_uid)
		self.owner.writeToDB()
	
	def reqCompleteQuest(self, index):
		if index < len(self.quest_list):
			self.CompleteQuest(index)

	# Skipped quests must have the same tag
	def getSkippableQuests(self, quest):
		if not quest.same_type_only:
			return self.eligible_quests
		
		tags = quest.tag
		same_tag_quests = []
		for quest_uid in self.eligible_quests:
			quest = Quest.getByUID(quest_uid)
			if len(tags.intersection(quest.tags)) > 0:
				same_tag_quests.append(quest.uid)

		return same_tag_quests

	def reqSkipQuest(self, index):
		player_quest = self.quest_list[index]
		import time
		success = False
		time_now = time.time()
		if time_now > self.last_reroll_time + self.quest_manager.roll_timer:
			cur_quest = Quest.getByUID(player_quest["uid"])
			same_tagged_quests = self.getSkippableQuests(cur_quest)
			if len(same_tagged_quests) > 0:
				new_quest = random.choice(same_tagged_quests)
				self.last_reroll_time = int(time_now)
				# need to inherit the start_time
				self.replaceQue`st(index, new_quest, player_quest["start_time"])
				success = True
		
		if self.owner.client and self.client:
			self.client.rspQuestSkipped(success)

	# provides the next quest based on the player quest component passed in
	def getNextQuest(self):
		if len(self.eligible_quests) > 0:
			return random.choice(self.eligible_quests)
		else:
			return None
		
	def updatePlayerQuests(self):
		player_stats = self.owner.player_stats_comp
		assert(player_stats is not None)
		refreshTime = self.quest_manager.refresh_timer

		for i in range(self.player_quest_max):
			if self.checkCanGetQuest(i, refreshTime):
				new_quest = self.getNextQuest()
				if new_quest is not None:
					self.addQuest(i, self.getNextQuest())
				else:
					break

		quest_count = 0
		completed_count = 0
		self.quest_list = self.quest_list
		for player_quest in self.quest_list:
			if player_quest["is_active"]:
				quest_count += 1

			if player_quest["target_value"] == player_quest["cur_value"]:
				completed_count += 1

		self.active_quest_count = quest_count
		if completed_count > 0: 
			if self.client_initialized and self.owner.client and self.client:
				self.client.rspQuestCompleteAlert()
			else:
				self.queued_alerts["complete_quest"] += 1

	def checkCanGetQuest(self, index, refreshTime):
		player_quest = self.quest_list[index]
		if player_quest["is_active"]:
			return False

		curTime = time.time()
		can_get_new_quest = player_quest["start_time"] == 0 or curTime - player_quest["complete_time"] > refreshTime
		free_refresh_available = curTime - self.free_quest_refresh_time > refreshTime
		if not can_get_new_quest and free_refresh_available:
			self.free_quest_refresh_time = int(curTime)
			return free_refresh_available

		return can_get_new_quest
	
	# for match based quests, we check the stats and save their progress directly
	def UpdateMatchBasedQuests(self, battle_info):
		for player_quest in self.quest_list:
			tracked_stat = player_quest["tracked_stat"]
			params = tracked_stat.split(":")
			if params[0] == "match_kills":
				total_kills = 0
				if len(params[1]) == 0:
					for _, kill_count in battle_info.kill_stats.items():
						total_kills += kill_count
				else:
					total_kills += battle_info.kill_stats[params[1]] if params[1] in battle_info.kill_stats.keys() else 0
				# reset progress because these quest progress do not persist.
				player_quest["cur_value"] = int(total_kills)
			
			if params[0] == "match_damage":
				total_damage = 0
				if len(params[1]) == 0:
					for _, damage_stat in battle_info.damage_stats.items():
						total_damage += damage_stat
				else:
					total_damage += battle_info.damage_stats[params[1]] if params[1] in battle_info.kill_stats.keys() else 0
					
				# reset progress because these quest progress do not persist.
				player_quest["cur_value"] = int(total_damage)
			
			if params[0] == "player_match_rank":
				if battle_info.rank <= 5:
					player_quest["cur_value"] += 1

	def resetRollTimer(self):
		self.last_reroll_time = 0

	def disableAllQuests(self):
		for player_quest in self.quest_list:
			player_quest["is_active"] = False
			player_quest["complete_time"] = int(time.time())
		self.quest_list = self.quest_list

	def overrideAndRefreshQuests(self):
		for player_quest in self.quest_list:
			player_quest["complete_time"] = 0
			player_quest["start_time"] = 0
			player_quest["is_active"] = False
		
		self.updatePlayerQuests()
		self.quest_list = self.quest_list

	def setQuestCooldown(self, timer):
		for player_quest in self.quest_list:
			player_quest["complete_time"] = int(time.time()) + timer - self.quest_manager.refresh_timer
			player_quest["is_active"] = False
		
		self.setupQuestTimers()
		self.quest_list = self.quest_list

	def setQuestComplete(self, index):
		player_quest = self.quest_list[index]
		player_quest["cur_value"] = player_quest["target_value"]
		player_quest["complete_time"] = int(time.time());
		self.quest_list = self.quest_list

		self.updatePlayerQuests()

	def reqQuestAlert(self):
		self.client_initialized = True
		if self.queued_alerts["new_quest"] > 0:
			self.client.rspNewQuestAlert()
		if self.queued_alerts["complete_quest"] > 0:
			self.client.rspQuestCompleteAlert()

		self.queued_alerts = {"new_quest" : 0, "complete_quest" : 0}


		
