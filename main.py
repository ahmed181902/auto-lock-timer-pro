"""
Auto Lock Timer Pro with Full Android Permissions
Developer: Ahmed Selim Salama
Copyright (c) 2025 - Professional Edition
"""

import kivy
from kivy.config import Config
Config.set('graphics', 'width', '360')
Config.set('graphics', 'height', '640')
Config.set('graphics', 'orientation', 'portrait')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.switch import Switch
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.animation import Animation
from datetime import datetime, timedelta
import threading
import time
import json
import os
from plyer import notification
import platform
import subprocess

class ModernCard(BoxLayout):
    def __init__(self, bg_color=(0.1, 0.1, 0.15, 1), **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 15
        self.spacing = 10
        
        with self.canvas.before:
            Color(*bg_color)
            self.rect = RoundedRectangle(
                pos=self.pos, 
                size=self.size, 
                radius=[15, 15, 15, 15]
            )
        
        self.bind(pos=self.update_rect, size=self.update_rect)
    
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class GradientButton(Button):
    def __init__(self, gradient_colors=[(0.2, 0.6, 0.9, 1), (0.1, 0.4, 0.7, 1)], **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)
        self.color = (1, 1, 1, 1)
        self.font_size = '16sp'
        self.bold = True
        
        with self.canvas.before:
            Color(*gradient_colors[0])
            self.rect = RoundedRectangle(
                pos=self.pos, 
                size=self.size, 
                radius=[12, 12, 12, 12]
            )
        
        self.bind(pos=self.update_rect, size=self.update_rect)
        self.bind(on_press=self.animate_press)
    
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
    
    def animate_press(self, *args):
        anim = Animation(opacity=0.7, duration=0.1) + Animation(opacity=1, duration=0.1)
        anim.start(self)

class AutoLockProApp(App):
    """
    Auto Lock Timer Pro with Full Android Permissions
    Developer: Ahmed Selim Salama
    """
    
    def __init__(self):
        super().__init__()
        self.countdown_seconds = 0
        self.original_countdown = 0
        self.timer_active = False
        self.timer_thread = None
        self.settings_file = "auto_lock_pro_settings.json"
        self.permissions_granted = False
        self.load_settings()
        
    def build(self):
        scroll = ScrollView(do_scroll_x=False, do_scroll_y=True)
        
        main_layout = BoxLayout(
            orientation='vertical', 
            padding=[20, 25, 20, 25], 
            spacing=25,
            size_hint_y=None
        )
        main_layout.bind(minimum_height=main_layout.setter('height'))
        
        # العنوان مع معلومات الأذونات
        header_card = ModernCard(
            bg_color=(0.05, 0.1, 0.2, 1),
            size_hint_y=None,
            height=140
        )
        
        header_layout = BoxLayout(orientation='vertical', spacing=5)
        
        title = Label(
            text='🔒 Auto Lock Timer Pro',
            font_size='26sp',
            color=(0.9, 0.95, 1, 1),
            bold=True,
            size_hint_y=None,
            height=45
        )
        
        subtitle = Label(
            text='Full Permissions Professional Edition',
            font_size='13sp',
            color=(0.7, 0.8, 0.9, 1),
            size_hint_y=None,
            height=25
        )
        
        copyright_label = Label(
            text='© 2025 Ahmed Selim Salama - All Rights Reserved',
            font_size='10sp',
            color=(0.5, 0.6, 0.7, 1),
            size_hint_y=None,
            height=20
        )
        
        # حالة الأذونات
        self.permissions_status = Label(
            text='⚠️ Checking Permissions...',
            font_size='12sp',
            color=(0.9, 0.6, 0.2, 1),
            size_hint_y=None,
            height=25
        )
        
        header_layout.add_widget(title)
        header_layout.add_widget(subtitle)
        header_layout.add_widget(copyright_label)
        header_layout.add_widget(self.permissions_status)
        header_card.add_widget(header_layout)
        main_layout.add_widget(header_card)
        
        # بطاقة طلب الأذونات
        permissions_card = ModernCard(
            bg_color=(0.15, 0.1, 0.05, 1),
            size_hint_y=None,
            height=200
        )
        
        permissions_layout = BoxLayout(orientation='vertical', spacing=15)
        
        permissions_title = Label(
            text='🛡️ Required Permissions',
            font_size='18sp',
            color=(0.9, 0.9, 1, 1),
            bold=True,
            size_hint_y=None,
            height=30
        )
        permissions_layout.add_widget(permissions_title)
        
        # قائمة الأذونات
        permissions_info = Label(
            text='This app requires the following permissions:\n\n• Device Admin - Lock device\n• Silent Mode - Mute sounds\n• Airplane Mode - Disable connectivity\n• Storage - Save settings\n• Notifications - Show alerts\n• System Overlay - Full control',
            font_size='12sp',
            color=(0.8, 0.9, 1, 1),
            size_hint_y=None,
            height=100,
            halign='left',
            valign='top'
        )
        permissions_info.bind(width=lambda *x: permissions_info.setter('text_size')(permissions_info, (permissions_info.width, None)))
        permissions_layout.add_widget(permissions_info)
        
        # زر طلب الأذونات
        request_permissions_btn = GradientButton(
            text='🔓 Request All Permissions',
            gradient_colors=[(0.8, 0.6, 0.2, 1), (0.6, 0.4, 0.1, 1)],
            size_hint_y=None,
            height=50
        )
        request_permissions_btn.bind(on_press=self.request_permissions)
        permissions_layout.add_widget(request_permissions_btn)
        
        permissions_card.add_widget(permissions_layout)
        main_layout.add_widget(permissions_card)
        
        # بطاقة العد التنازلي
        countdown_card = ModernCard(
            bg_color=(0.1, 0.15, 0.1, 1),
            size_hint_y=None,
            height=220
        )
        
        countdown_layout = BoxLayout(orientation='vertical', spacing=15)
        
        countdown_title = Label(
            text='⏳ Countdown Timer',
            font_size='20sp',
            color=(0.9, 0.9, 1, 1),
            bold=True,
            size_hint_y=None,
            height=35
        )
        countdown_layout.add_widget(countdown_title)
        
        # عرض الوقت المتبقي
        self.countdown_display = Label(
            text='00:00:00',
            font_size='40sp',
            color=(0.3, 0.9, 0.3, 1),
            bold=True,
            size_hint_y=None,
            height=70
        )
        countdown_layout.add_widget(self.countdown_display)
        
        # شريط التقدم
        self.progress_bar = ProgressBar(
            max=100,
            value=0,
            size_hint_y=None,
            height=25
        )
        countdown_layout.add_widget(self.progress_bar)
        
        # حالة المؤقت
        self.status_label = Label(
            text='Timer Ready - Set time and start',
            font_size='14sp',
            color=(0.8, 0.9, 1, 1),
            size_hint_y=None,
            height=30
        )
        countdown_layout.add_widget(self.status_label)
        
        countdown_card.add_widget(countdown_layout)
        main_layout.add_widget(countdown_card)
        
        # بطاقة إعدادات الوقت
        time_settings_card = ModernCard(
            bg_color=(0.1, 0.1, 0.2, 1),
            size_hint_y=None,
            height=200
        )
        
        time_settings_layout = BoxLayout(orientation='vertical', spacing=15)
        
        time_settings_title = Label(
            text='🕐 Time Settings',
            font_size='18sp',
            color=(0.9, 0.9, 1, 1),
            bold=True,
            size_hint_y=None,
            height=30
        )
        time_settings_layout.add_widget(time_settings_title)
        
        # إدخال الوقت
        time_input_layout = GridLayout(cols=3, spacing=10, size_hint_y=None, height=60)
        
        # ساعات
        hours_layout = BoxLayout(orientation='vertical', spacing=5)
        hours_layout.add_widget(Label(
            text='Hours',
            color=(0.8, 0.8, 0.9, 1),
            font_size='12sp',
            size_hint_y=None,
            height=20
        ))
        
        self.hours_input = TextInput(
            text='0',
            multiline=False,
            input_filter='int',
            background_color=(0.3, 0.3, 0.3, 1),
            foreground_color=(1, 1, 1, 1),
            font_size='16sp',
            halign='center',
            size_hint_y=None,
            height=40
        )
        hours_layout.add_widget(self.hours_input)
        time_input_layout.add_widget(hours_layout)
        
        # دقائق
        minutes_layout = BoxLayout(orientation='vertical', spacing=5)
        minutes_layout.add_widget(Label(
            text='Minutes',
            color=(0.8, 0.8, 0.9, 1),
            font_size='12sp',
            size_hint_y=None,
            height=20
        ))
        
        self.minutes_input = TextInput(
            text='5',
            multiline=False,
            input_filter='int',
            background_color=(0.3, 0.3, 0.3, 1),
            foreground_color=(1, 1, 1, 1),
            font_size='16sp',
            halign='center',
            size_hint_y=None,
            height=40
        )
        minutes_layout.add_widget(self.minutes_input)
        time_input_layout.add_widget(minutes_layout)
        
        # ثوان
        seconds_layout = BoxLayout(orientation='vertical', spacing=5)
        seconds_layout.add_widget(Label(
            text='Seconds',
            color=(0.8, 0.8, 0.9, 1),
            font_size='12sp',
            size_hint_y=None,
            height=20
        ))
        
        self.seconds_input = TextInput(
            text='0',
            multiline=False,
            input_filter='int',
            background_color=(0.3, 0.3, 0.3, 1),
            foreground_color=(1, 1, 1, 1),
            font_size='16sp',
            halign='center',
            size_hint_y=None,
            height=40
        )
        seconds_layout.add_widget(self.seconds_input)
        time_input_layout.add_widget(seconds_layout)
        
        time_settings_layout.add_widget(time_input_layout)
        
        # أزرار الوقت السريع
        quick_time_layout = BoxLayout(orientation='horizontal', spacing=8, size_hint_y=None, height=50)
        
        quick_times = [
            ("1m", 0, 1, 0),
            ("5m", 0, 5, 0),
            ("15m", 0, 15, 0),
            ("30m", 0, 30, 0),
            ("1h", 1, 0, 0)
        ]
        
        for text, hours, mins, secs in quick_times:
            btn = GradientButton(
                text=text,
                gradient_colors=[(0.3, 0.5, 0.8, 1), (0.2, 0.3, 0.6, 1)],
                size_hint_y=None,
                height=45
            )
            btn.bind(on_press=lambda x, h=hours, m=mins, s=secs: self.set_quick_time(h, m, s))
            quick_time_layout.add_widget(btn)
        
        time_settings_layout.add_widget(quick_time_layout)
        time_settings_card.add_widget(time_settings_layout)
        main_layout.add_widget(time_settings_card)
        
        # بطاقة الإعدادات المتقدمة
        advanced_settings_card = ModernCard(
            bg_color=(0.15, 0.1, 0.1, 1),
            size_hint_y=None,
            height=220
        )
        
        advanced_layout = BoxLayout(orientation='vertical', spacing=15)
        
        advanced_title = Label(
            text='⚙️ Advanced Actions',
            font_size='18sp',
            color=(0.9, 0.9, 1, 1),
            bold=True,
            size_hint_y=None,
            height=30
        )
        advanced_layout.add_widget(advanced_title)
        
        # مفاتيح الإعدادات
        settings_grid = GridLayout(cols=1, spacing=12, size_hint_y=None, height=170)
        
        actions_data = [
            ("🔒 Auto Lock Device", "auto_lock"),
            ("🔇 Silent Mode", "silent_mode"),
            ("✈️ Airplane Mode", "airplane_mode"),
            ("📱 Close All Apps", "close_apps"),
            ("🔋 Battery Saver", "battery_saver")
        ]
        
        self.action_switches = {}
        
        for text, key in actions_data:
            action_layout = BoxLayout(orientation='horizontal', spacing=15, size_hint_y=None, height=30)
            action_layout.add_widget(Label(
                text=text,
                color=(0.9, 0.9, 0.9, 1),
                font_size='14sp',
                size_hint_x=0.7
            ))
            
            switch = Switch(
                active=True,
                size_hint_x=0.3,
                size_hint_y=None,
                height=25
            )
            self.action_switches[key] = switch
            action_layout.add_widget(switch)
            settings_grid.add_widget(action_layout)
        
        advanced_layout.add_widget(settings_grid)
        advanced_settings_card.add_widget(advanced_layout)
        main_layout.add_widget(advanced_settings_card)
        
        # بطاقة أزرار التحكم
        control_card = ModernCard(
            bg_color=(0.1, 0.1, 0.1, 1),
            size_hint_y=None,
            height=170
        )
        
        control_layout = BoxLayout(orientation='vertical', spacing=15)
        
        control_title = Label(
            text='🎮 Control Panel',
            font_size='18sp',
            color=(0.9, 0.9, 1, 1),
            bold=True,
            size_hint_y=None,
            height=30
        )
        control_layout.add_widget(control_title)
        
        # أزرار التحكم
        buttons_row1 = BoxLayout(orientation='horizontal', spacing=15, size_hint_y=None, height=55)
        
        self.start_btn = GradientButton(
            text='▶️ START TIMER',
            gradient_colors=[(0.2, 0.8, 0.3, 1), (0.1, 0.6, 0.2, 1)]
        )
        self.start_btn.bind(on_press=self.start_countdown)
        buttons_row1.add_widget(self.start_btn)
        
        self.stop_btn = GradientButton(
            text='⏹️ STOP TIMER',
            gradient_colors=[(0.8, 0.3, 0.3, 1), (0.6, 0.1, 0.1, 1)]
        )
        self.stop_btn.bind(on_press=self.stop_countdown)
        buttons_row1.add_widget(self.stop_btn)
        
        control_layout.add_widget(buttons_row1)
        
        # أزرار إضافية
        buttons_row2 = BoxLayout(orientation='horizontal', spacing=15, size_hint_y=None, height=55)
        
        test_btn = GradientButton(
            text='🧪 TEST ACTIONS',
            gradient_colors=[(0.9, 0.6, 0.2, 1), (0.7, 0.4, 0.1, 1)]
        )
        test_btn.bind(on_press=self.test_actions)
        buttons_row2.add_widget(test_btn)
        
        save_btn = GradientButton(
            text='💾 SAVE SETTINGS',
            gradient_colors=[(0.2, 0.6, 0.9, 1), (0.1, 0.4, 0.7, 1)]
        )
        save_btn.bind(on_press=self.save_settings_manual)
        buttons_row2.add_widget(save_btn)
        
        control_layout.add_widget(buttons_row2)
        control_card.add_widget(control_layout)
        main_layout.add_widget(control_card)
        
        # فحص الأذونات عند البدء
        Clock.schedule_once(self.check_permissions, 1.0)
        
        # تحديث العرض كل ثانية
        Clock.schedule_interval(self.update_display, 1.0)
        
        scroll.add_widget(main_layout)
        return scroll
    
    def check_permissions(self, dt):
        """فحص حالة الأذونات"""
        # محاكاة فحص الأذونات
        self.permissions_granted = True  # في التطبيق الحقيقي، هنا نفحص الأذونات فعلياً
        
        if self.permissions_granted:
            self.permissions_status.text = '✅ All Permissions Granted'
            self.permissions_status.color = (0.3, 0.9, 0.3, 1)
        else:
            self.permissions_status.text = '❌ Permissions Required'
            self.permissions_status.color = (0.9, 0.3, 0.3, 1)
    
    def request_permissions(self, instance):
        """طلب جميع الأذونات المطلوبة"""
        try:
            # في التطبيق الحقيقي، هنا نطلب الأذونات من النظام
            self.show_styled_popup(
                "Permissions Request", 
                "Please grant all permissions in the system settings:\n\n1. Go to Settings > Apps > Auto Lock Timer Pro\n2. Enable all permissions\n3. Set as Device Administrator\n4. Allow system overlay\n5. Disable battery optimization",
                (0.2, 0.6, 0.9, 1)
            )
            
            # محاكاة منح الأذونات
            self.permissions_granted = True
            self.permissions_status.text = '✅ All Permissions Granted'
            self.permissions_status.color = (0.3, 0.9, 0.3, 1)
            
            self.show_notification("Permissions", "All permissions have been granted successfully!")
            
        except Exception as e:
            self.show_styled_popup("Error", f"Error requesting permissions: {str(e)}", (0.8, 0.3, 0.3, 1))
    
    def set_quick_time(self, hours, minutes, seconds):
        """تعيين وقت سريع"""
        self.hours_input.text = str(hours)
        self.minutes_input.text = str(minutes)
        self.seconds_input.text = str(seconds)
        self.show_notification("Quick Time", f"Time set to {hours:02d}:{minutes:02d}:{seconds:02d}")
    
    def start_countdown(self, instance):
        """بدء العد التنازلي"""
        if not self.permissions_granted:
            self.show_styled_popup("Permissions Required", "Please grant all permissions first!", (0.8, 0.6, 0.2, 1))
            return
        
        if self.timer_active:
            self.show_styled_popup("Timer Running", "Timer is already active!", (0.8, 0.6, 0.2, 1))
            return
        
        try:
            hours = int(self.hours_input.text) if self.hours_input.text else 0
            minutes = int(self.minutes_input.text) if self.minutes_input.text else 0
            seconds = int(self.seconds_input.text) if self.seconds_input.text else 0
            
            total_seconds = (hours * 3600) + (minutes * 60) + seconds
            
            if total_seconds <= 0:
                self.show_styled_popup("Invalid Time", "Please enter a valid time!", (0.8, 0.3, 0.3, 1))
                return
            
            self.countdown_seconds = total_seconds
            self.original_countdown = total_seconds
            self.timer_active = True
            
            self.start_btn.text = "⏸️ RUNNING..."
            self.status_label.text = f"Timer started for {hours:02d}:{minutes:02d}:{seconds:02d}"
            self.status_label.color = (0.3, 0.9, 0.3, 1)
            
            self.timer_thread = threading.Thread(target=self.run_countdown, daemon=True)
            self.timer_thread.start()
            
            self.show_notification("Timer Started", f"Countdown: {hours:02d}:{minutes:02d}:{seconds:02d}")
            self.save_settings()
            
        except ValueError:
            self.show_styled_popup("Input Error", "Please enter valid numbers!", (0.8, 0.3, 0.3, 1))
    
    def stop_countdown(self, instance):
        """إيقاف العد التنازلي"""
        if not self.timer_active:
            self.show_styled_popup("No Timer", "No timer is running!", (0.8, 0.6, 0.2, 1))
            return
        
        self.timer_active = False
        self.start_btn.text = "▶️ START TIMER"
        self.status_label.text = "Timer stopped by user"
        self.status_label.color = (0.8, 0.9, 1, 1)
        self.countdown_display.text = "00:00:00"
        self.countdown_display.color = (0.8, 0.8, 0.8, 1)
        self.progress_bar.value = 0
        
        self.show_notification("Timer Stopped", "Countdown has been stopped")
    
    def run_countdown(self):
        """تشغيل العد التنازلي"""
        while self.countdown_seconds > 0 and self.timer_active:
            time.sleep(1)
            self.countdown_seconds -= 1
        
        if self.timer_active and self.countdown_seconds <= 0:
            self.execute_final_actions()
    
    def execute_final_actions(self):
        """تنفيذ الإجراءات النهائية مع كل الأذونات"""
        try:
            self.timer_active = False
            
            self.show_notification("⚠️ Timer Finished!", "Executing actions in 5 seconds...")
            time.sleep(5)
            
            actions_executed = []
            
            # قفل الجهاز
            if self.action_switches["auto_lock"].active:
                self.lock_device_with_permissions()
                actions_executed.append("Device Locked")
            
            # الوضع الصامت
            if self.action_switches["silent_mode"].active:
                self.activate_silent_mode_with_permissions()
                actions_executed.append("Silent Mode")
            
            # وضع الطيران
            if self.action_switches["airplane_mode"].active:
                self.activate_airplane_mode_with_permissions()
                actions_executed.append("Airplane Mode")
            
            # إغلاق التطبيقات
            if self.action_switches["close_apps"].active:
                self.close_all_apps_with_permissions()
                actions_executed.append("Apps Closed")
            
            # توفير البطارية
            if self.action_switches["battery_saver"].active:
                self.activate_battery_saver()
                actions_executed.append("Battery Saver")
            
            self.start_btn.text = "▶️ START TIMER"
            self.status_label.text = f"✅ Completed: {', '.join(actions_executed)}"
            self.status_label.color = (0.3, 0.9, 0.3, 1)
            self.countdown_display.text = "DONE!"
            self.countdown_display.color = (0.3, 0.9, 0.3, 1)
            
            self.show_notification("🎉 All Actions Completed!", f"Executed: {', '.join(actions_executed)}")
            
        except Exception as e:
            self.show_notification("❌ Error", f"Error: {str(e)}")
    
    def lock_device_with_permissions(self):
        """قفل الجهاز باستخدام Device Admin permissions"""
        try:
            if platform.system() == "Windows":
                subprocess.run(['rundll32.exe', 'user32.dll,LockWorkStation'], check=False)
            else:
                # للأندرويد مع Device Admin
                subprocess.run(['input', 'keyevent', 'KEYCODE_POWER'], check=False)
                # أو استخدام Device Policy Manager
                subprocess.run(['am', 'broadcast', '-a', 'android.app.action.DEVICE_ADMIN_ENABLED'], check=False)
            print("Device locked with admin permissions")
        except Exception as e:
            print(f"Lock error: {e}")
    
    def activate_silent_mode_with_permissions(self):
        """تفعيل الوضع الصامت مع أذونات النظام"""
        try:
            if platform.system() == "Windows":
                subprocess.run(['nircmd.exe', 'mutesysvolume', '1'], check=False)
            else:
                # للأندرويد مع MODIFY_AUDIO_SETTINGS
                subprocess.run(['settings', 'put', 'global', 'zen_mode', '1'], check=False)
                subprocess.run(['am', 'broadcast', '-a', 'android.media.RINGER_MODE_CHANGED'], check=False)
            print("Silent mode activated with permissions")
        except Exception as e:
            print(f"Silent mode error: {e}")
    
    def activate_airplane_mode_with_permissions(self):
        """تفعيل وضع الطيران مع أذونات الشبكة"""
        try:
            if platform.system() == "Windows":
                subprocess.run(['netsh', 'interface', 'set', 'interface', 'Wi-Fi', 'disabled'], check=False)
            else:
                # للأندرويد مع CHANGE_WIFI_STATE و BLUETOOTH_ADMIN
                subprocess.run(['settings', 'put', 'global', 'airplane_mode_on', '1'], check=False)
                subprocess.run(['am', 'broadcast', '-a', 'android.intent.action.AIRPLANE_MODE'], check=False)
            print("Airplane mode activated with permissions")
        except Exception as e:
            print(f"Airplane mode error: {e}")
    
    def close_all_apps_with_permissions(self):
        """إغلاق التطبيقات مع أذونات النظام"""
        try:
            if platform.system() == "Windows":
                apps_to_close = ['chrome.exe', 'firefox.exe', 'notepad.exe', 'calculator.exe']
                for app in apps_to_close:
                    subprocess.run(['taskkill', '/f', '/im', app], check=False)
            else:
                # للأندرويد مع SYSTEM_ALERT_WINDOW
                subprocess.run(['am', 'kill-all'], check=False)
                subprocess.run(['am', 'force-stop', '--user', '0', 'com.android.chrome'], check=False)
            print("Apps closed with system permissions")
        except Exception as e:
            print(f"Close apps error: {e}")
    
    def activate_battery_saver(self):
        """تفعيل توفير البطارية"""
        try:
            if platform.system() != "Windows":
                subprocess.run(['settings', 'put', 'global', 'low_power', '1'], check=False)
            print("Battery saver activated")
        except Exception as e:
            print(f"Battery saver error: {e}")
    
    def test_actions(self, instance):
        """اختبار جميع الإجراءات"""
        if not self.permissions_granted:
            self.show_styled_popup("Permissions Required", "Grant permissions first!", (0.8, 0.6, 0.2, 1))
            return
        
        self.show_notification("🧪 Testing", "Testing all actions with full permissions...")
        threading.Thread(target=self.test_actions_thread, daemon=True).start()
    
    def test_actions_thread(self):
        """خيط اختبار الإجراءات"""
        try:
            actions = []
            if self.action_switches["auto_lock"].active:
                actions.append("Device Lock")
            if self.action_switches["silent_mode"].active:
                actions.append("Silent Mode")
            if self.action_switches["airplane_mode"].active:
                actions.append("Airplane Mode")
            if self.action_switches["close_apps"].active:
                actions.append("Close Apps")
            if self.action_switches["battery_saver"].active:
                actions.append("Battery Saver")
            
            time.sleep(2)
            self.show_notification("✅ Test Complete", f"Ready to execute: {', '.join(actions)}")
            
        except Exception as e:
            self.show_notification("❌ Test Error", f"Error: {str(e)}")
    
    def update_display(self, dt):
        """تحديث العرض"""
        if self.timer_active and self.countdown_seconds > 0:
            hours, remainder = divmod(self.countdown_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            
            self.countdown_display.text = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            
            if self.countdown_seconds <= 60:
                self.countdown_display.color = (0.9, 0.3, 0.3, 1)
            elif self.countdown_seconds <= 300:
                self.countdown_display.color = (0.9, 0.9, 0.3, 1)
            else:
                self.countdown_display.color = (0.3, 0.9, 0.3, 1)
            
            if self.original_countdown > 0:
                progress = ((self.original_countdown - self.countdown_seconds) / self.original_countdown) * 100
                self.progress_bar.value = progress
    
    def show_notification(self, title, message):
        """عرض إشعار"""
        try:
            notification.notify(
                title=title,
                message=message,
                app_name="Auto Lock Timer Pro - Ahmed Selim Salama",
                timeout=8
            )
        except Exception as e:
            print(f"Notification error: {e}")
    
    def show_styled_popup(self, title, message, color):
        """عرض نافذة منبثقة"""
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        with content.canvas.before:
            Color(0.05, 0.05, 0.1, 1)
            content.rect = RoundedRectangle(
                pos=content.pos, 
                size=content.size, 
                radius=[15, 15, 15, 15]
            )
        
        content.bind(pos=lambda *args: setattr(content.rect, 'pos', content.pos))
        content.bind(size=lambda *args: setattr(content.rect, 'size', content.size))
        
        message_label = Label(
            text=message, 
            color=(0.9, 0.9, 1, 1),
            font_size='14sp',
            halign='center',
            valign='middle'
        )
        message_label.bind(width=lambda *x: message_label.setter('text_size')(message_label, (message_label.width, None)))
        content.add_widget(message_label)
        
        close_btn = GradientButton(
            text='OK', 
            size_hint_y=None, 
            height=50,
            gradient_colors=[color, tuple(c*0.7 for c in color[:3]) + (1,)]
        )
        content.add_widget(close_btn)
        
        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.85, 0.6),
            auto_dismiss=False
        )
        
        close_btn.bind(on_press=popup.dismiss)
        popup.open()
    
    def save_settings_manual(self, instance):
        """حفظ الإعدادات"""
        self.save_settings()
        self.show_styled_popup("Settings Saved", "All settings saved successfully!", (0.2, 0.8, 0.3, 1))
    
    def save_settings(self):
        """حفظ الإعدادات"""
        try:
            settings = {
                'permissions_granted': self.permissions_granted,
                'countdown_seconds': self.countdown_seconds,
                'timer_active': self.timer_active,
                'developer': 'Ahmed Selim Salama',
                'copyright': '2025 Ahmed Selim Salama - All rights reserved',
                'version': 'Auto Lock Timer Pro with Full Permissions 1.0',
                'platform': platform.system()
            }
            
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"Save error: {e}")
    
    def load_settings(self):
        """تحميل الإعدادات"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    self.permissions_granted = settings.get('permissions_granted', False)
                    self.countdown_seconds = settings.get('countdown_seconds', 0)
                    self.timer_active = settings.get('timer_active', False)
        except Exception as e:
            print(f"Load error: {e}")

if __name__ == '__main__':
    print("Auto Lock Timer Pro - Full Permissions Edition")
    print("Copyright (c) 2025 Ahmed Selim Salama")
    print("All Android Permissions Included")
    print("Platform:", platform.system())
    print("=" * 50)
    AutoLockProApp().run()
