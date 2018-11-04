from sublime_db.core.typecheck import List

import os
import sublime

from sublime_db import ui, core
from sublime_db.main.components.variable_component import VariableComponent, Variable, VariableComponent

class EventLogVariable (ui.Component):
	def __init__(self, variable: Variable) -> None:
		super().__init__()
		self.variables = [] #type: List[Variable]
		# We exand this variabble right away. 
		# It seems that console messages that have a variable reference are an array of variables to display
		# the names of those variables are their index...
		@core.async
		def onVariables() -> core.awaitable[None]:
			self.variables = yield from variable.adapter.GetVariables(variable.reference)
			self.dirty()
		core.run(onVariables())

	def render(self) -> ui.components:
		items = []
		for v in self.variables:
			# we replace the name with the value... since the name is a number
			# this seems to be what vscode does
			v.name = v.value
			v.value = ''
			items.append(VariableComponent(v))
		return items


class EventLogComponent (ui.Component):
	def __init__(self):
		super().__init__()
		self.items = [] #type: List[ui.Component]
		self.text = [] #type: List[str]
	def get_text (self) -> str:
		return ''.join(self.text)
	def open_in_view(self) -> None:
		file = sublime.active_window().new_file()
		file.run_command('append', {
			'characters' : self.get_text(),
			'scroll_to_end' : True
		})
	def AddVariable(self, variable: Variable) -> None:
		self.text.append(variable.name)
		self.text.append(' = ')
		self.text.append(variable.value)

		item = EventLogVariable(variable)
		self.items.append(item)
		self.dirty()

	def Add(self, text: str) -> None:
		self.text.append(text)
		for line in reversed(text.rstrip('\n').split('\n')):
			item = ui.Label(line, color = 'secondary')
			self.items.append(item)
		self.dirty()

	def AddStdout(self, text: str) -> None:
		self.text.append(text)
		for line in reversed(text.rstrip('\n').split('\n')):
			item = ui.Label(line, color = 'primary')
			self.items.append(item)
		self.dirty()

	def AddStderr(self, text: str) -> None:
		self.text.append(text)
		for line in reversed(text.rstrip('\n').split('\n')):
			item = ui.Label(line, color = 'red')
			self.items.append(item)
		self.dirty()

	def clear(self) -> None:
		self.items.clear()
		self.text.clear()
		self.dirty()

	def render (self) -> ui.components:
		items = list(reversed(self.items[-25:]))
		return [
			ui.HorizontalSpacer(300),
			ui.Panel(items = [
				ui.Segment(items = [
					ui.Button(self.open_in_view, [
						ui.Label('Event Log')
					])
				]),
				ui.Table(items = items)
			])
		]