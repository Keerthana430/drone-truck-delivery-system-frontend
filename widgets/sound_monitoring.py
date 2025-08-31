"""
Sound monitoring widgets for drone noise analysis
"""
import time
import numpy as np
from collections import deque
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QGroupBox, QLabel, 
                           QProgressBar, QGridLayout)
import pyqtgraph as pg

class SoundGraphWidget(QWidget):
    """Real-time drone sound visualization"""
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Waveform graph
        self.waveform_widget = pg.PlotWidget(title="Drone Sound Waveform")
        self.waveform_widget.setBackground('#2d2d2d')
        self.waveform_widget.setLabel('left', 'Amplitude')
        self.waveform_widget.setLabel('bottom', 'Time (ms)')
        self.waveform_curve = self.waveform_widget.plot(pen=pg.mkPen('#ff6b35', width=2))
        
        # Sound level graph
        self.level_widget = pg.PlotWidget(title="Sound Level (dB)")
        self.level_widget.setBackground('#2d2d2d')
        self.level_widget.setLabel('left', 'dB')
        self.level_widget.setLabel('bottom', 'Time')
        self.level_curve = self.level_widget.plot(pen=pg.mkPen('#00ff88', width=2))
        
        layout.addWidget(self.waveform_widget)
        layout.addWidget(self.level_widget)
        
        # Data buffers
        self.waveform_data = np.zeros(50)
        self.level_data = deque(maxlen=60)
        self.time_data = deque(maxlen=60)
        
    def update_sound_data(self, level, waveform):
        """Update both sound graphs"""
        # Update waveform
        self.waveform_data = np.array(waveform)
        self.waveform_curve.setData(self.waveform_data)
        
        # Update level graph
        current_time = time.time()
        self.level_data.append(level)
        self.time_data.append(current_time)
        
        if len(self.level_data) > 1:
            times = np.array(self.time_data) - self.time_data[0]
            levels = np.array(self.level_data)
            self.level_curve.setData(times, levels)

class NoiseStatisticsWidget(QWidget):
    """Display noise statistics and metrics"""
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.reset_stats()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Current readings
        current_group = QGroupBox("Current Readings")
        current_layout = QGridLayout(current_group)
        
        self.current_level = QLabel("-- dB")
        self.current_level.setStyleSheet("font-size: 24px; font-weight: bold; color: #ff6b35;")
        
        current_layout.addWidget(QLabel("Current Level:"), 0, 0)
        current_layout.addWidget(self.current_level, 0, 1)
        
        # Statistics
        stats_group = QGroupBox("Statistics")
        stats_layout = QGridLayout(stats_group)
        
        self.avg_level = QLabel("-- dB")
        self.peak_level = QLabel("-- dB")
        self.min_level = QLabel("-- dB")
        
        self.avg_level.setStyleSheet("font-size: 18px; color: #00ff88;")
        self.peak_level.setStyleSheet("font-size: 18px; color: #ff4757;")
        self.min_level.setStyleSheet("font-size: 18px; color: #3742fa;")
        
        stats_layout.addWidget(QLabel("Average:"), 0, 0)
        stats_layout.addWidget(self.avg_level, 0, 1)
        stats_layout.addWidget(QLabel("Peak:"), 1, 0)
        stats_layout.addWidget(self.peak_level, 1, 1)
        stats_layout.addWidget(QLabel("Minimum:"), 2, 0)
        stats_layout.addWidget(self.min_level, 2, 1)
        
        # Progress bars for levels
        levels_group = QGroupBox("Noise Levels")
        levels_layout = QVBoxLayout(levels_group)
        
        self.current_bar = QProgressBar()
        self.current_bar.setRange(0, 100)
        self.avg_bar = QProgressBar()
        self.avg_bar.setRange(0, 100)
        
        levels_layout.addWidget(QLabel("Current Level"))
        levels_layout.addWidget(self.current_bar)
        levels_layout.addWidget(QLabel("Average Level"))
        levels_layout.addWidget(self.avg_bar)
        
        layout.addWidget(current_group)
        layout.addWidget(stats_group)
        layout.addWidget(levels_group)
        layout.addStretch()
        
    def reset_stats(self):
        self.levels_history = []
        
    def update_statistics(self, current_level):
        """Update noise statistics"""
        self.levels_history.append(current_level)
        
        # Keep only last 100 readings
        if len(self.levels_history) > 100:
            self.levels_history.pop(0)
            
        avg = np.mean(self.levels_history)
        peak = np.max(self.levels_history)
        minimum = np.min(self.levels_history)
        
        self.current_level.setText(f"{current_level:.1f} dB")
        self.avg_level.setText(f"{avg:.1f} dB")
        self.peak_level.setText(f"{peak:.1f} dB")
        self.min_level.setText(f"{minimum:.1f} dB")
        
        # Update progress bars
        self.current_bar.setValue(int(current_level))
        self.avg_bar.setValue(int(avg))