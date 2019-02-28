import KBEngine
class Achievement():
	instance = None
	data_achievement_chains = {}

	data_properties = {
		"uid" 			: "id",
		"display_name" 	: "Achieve_Name",
		"desc" 			: "Achieve_Describe",
		"tag" 			: "TabTag",
		"requirements" 	: "Required",
		"next_chain" 	: "PostAchieve",
		"objective"		: "TaskObject",  
		"target_count" 	: {"TaskTarget" : "TaskCount"}, # TODO Make regex and parse through all similar tables
		"reward"		: {"RewardType" : "Reward_Count"},
		"cooldown"		: "Interval",
		"duration"		: "Duration",
		"is_daily"		: "Daily_Bool",
		"is_event"		: "EventQuest",
		"is_locked"		: "LockType",
		"is_hidden"		: "HiddenType",
		"is_enabled"	: "EnabledFlag",
		"is_cumulative"	: "Cumulative",
		"icon_image"	: "ArtID",
		"client_popup"	: "UnlockUI"
	}
	
	def __init__(self):
		self.data_map = {}

	def getNext(self):
		if self.next_chain is None:
			return None
		
		return  Achievement.getByUID(Achievement.data_achievement_chains[self.next_chain])
	
	@staticmethod
	def getInstance():
		if not Achievement.instance and not KBEngine.globalData.has_key("Achievement"):
			Achievement.instance = Achievement()
			KBEngine.globalData["Achievement"] = Achievement.instance
		
		return KBEngine.globalData["Achievement"]
	
	@staticmethod
	def setInstance():
		KBEngine.globalData["Achievement"] = Achievement.instance

	@staticmethod
	def setup():
		Achievement.setupAchievementChains()
	
	@staticmethod
	def setupAchievementChains():
		Achievement.data_achievement_chains = {}
		for ach_uid, ach_data in Achievement.getInstance().data_map.items():
			if ach_data.next_chain is not None:
				Achievement.data_achievement_chains[ach_uid] = ach_data.next_chain

	@staticmethod
	def getByUID(uid):
		if uid in Achievement.getInstance().data_map:
			return Achievement.getInstance().data_map[uid]

		return None

	@staticmethod
	def getByTag(tag):
		tagged_achievements = []
		for ach_uid, ach_data in Achievement.getInstance().data_map:
			if len(set(ach_data.tag).intersection(tag)):
				tagged_achievements.append(ach_uid)
		return tagged_achievements
	
	@staticmethod
	def getAll():
		return Achievement.getInstance().data_map
	
	@staticmethod
	def require():
		pass
