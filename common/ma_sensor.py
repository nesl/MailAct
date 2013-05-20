class SensorObject(object):
	''' Sensor Object: name, matching criteria, extractions, func file  '''
	def __init__(self, name, match_crit, extract, actions):
		self.name = name
		self.match_crit = match_crit
		self.extract = extract
		self.actions = actions
