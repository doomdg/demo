from DataLoader import DataLoader
from StaticData.Quest import Quest
from StaticData.Achievement import Achievement
import KBEngine
from KBEDebug import *
import sys


class StaticData():
	instance = None
	static_data_list = {
		"Quest" : "data_quests",
		"Achievement" : "data_achievements"}

	def __init__(self):
		self.all_uids = {}
		self.warm()

	@staticmethod
	def getInstance():
		if not StaticData.instance:
			StaticData.instance = StaticData()
		
		return StaticData.instance

	@staticmethod
	def str_to_class(classname):
		return getattr(sys.modules[__name__], classname)

	def warm(self):
		ERROR_MSG("Static Data")
		for class_name, data_path in StaticData.static_data_list.items():
			data_sheet = DataLoader.getInstance().getData(data_path)
			if data_sheet is not None:
				data_class = StaticData.str_to_class(class_name)
				data_instance = data_class.getInstance()
				self.all_uids[class_name] = []
				for uid, value in data_sheet.items():
					data_object = data_class()
					for prop, col_name in data_class.data_properties.items():
						if isinstance(col_name, str):
							value = data_sheet[uid].get(col_name)
							values = value.split(";") if hasattr(value, "split") else []
							is_array = len(values) > 1
							setattr(data_object, prop, values if is_array else value)

						elif isinstance(col_name, dict):
							for k, v in col_name.items():
								key = k
								value = v
							
							setattr(data_object, prop, {data_sheet[uid].get(key) : data_sheet[uid].get(value)})
					
					self.all_uids[class_name].append(data_object.uid)
					data_instance.data_map[data_object.uid] = data_object
				
				if hasattr(data_class, "setup"):
					data_class.setup()
				data_class.setInstance()
				
			print("Importing " + class_name + " : " + str(len(data_class.getInstance().data_map)) + " rows")

	@staticmethod
	def getByUID(uid):
		for class_name, uids in StaticData.instance.all_uids:
			if uid in uids:
				data_class = StaticData.str_to_class(class_name)
				return data_class.getByUID(uid)
		
		return None
	
	@staticmethod
	def require():
		pass
