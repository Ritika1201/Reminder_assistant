# mate.py
import sys
import random
import os
import time
from PySide6.QtWidgets import QWidget, QLabel, QApplication, QVBoxLayout, QHBoxLayout, QPushButton, QGraphicsOpacityEffect
from PySide6.QtCore import QTimer, Qt, QPoint, QSize
from PySide6.QtGui import QPixmap

class TextBubblePopup(QWidget):
    def __init__(self, parent_mate):
        super().__init__()
        self.mate = parent_mate
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.SubWindow)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.container = QWidget(self)
        self.container.setObjectName("ContainerBox")
        self.container.setStyleSheet("""
            QWidget#ContainerBox {
                background-color: rgba(20, 20, 25, 0.95);
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 12px;
            }
        """)
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(10, 10, 10, 10)
        
        self.bubble_label = QLabel(self)
        self.bubble_label.setWordWrap(True)
        self.bubble_label.setAlignment(Qt.AlignCenter)
        self.bubble_label.setStyleSheet("QLabel { color: #FFFFFF; font-family: 'Segoe UI'; font-size: 11px; font-weight: 500; }")
        container_layout.addWidget(self.bubble_label)
        
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignCenter)
        
        self.yes_btn = QPushButton(self)
        self.yes_btn.setStyleSheet(self.get_button_style("#4CAF50", "#45a049"))
        self.yes_btn.clicked.connect(self.on_yes_clicked)
        button_layout.addWidget(self.yes_btn)
        
        container_layout.addLayout(button_layout)
        layout.addWidget(self.container)
        self.setFixedSize(230, 115)
        self.hide()

    def get_button_style(self, main_color, hover_color):
        return f"QPushButton {{ background-color: {main_color}; color: white; border-radius: 6px; font-size: 11px; font-weight: bold; padding: 6px 14px; min-width: 100px; }} QPushButton:hover {{ background-color: {hover_color}; }}"

    def display_text(self, text, x_pos, y_pos):
        yes_phrases = ["✅ Yeah", "✅ Thanks Beautiful", "✅ Yeah cutie", "✅ Okay", "✅ Done , Diva"]
        self.yes_btn.setText(random.choice(yes_phrases))
        self.bubble_label.setText(text)
        self.move(x_pos, y_pos)
        self.show()

    def on_yes_clicked(self):
        self.hide()
        self.mate.resume_remaining_action()


class RiyaDesktopMate(QWidget):
    def __init__(self, frames_directory):
        super().__init__()
        self.frames_dir = os.path.abspath(frames_directory)
        self.frames_buffer = []
        self.current_frame_idx = 0
        
        self.mate_width = 180
        self.mate_height = 250
        self.alert_interval_ms = 90*60*1000
        
        self.reminder_messages = [
            "💧 Hey! Time to drink up some water. ✨",
            "👀 Look away! There is a glass of water.",
            "🧘 Stay hydrated!!"
            "👐🏻Sweetie ! Take a sip of water..."
            "❕❕ No scrolling until u take a sip.."
        ]
        
        self.start_timestamp = 0.0
        self.init_desktop_layer()
        self.load_frames_directly()  
        self.start_routine_timer()
        
    def init_desktop_layer(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.SubWindow)
        # Clean pure background mode active
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setFixedSize(self.mate_width, self.mate_height)
        
        self.character_canvas = QLabel(self)
        self.character_canvas.setGeometry(0, 0, self.mate_width, self.mate_height)
        self.character_canvas.setAlignment(Qt.AlignCenter)
        self.character_canvas.setStyleSheet("QLabel { background: transparent; padding: 0px; margin: 0px; }")
        
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.character_canvas.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(0.0) 
        
        self.text_bubble = TextBubblePopup(self)
        
        screen_geo = QApplication.primaryScreen().geometry()
        taskbar_offset = 60
        self.active_pos = QPoint(screen_geo.width() - self.mate_width - 20, screen_geo.height() - self.mate_height - taskbar_offset)
        self.move(self.active_pos)
        
        self.loop_timer = QTimer(self)
        self.loop_timer.timeout.connect(self.render_next_pixel_frame)

    def load_frames_directly(self):
        self.frames_buffer = []
        if not os.path.exists(self.frames_dir):
            print(f"[-] Error: Path '{self.frames_dir}' nahi mila!")
            return
            
        all_files = sorted(os.listdir(self.frames_dir))
        files = [os.path.join(self.frames_dir, f) for f in all_files if f.lower().endswith('.png')]
        
        if not files:
            print("[-] Error: Folder me koi images nahi mili!")
            return

        print(f"[✔] Total Frames Loaded: {len(files)}")
        target_size = QSize(self.mate_width, self.mate_height)
        
        for f in files:
            pixmap = QPixmap()
            pixmap.load(f) 
            if not pixmap.isNull():
                scaled = pixmap.scaled(target_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.frames_buffer.append(scaled)

    def start_routine_timer(self):
        self.routine_timer = QTimer(self)
        self.routine_timer.timeout.connect(self.trigger_entrance)
        self.routine_timer.start(self.alert_interval_ms)

    def render_next_pixel_frame(self):
        if not self.frames_buffer:
            return
            
        total_frames = len(self.frames_buffer)
        
        if self.current_frame_idx < total_frames:
            self.character_canvas.setPixmap(self.frames_buffer[self.current_frame_idx])
            
            # Smooth entrance fade
            if self.current_frame_idx <= 77:
                elapsed_time = (time.time() - self.start_timestamp) * 1000.0
                if elapsed_time <= 1500.0:
                    self.opacity_effect.setOpacity(min(1.0, elapsed_time / 1500.0))
                else:
                    self.opacity_effect.setOpacity(1.0)
            
            # STRICT FREEZE CHECKPOINT AT FRAME 78
            if self.current_frame_idx == 77:
                self.loop_timer.stop()
                self.opacity_effect.setOpacity(1.0)
                self.show_popup_message()
                return  
            
            # Exit wrap tracking near frame 101
            fade_out_start = max(78, total_frames - 5)
            if self.current_frame_idx >= fade_out_start:
                remaining_steps = max(1, total_frames - fade_out_start)
                current_step = self.current_frame_idx - fade_out_start
                self.opacity_effect.setOpacity(max(0.0, 1.0 - (current_step / remaining_steps)))
            
            self.current_frame_idx += 1
        else:
            self.loop_timer.stop()
            self.on_sequence_complete()

    def trigger_entrance(self):
        if not self.frames_buffer:
            return
        self.opacity_effect.setOpacity(0.0) 
        self.show()
        self.current_frame_idx = 0 
        self.start_timestamp = time.time()
        self.loop_timer.start(55) 

    def show_popup_message(self):
        selected_msg = random.choice(self.reminder_messages)
        popup_x = self.pos().x() + (self.mate_width // 2) - 115
        popup_y = self.pos().y() - 110
        self.text_bubble.display_text(selected_msg, popup_x, popup_y)

    def resume_remaining_action(self):
        total_frames = len(self.frames_buffer)
        if total_frames > 78:
            self.current_frame_idx = 78  
            self.loop_timer.start(55)
        else:
            self.on_sequence_complete()     

    def on_sequence_complete(self):
        self.hide()
        self.opacity_effect.setOpacity(0.0)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    riya_mate = RiyaDesktopMate(os.path.join(current_dir, "frames"))
    QTimer.singleShot(2000, riya_mate.trigger_entrance) 
    sys.exit(app.exec())