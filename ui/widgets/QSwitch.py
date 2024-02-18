#!/usr/bin/env python3

# -*- coding: utf-8 -*-

"""
	QSwitch v.0.0.1 - 2023-12-28 (Python3 / PyQt6 GUI extension)

	This is a new Python 3 / PyQt6 Widget that acts like a checkbox but displays a toggle switch.
	The widget aims to follow the PyQt6 coding guidelines and has - beside PyQt6 - no dependensies.
	The drawing of the switch is completely done with PyQt6 functionality

	Author:		DaVe inc. Kim-David Hauser
	License:	MIT
	Git:		https://github.com/jetedonner/ch.kimhauser.python.helper
	Website:	https://kimhauser.ch
"""
		
from enum import Enum

from PyQt6.QtGui import *
from PyQt6.QtCore import *

from PyQt6.QtWidgets import *
from PyQt6 import uic, QtWidgets

class SwitchSize(Enum):
	Small = 1
	Medium = 2
	Large = 3
	
class SwitchLabelPos(Enum):
	Leading = 1
	Trailing = 2
	Above = 3
	Below = 4
	
class SwitchPrivate(QObject):
	
	currentColor = QColor("blue")
	
	def __init__(self, q, parent=None):
		QObject.__init__(self, parent=parent)
		self.mPointer = q
		self.mPosition = 0.0
		self.mGradient = QLinearGradient()
		self.mGradient.setSpread(QGradient.Spread.PadSpread)
		
		self.animation = QPropertyAnimation(self)
		self.animation.setTargetObject(self)
		self.animation.setPropertyName(b'position')
		self.animation.setStartValue(0.0)
		self.animation.setEndValue(1.0)
		self.animation.setDuration(200)
		self.animation.setEasingCurve(QEasingCurve.Type.InOutExpo)
		
		self.animation.finished.connect(self.mPointer.update)
		
	@pyqtProperty(float)
	def position(self):
		return self.mPosition
	
	@position.setter
	def position(self, value):
		self.mPosition = value
		self.mPointer.update()
		
	def draw(self, painter):
		r = self.mPointer.rect()
		margin = (r.height()/10)
		self.shadow = self.mPointer.palette().color(QPalette.ColorRole.Dark)
		self.light = self.mPointer.palette().color(QPalette.ColorRole.Light)
		self.button = self.mPointer.palette().color(QPalette.ColorRole.Button)
		painter.setPen(Qt.PenStyle.NoPen)
		
		self.mGradient.setColorAt(0, self.currentColor.darker(30))
		self.mGradient.setColorAt(1, self.currentColor.darker(30))
		self.mGradient.setStart(0, r.height())
		self.mGradient.setFinalStop(0, 0)
		painter.setBrush(self.mGradient)
		painter.drawRoundedRect(r, r.height()/2, r.height()/2)
		
		self.mGradient.setColorAt(0, self.shadow.darker(40))
		self.mGradient.setColorAt(1, self.light.darker(60))
		self.mGradient.setStart(0, 0)
		self.mGradient.setFinalStop(0, r.height())
		painter.setBrush(self.mGradient)
		painter.drawRoundedRect(r.adjusted(int(margin), int(margin), int(-margin), int(-margin)), r.height()/2, r.height()/2)
		
		self.mGradient.setColorAt(0, self.light.darker(40))
		self.mGradient.setColorAt(1, self.currentColor)
		
		painter.setBrush(self.mGradient)
		
		marginInner = margin + 2
		x = r.height()/2.0 + self.mPosition*(r.width()-r.height())
		painter.drawEllipse(QPointF(x, r.height()/2), (r.height()/2)-marginInner, (r.height()/2)-marginInner)
		
	@pyqtSlot(bool, name='animate')
	def animate(self, checked):
		if checked:
			self.currentColor = QColor("green")
		else:
			self.currentColor = QColor("blue")
			
		self.animation.setDirection(QPropertyAnimation.Direction.Forward if checked else QPropertyAnimation.Direction.Backward)
		self.animation.start()
		
		
