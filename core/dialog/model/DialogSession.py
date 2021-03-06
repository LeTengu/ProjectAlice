from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from paho.mqtt.client import MQTTMessage

from core.base.model import Intent
from core.commons import constants


@dataclass
class DialogSession:
	siteId: str
	sessionId: str = ''
	user: str = constants.UNKNOWN_USER
	message: MQTTMessage = None
	intentName: str = ''
	notUnderstood: int = 0
	currentState: str = constants.DEFAULT
	isAPIGenerated: bool = False
	slots: dict = field(default_factory=dict)
	slotsAsObjects: dict = field(default_factory=dict)
	customData: dict = field(default_factory=dict)
	payload: dict = field(default_factory=dict)
	intentHistory: list = field(default_factory=list)
	intentFilter: list = field(default_factory=list)


	def extend(self, message: MQTTMessage, sessionId: str = None):
		if sessionId:
			self.sessionId = sessionId

		from core.commons.CommonsManager import CommonsManager
		self.message = message
		self.intentName = message.topic
		self.payload = CommonsManager.payload(message)
		self.slots = CommonsManager.parseSlots(message)
		self.slotsAsObjects = CommonsManager.parseSlotsToObjects(message)
		self.customData = CommonsManager.parseCustomData(message)


	def update(self, message: MQTTMessage):
		from core.commons.CommonsManager import CommonsManager
		self.message = message
		self.intentName = message.topic
		self.payload = CommonsManager.payload(message)
		self.slots.update(CommonsManager.parseSlots(message))
		self.slotsAsObjects.update(CommonsManager.parseSlotsToObjects(message))
		self.customData.update(CommonsManager.parseCustomData(message))


	def reviveOldSession(self, session: DialogSession):
		"""
		Revives old session keeping siteId, sessionId and isAPIGenerated from the
		new session
		"""
		self.payload = session.payload
		self.slots = session.slots
		self.slotsAsObjects = session.slotsAsObjects
		self.customData = session.customData
		self.user = session.user
		self.message = session.message
		self.intentName = session.intentName
		self.intentHistory = session.intentHistory
		self.intentFilter = session.intentFilter
		self.notUnderstood = session.notUnderstood
		self.currentState = session.currentState
		self.isAPIGenerated = session.isAPIGenerated


	def slotValue(self, slotName: str, index: int = 0, defaultValue: Any = None) -> Any:
		"""
		This returns the slot master value, not what was heard / captured
		"""
		try:
			return self.slotsAsObjects[slotName][index].value['value']
		except (KeyError, IndexError):
			return defaultValue


	def slotRawValue(self, slotName: str) -> str:
		"""
		This returns the slot raw value, what whas really heard / captured, so it can be a synonym for example
		"""
		return self.slots.get(slotName, '')


	def addToHistory(self, intent: Intent):
		self.intentHistory.append(intent)


	@property
	def previousIntent(self) -> Optional[Intent]:
		return self.intentHistory[-1] if self.intentHistory else None
