"""
Auto Lock Timer Application - Portrait Mode
Copyright (c) 2025 Ahmed Selim Salama
All rights reserved.
"""

import kivy
from kivy.config import Config
Config.set('graphics', 'width', '360')
Config.set('graphics', 'height', '640')
Config.set('graphics', 'orientation', 'portrait')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.switch import Switch
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from datetime import datetime, timedelta
import threading
import time
import json
import os
from plyer import notification
import platform

class AutoLockApp(App):
    """
    Auto Lock Timer Application - Portrait Mode
    Developer: Ahmed Selim Salama
    """
    
    def __init__(self):
        super().__init__()
        self.scheduled_time = None
        self.is_timer_active = False
        self.timer_thread = None
        self.settings_file = "auto_lock_settings.json"
        self.load_settings()
        
    def build(self):
        scroll = ScrollView(do_scroll_x=False, do_scroll_y=True)
        
        main_layout = BoxLayout(
            orientation='vertical', 
            padding=[15, 20, 15, 20], 
            spacing=15,
            size_hint_y=None
        )
        main_layout.bind(minimum_height=main_layout.setter('height'))
        
        # العنوان الرئيسي
        header_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=100,
            spacing=5
        )
        
        title = Label(
            text='Auto Lock Timer Pro',
            font_size='22sp',
            color=(1, 1, 1, 1),
            bold=True,
            size_hint_y=None,
            height=40
        )
        
        subtitle = Label(
            text='Smart Device Protection System',
            font_size='12sp',
            color=(0.8, 0.8, 0.8, 1),
            size_hint_y=None,
            height=25
        )
        
        copyright_label = Label(
            text='Copyright (c) 2025 Ahmed Selim Salama',
            font_size='9sp',
            color=(0.6, 0.6, 0.6, 1),
            size_hint_y=None,
            height=20
        )
        
        header_layout.add_widget(title)
        header_layout.add_widget(subtitle)
        header_layout.add_widget(copyright_label)
        main_layout.add_widget(header_layout)
        
        # خط فاصل
        separator1 = Label(
            text='=' * 30,
            color=(0.5, 0.5, 0.5, 1),
            size_hint_y=None,
            height=15
        )
        main_layout.add_widget(separator1)
        
        # قسم إعدادات الوقت
        time_section = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=120,
            spacing=10
        )
        
        time_title = Label(
            text='Schedule Settings',
            font_size='18sp',
            color=(0.9, 0.9, 1, 1),
            bold=True,
            size_hint_y=None,
            height=30
        )
        time_section.add_widget(time_title)
        
        # إدخال الوقت
        time_input_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=50,
            spacing=10
        )
        
        time_input_layout.add_widget(Label(
            text='Hour:',
            color=(0.8, 0.8, 0.8, 1),
            font_size='14sp',
            size_hint_x=0.25
        ))
        
        self.hour_input = TextInput(
            text=str(self.get_saved_hour()),
            multiline=False,
            input_filter='int',
            background_color=(0.3, 0.3, 0.3, 1),
            foreground_color=(1, 1, 1, 1),
            font_size='16sp',
            size_hint_x=0.25,
            halign='center'
        )
        time_input_layout.add_widget(self.hour_input)
        
        time_input_layout.add_widget(Label(
            text='Minute:',
            color=(0.8, 0.8, 0.8, 1),
            font_size='14sp',
            size_hint_x=0.25
        ))
        
        self.minute_input = TextInput(
            text=str(self.get_saved_minute()),
            multiline=False,
            input_filter='int',
            background_color=(0.3, 0.3, 0.3, 1),
            foreground_color=(1, 1, 1, 1),
            font_size='16sp',
            size_hint_x=0.25,
            halign='center'
        )
        time_input_layout.add_widget(self.minute_input)
        
        time_section.add_widget(time_input_layout)
        main_layout.add_widget(time_section)
        
        # خط فاصل
        separator2 = Label(
            text='=' * 30,
            color=(0.5, 0.5, 0.5, 1),
            size_hint_y=None,
            height=15
        )
        main_layout.add_widget(separator2)
        
        # قسم التحكم
        control_section = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=80,
            spacing=10
        )
        
        control_title = Label(
            text='Timer Control',
            font_size='18sp',
            color=(0.9, 0.9, 1, 1),
            bold=True,
            size_hint_y=None,
            height=30
        )
        control_section.add_widget(control_title)
        
        # مفتاح التفعيل
        switch_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=40,
            spacing=10
        )
        
        switch_layout.add_widget(Label(
            text='Enable Auto Lock:',
            color=(0.9, 0.9, 0.9, 1),
            font_size='14sp',
            size_hint_x=0.7
        ))
        
        self.timer_switch = Switch(
            active=self.is_timer_active,
            size_hint_x=0.3
        )
        self.timer_switch.bind(active=self.on_timer_switch)
        switch_layout.add_widget(self.timer_switch)
        
        control_section.add_widget(switch_layout)
        main_layout.add_widget(control_section)
        
        # خط فاصل
        separator3 = Label(
            text='=' * 30,
            color=(0.5, 0.5, 0.5, 1),
            size_hint_y=None,
            height=15
        )
        main_layout.add_widget(separator3)
        
        # أزرار العمليات
        buttons_section = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=170,
            spacing=10
        )
        
        buttons_title = Label(
            text='Actions',
            font_size='18sp',
            color=(0.9, 0.9, 1, 1),
            bold=True,
            size_hint_y=None,
            height=30
        )
        buttons_section.add_widget(buttons_title)
        
        save_btn = Button(
            text='Save Settings',
            background_color=(0.2, 0.8, 0.3, 1),
            color=(1, 1, 1, 1),
            font_size='14sp',
            bold=True,
            size_hint_y=None,
            height=45
        )
        save_btn.bind(on_press=self.save_timer_settings)
        buttons_section.add_widget(save_btn)
        
        notification_btn = Button(
            text='Test Notification',
            background_color=(0.2, 0.6, 0.9, 1),
            color=(1, 1, 1, 1),
            font_size='14sp',
            bold=True,
            size_hint_y=None,
            height=45
        )
        notification_btn.bind(on_press=self.test_notification)
        buttons_section.add_widget(notification_btn)
        
        info_btn = Button(
            text='App Info',
            background_color=(0.6, 0.4, 0.8, 1),
            color=(1, 1, 1, 1),
            font_size='14sp',
            bold=True,
            size_hint_y=None,
            height=45
        )
        info_btn.bind(on_press=self.show_app_info)
        buttons_section.add_widget(info_btn)
        
        main_layout.add_widget(buttons_section)
        
        # خط فاصل
        separator4 = Label(
            text='=' * 30,
            color=(0.5, 0.5, 0.5, 1),
            size_hint_y=None,
            height=15
        )
        main_layout.add_widget(separator4)
        
        # قسم الحالة
        status_section = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=220,
            spacing=10
        )
        
        status_title = Label(
            text='System Status',
            font_size='18sp',
            color=(0.9, 0.9, 1, 1),
            bold=True,
            size_hint_y=None,
            height=30
        )
        status_section.add_widget(status_title)
        
        self.status_label = Label(
            text=self.get_status_text(),
            color=(0.8, 0.9, 1, 1),
            font_size='11sp',
            halign='center',
            valign='top',
            size_hint_y=None,
            height=180
        )
        self.status_label.bind(width=lambda *x: self.status_label.setter('text_size')(self.status_label, (self.status_label.width, None)))
        
        status_section.add_widget(self.status_label)
        main_layout.add_widget(status_section)
        
        # بدء المؤقت إذا كان مفعل
        if self.is_timer_active:
            self.start_timer()
            
        # تحديث الحالة كل ثانية
        Clock.schedule_interval(self.update_status, 1.0)
        
        scroll.add_widget(main_layout)
        return scroll
    
    def get_saved_hour(self):
        if self.scheduled_time:
            return int(self.scheduled_time.split(':')[0])
        return 23
    
    def get_saved_minute(self):
        if self.scheduled_time:
            return int(self.scheduled_time.split(':')[1])
        return 0
    
    def on_timer_switch(self, instance, value):
        self.is_timer_active = value
        if value:
            self.start_timer()
            self.show_notification("Timer Enabled", "Timer activated successfully")
        else:
            self.stop_timer()
            self.show_notification("Timer Disabled", "Timer deactivated")
    
    def save_timer_settings(self, instance):
        try:
            hour = int(self.hour_input.text) if self.hour_input.text else 23
            minute = int(self.minute_input.text) if self.minute_input.text else 0
            
            if not (0 <= hour <= 23) or not (0 <= minute <= 59):
                self.show_popup("Error", "Please enter valid time\n(Hour: 0-23, Minute: 0-59)")
                return
            
            self.scheduled_time = f"{hour:02d}:{minute:02d}"
            
            settings = {
                'scheduled_time': self.scheduled_time,
                'is_active': self.is_timer_active,
                'hour': hour,
                'minute': minute,
                'developer': 'Ahmed Selim Salama',
                'copyright': '2025 Ahmed Selim Salama - All rights reserved',
                'platform': platform.system(),
                'version': '2.1'
            }
            
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
            
            self.show_popup("Success", f"Settings saved successfully!\nLock time: {self.scheduled_time}")
            
            if self.is_timer_active:
                self.start_timer()
                
        except ValueError:
            self.show_popup("Error", "Please enter valid numbers")
    
    def load_settings(self):
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    self.scheduled_time = settings.get('scheduled_time', '23:00')
                    self.is_timer_active = settings.get('is_active', False)
        except Exception as e:
            print(f"Error loading settings: {e}")
            self.scheduled_time = '23:00'
            self.is_timer_active = False
    
    def start_timer(self):
        if not self.scheduled_time:
            return
            
        self.stop_timer()
        self.is_timer_active = True
        
        self.timer_thread = threading.Thread(target=self.run_timer, daemon=True)
        self.timer_thread.start()
        
        print(f"Timer started for: {self.scheduled_time}")
    
    def stop_timer(self):
        self.is_timer_active = False
        print("Timer stopped")
    
    def run_timer(self):
        while self.is_timer_active:
            now = datetime.now()
            current_time = now.strftime("%H:%M")
            
            if current_time == self.scheduled_time:
                self.execute_lock_sequence()
                break
                
            time.sleep(30)
    
    def execute_lock_sequence(self):
        try:
            self.show_notification(
                "Auto Lock Activated", 
                "Device protection sequence initiated by Ahmed Selim Salama App"
            )
            
        except Exception as e:
            print(f"Error in lock sequence: {e}")
    
    def test_notification(self, instance):
        self.show_notification("Test Notification", "Notifications are working correctly!\nApp by Ahmed Selim Salama")
    
    def show_app_info(self, instance):
        info_text = "Auto Lock Timer Pro v2.1\n\nDeveloper: Ahmed Selim Salama\nCopyright: 2025\nPlatform: " + platform.system() + "\n\nThis app helps protect your device by scheduling automatic notifications at specified times."
        self.show_popup("App Information", info_text)
    
    def show_notification(self, title, message):
        try:
            notification.notify(
                title=title,
                message=message,
                app_name="Auto Lock Pro - Ahmed Selim Salama",
                timeout=5
            )
        except Exception as e:
            print(f"Notification error: {e}")
    
    def show_popup(self, title, message):
        content = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        message_label = Label(
            text=message, 
            color=(1, 1, 1, 1),
            font_size='12sp',
            halign='center',
            valign='middle'
        )
        message_label.bind(width=lambda *x: message_label.setter('text_size')(message_label, (message_label.width, None)))
        content.add_widget(message_label)
        
        close_btn = Button(
            text='OK', 
            size_hint_y=None, 
            height=40,
            background_color=(0.2, 0.6, 0.9, 1),
            color=(1, 1, 1, 1),
            font_size='14sp',
            bold=True
        )
        content.add_widget(close_btn)
        
        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.85, 0.5),
            auto_dismiss=False
        )
        
        close_btn.bind(on_press=popup.dismiss)
        popup.open()
    
    def get_status_text(self):
        platform_info = f"Platform: {platform.system()}"
        
        if not self.is_timer_active:
            return f"Timer Status: DISABLED\n\nThe auto-lock feature is currently turned off.\nEnable the timer to activate protection.\n\n{platform_info}\n\nDeveloped by Ahmed Selim Salama\nVersion 2.1"
        
        if not self.scheduled_time:
            return f"Timer Status: NO TIME SET\n\nPlease set a lock time and save settings.\n\n{platform_info}\n\nDeveloped by Ahmed Selim Salama\nVersion 2.1"
        
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        
        try:
            target_hour, target_minute = map(int, self.scheduled_time.split(':'))
            target_time = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
            
            if target_time <= now:
                target_time += timedelta(days=1)
            
            time_remaining = target_time - now
            hours, remainder = divmod(time_remaining.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            
            return f"Timer Status: ACTIVE\n\nCurrent Time: {current_time}\nScheduled Time: {self.scheduled_time}\nTime Remaining: {hours:02d}:{minutes:02d}:{seconds:02d}\n\nYour device will receive a notification at the scheduled time.\n\n{platform_info}\n\nDeveloped by Ahmed Selim Salama\nVersion 2.1"
            
        except Exception as e:
            return f"Timer Status: ERROR\n\nTime calculation error: {e}\n\n{platform_info}\n\nDeveloped by Ahmed Selim Salama\nVersion 2.1"
    
    def update_status(self, dt):
        self.status_label.text = self.get_status_text()

if __name__ == '__main__':
    print("Auto Lock Timer Application - Portrait Mode")
    print("Copyright (c) 2025 Ahmed Selim Salama")
    print("Platform:", platform.system())
    print("Version: 2.1")
    print("=" * 50)
    AutoLockApp().run()