class Switch(QAbstractButton):
	
	checked = pyqtSignal(bool)
	switchSize:SwitchSize = SwitchSize.Small
	
	def __init__(self, switchSize:SwitchSize = SwitchSize.Small, switchChecked = False, parent=None):
		QAbstractButton.__init__(self, parent=parent)
		self._switchChecked = switchChecked
		self.dPtr = SwitchPrivate(self)
		self.switchSize = switchSize
		self.setCheckable(True)
		self.clicked.connect(self.animate)
		self.setSwitchSize(switchSize)
		
	def setSwitchSize(self, switchSize:SwitchSize = SwitchSize.Small):
		fixedSize = QSize(48, 29)
		if self.switchSize == SwitchSize.Small:
			fixedSize = QSize(36, 21)
		elif self.switchSize == SwitchSize.Large:
			fixedSize = QSize(84, 42)
		self.setFixedSize(fixedSize)
	
	@pyqtSlot(bool)
	def animate(self, checked):
		self.setChecked(checked)
		self.dPtr.animate(checked)
		self.checked.emit(checked)
	
	@property
	def switchChecked(self):
		return self._switchChecked
	
	@switchChecked.setter
	def switchChecked(self, new_switchChecked):
		if not isinstance(new_switchChecked, bool):
			raise TypeError('checked must be a bool')
		self._switchChecked = new_switchChecked
		self.setChecked(new_switchChecked)
		self.dPtr.animate(new_switchChecked)
	
	def paintEvent(self, event):
		painter = QPainter(self)
		painter.setRenderHint(QPainter.RenderHint.Antialiasing)
		self.dPtr.draw(painter)
		
	def resizeEvent(self, event):
		self.update()
		
class QSwitch(QWidget):
	
	checked = pyqtSignal(bool)
	
	switchSize:SwitchSize = SwitchSize.Small
	switchLabelPos:SwitchLabelPos = SwitchLabelPos.Trailing
	
	def foo(self, event, **kwargs):
		if self.lblToggleSwitch:
			self.switch.animate(not self.switch.isChecked())
		
	@property
	def lblToggleSwitch(self):
		return self._lblToggleSwitch
	
	@lblToggleSwitch.setter
	def lblToggleSwitch(self, new_lblToggleSwitch):
		if not isinstance(new_lblToggleSwitch, bool):
			raise TypeError('lblToggleSwitch must be a bool')
		self._lblToggleSwitch = new_lblToggleSwitch
			
	def __init__(self, descTxt:str, switchSize:SwitchSize = SwitchSize.Small, switchLabelPos:SwitchLabelPos = SwitchLabelPos.Trailing, lblToggleSwitch = True, parent=None):
		QWidget.__init__(self, parent=parent)
		self.switchLabelPos = switchLabelPos
		self._lblToggleSwitch = lblToggleSwitch
		
		self.switch = Switch(switchSize)
		self.switch.checked.connect(self.checked_changed)
		self.lblDesc = QLabel(descTxt)
		self.lblDesc.mousePressEvent = self.foo
		if self.switchLabelPos == SwitchLabelPos.Leading or self.switchLabelPos == SwitchLabelPos.Trailing:
			self.setLayout(QHBoxLayout())
			if self.switchLabelPos == SwitchLabelPos.Leading:
				self.layout().addWidget(self.lblDesc)
				self.layout().addWidget(self.switch)
			else:
				self.layout().addWidget(self.switch)
				self.layout().addWidget(self.lblDesc)
		else:
			self.setLayout(QVBoxLayout())
			if self.switchLabelPos == SwitchLabelPos.Below:
				self.layout().addWidget(self.switch)
				self.layout().addWidget(self.lblDesc)
			else:
				self.layout().addWidget(self.lblDesc)
				self.layout().addWidget(self.switch)
		self.margin = QMargins(0, 0, 0, 0)
		self.layout().setContentsMargins(self.margin)
	
	def isChecked(self):
		return self.switch.switchChecked

	def setChecked(self, checked):
		self.switch.switchChecked = checked
		
	@pyqtSlot(bool)
	def checked_changed(self, checked):
		self.switch.switchChecked = checked
		self.checked.emit(checked)

class QSwitchDemoWindow(QMainWindow):
	"""PyMobiledevice3GUI's main window (GUI or view)."""
	
	def __init__(self):
		super().__init__()
		self.setWindowTitle("QSwitch - Demo app v0.0.1")
		
		self.layMain = QVBoxLayout()
		self.wdtMain = QWidget()
		self.wdtMain.setLayout(self.layMain)
		
		swtSmallAbove = QSwitch("QSwitch-Small, label above", SwitchSize.Small, SwitchLabelPos.Above)
		swtSmallBelow = QSwitch("QSwitch-Medium, label below", SwitchSize.Medium, SwitchLabelPos.Below)
		swtSmallBefore = QSwitch("QSwitch-Large, label leading", SwitchSize.Large, SwitchLabelPos.Leading)
		swtSmallAfter = QSwitch("QSwitch-Small, label trailing", SwitchSize.Small, SwitchLabelPos.Trailing)

		self.lblDesc = QLabel(f"This is a rought demo of the usage of QSwitch with a mixed matrix of its options")
		self.layMain.addWidget(self.lblDesc)
		
		self.layMain.addWidget(swtSmallAbove)
		self.layMain.addWidget(swtSmallBelow)
		self.layMain.addWidget(swtSmallBefore)
		self.layMain.addWidget(swtSmallAfter)
		self.setCentralWidget(self.wdtMain)

if __name__ == '__main__':
	import sys
	app = QApplication(sys.argv)
	win = QSwitchDemoWindow()
	win.show()
	sys.exit(app.exec())