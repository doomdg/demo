import KBEngine

class Quest():
	instance = None

	data_properties = {
		"uid" 			: "id",
		"display_name" 	: "Achieve_Name",
		"desc" 			: "Achieve_Describe",
		"tag" 			: "TabTag",
		"requirements" 	: "Required",
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
		"is_timed"		: "UseDuration",
		"icon_image"	: "ArtID"
	}
	
	def __init__(self):
		self.data_map = {} 

	@staticmethod
	def getByUID(uid):
		if uid in Quest.getInstance().data_map:
			return Quest.getInstance().data_map[uid]

		return None
	
	@staticmethod
	def getInstance():
		if not Quest.instance and not KBEngine.globalData.has_key("Quest"):
			Quest.instance = Quest()
			KBEngine.globalData["Quest"] = Quest.instance
		
		return KBEngine.globalData["Quest"]

	@staticmethod
	def setInstance():
		KBEngine.globalData["Quest"] = Quest.instance
		
	@staticmethod
	def getByTag(tag):
		tagged_quests = []
		for quest_uid, quest_data in Quest.getInstance().data_map:
			if len(set(quest_data.tag).intersection(tag)):
				tagged_quests.append(quest_uid)
		return tagged_quests
	
	@staticmethod
	def getAll():
		return Quest.getInstance().data_map
	
	@staticmethod
	def require():
		pass
