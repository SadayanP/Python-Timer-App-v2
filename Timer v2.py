# Version 2 of Timer

import sys
import time
from enum import Enum, auto

from PyQt5.QtCore import QObject, QTimer, Qt
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QSpinBox
)
from PyQt5.QtCore import pyqtSignal


class TimerState(Enum):
    STOPPED = auto()
    RUNNING = auto()
    PAUSED = auto()
    FINISHED = auto()


class TimerModel:
    def __init__(self):
        self.duration = 0
        self.end_time = 0
        self.remaining = 0


class TimerViewModel(QObject):
    time_changed = pyqtSignal(str)
    state_changed = pyqtSignal(object)
    button_text_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.model = TimerModel()
        self.state = TimerState.STOPPED
        self.timer = QTimer()
        self.timer.timeout.connect(self.tick)

    def start(self, duration):
        if self.state == TimerState.RUNNING or duration <= 0:
            return

        self.model.duration = duration
        self.model.end_time = time.monotonic() + duration

        self.state = TimerState.RUNNING
        self.state_changed.emit(self.state)
        self.button_text_changed.emit("Pause")
        self.timer.start(200)

    def pause(self):
        if self.state != TimerState.RUNNING:
            return

        self.model.remaining = self.model.end_time - time.monotonic()
        self.timer.stop()

        self.state = TimerState.PAUSED
        self.state_changed.emit(self.state)
        self.button_text_changed.emit("Resume")

    def resume(self):
        if self.state != TimerState.PAUSED:
            return

        self.model.end_time = time.monotonic() + self.model.remaining

        self.state = TimerState.RUNNING
        self.state_changed.emit(self.state)
        self.button_text_changed.emit("Pause")
        self.timer.start(200)

    def stop(self):
        self.timer.stop()
        self.state = TimerState.STOPPED
        self.state_changed.emit(self.state)
        self.button_text_changed.emit("Start")

    def tick(self):
        remaining = self.model.end_time - time.monotonic()

        if remaining <= 0:
            self.timer.stop()
            self.state = TimerState.FINISHED
            self.state_changed.emit(self.state)
            self.time_changed.emit("00:00:00")
            self.button_text_changed.emit("Start")
            return

        h = int(remaining // 3600)
        m = int((remaining % 3600) // 60)
        s = int(remaining % 60)

        self.time_changed.emit(f"{h:02d}:{m:02d}:{s:02d}")
        
    def reset(self):
        self.time_changed.emit("00:00:00")
        self.button_text_changed.emit("Start")
        self.model.end_time = 0
        self.model.remaining = 0
        self.model.duration = 0
        self.state = TimerState.STOPPED
        self.state_changed.emit(self.state)
        self.timer.stop()


class View(QMainWindow):
    def __init__(self, vm):
        super().__init__()
        self.vm = vm

        self.setWindowTitle("Sleek Timer")
        self.setFixedSize(380, 450) # Keep the app structured and gadget-like
        
       

        # Global Premium Dark Stylesheet
        self.setStyleSheet("""
            QMainWindow {
                background-color: #121214;
            }
            QLabel#TitleLabel {
                color: #6c7d93;
                font-family: 'Segoe UI', Helvetica, Arial;
                font-size: 14px;
                font-weight: bold;
                letter-spacing: 2px;
                text-transform: uppercase;
            }
            QLabel#ClockLabel {
                color: #ffffff;
                font-family: 'Consolas', 'Courier New', monospace; /* Monospace prevents numbers jumping widths */
                font-size: 56px;
                font-weight: bold;
            }
            QSpinBox {
                background-color: #1a1a1e;
                border: 2px solid #2a2a30;
                border-radius: 8px;
                color: #ffffff;
                font-family: 'Segoe UI', Arial;
                font-size: 18px;
                padding: 8px;
                min-width: 80px;
            }
            QSpinBox:focus {
                border: 2px solid #00adb5;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 20px;
                background-color: transparent;
            }
            QPushButton {
                background-color: #00adb5;
                border: none;
                border-radius: 10px;
                color: #ffffff;
                font-family: 'Segoe UI', Arial;
                font-size: 18px;
                font-weight: bold;
                padding: 14px;
            }
            QPushButton:hover {
                background-color: #00cfd6;
            }
            QPushButton:pressed {
                background-color: #008c94;
            }
            QPushButton:disabled {
                background-color: #2a2a30;
                color: #6c7d93;
            }
        """)

        # --- UI ELEMENTS ---
        self.title_label = QLabel("Countdown Timer")
        self.title_label.setObjectName("TitleLabel")
        
        self.label = QLabel("00:00:00")
        self.label.setObjectName("ClockLabel")
        
        self.hours = QSpinBox()
        self.hours.setRange(0, 99)
        self.hours.setSuffix(" h")
        self.hours.setAlignment(Qt.AlignCenter)

        self.minutes = QSpinBox()
        self.minutes.setRange(0, 59)
        self.minutes.setSuffix(" m")
        self.minutes.setAlignment(Qt.AlignCenter)

        self.seconds = QSpinBox()
        self.seconds.setRange(0, 59)
        self.seconds.setSuffix(" s")
        self.seconds.setAlignment(Qt.AlignCenter)

        self.button1 = QPushButton("Start")
        self.button2 = QPushButton("Reset")

        # --- LAYOUT DESIGN ---
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(30, 40, 30, 40)
        self.layout.setSpacing(20)
        

        self.input_row = QHBoxLayout()
        self.input_row.setSpacing(12)
        self.input_row.addWidget(self.hours)
        self.input_row.addWidget(self.minutes)
        self.input_row.addWidget(self.seconds)

        # Build clean structural spacing
        self.layout.addWidget(self.title_label, alignment=Qt.AlignCenter)
        self.layout.addStretch()
        self.layout.addWidget(self.label, alignment=Qt.AlignCenter)
        self.layout.addStretch()
        self.layout.addLayout(self.input_row)
        self.layout.addWidget(self.button2)
        self.layout.addWidget(self.button1)
        
        self.button2.hide()


        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

        # --- CONNECTIONS ---
        self.button1.clicked.connect(self.handle_button)
        self.button2.clicked.connect(self.handle_reset)
        self.vm.time_changed.connect(self.label.setText)
        self.vm.button_text_changed.connect(self.button1.setText)
        
        # Connect state changes to handle UI locking mechanics
        self.vm.state_changed.connect(self.handle_state_changed)

    def get_duration(self):
        return (
            self.hours.value() * 3600 +
            self.minutes.value() * 60 +
            self.seconds.value()
        )

    def handle_button(self):
        state = self.vm.state
        if state == TimerState.STOPPED:
            if self.get_duration() > 0:
                self.vm.start(self.get_duration())
                
        elif state == TimerState.RUNNING:
            self.vm.pause()
             
        elif state == TimerState.PAUSED:
            self.vm.resume()
            
    def handle_reset(self):
        self.vm.reset()
        

            
            
    def handle_state_changed(self, state):
        """Disables/Enables inputs depending on whether the clock is ticking"""
        if state in (TimerState.RUNNING, TimerState.PAUSED):
            self.hours.setEnabled(False)
            self.minutes.setEnabled(False)
            self.seconds.setEnabled(False)
            self.button2.show()
        else:
            self.hours.setEnabled(True)
            self.minutes.setEnabled(True)
            self.seconds.setEnabled(True)
            self.button2.hide()
            
            

def main():
    app = QApplication(sys.argv)
    vm = TimerViewModel()
    view = View(vm)
    view.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
    