"""
Auto Lock Timer Application
Copyright (c) 2025 Ahmed Selim Salama
All rights reserved.

This software is the exclusive property of Ahmed Selim Salama.
No part of this software may be reproduced, distributed, or transmitted
in any form or by any means without the prior written permission of the owner.
"""

import kivy
from kivy.config import Config
Config.set('graphics', 'width', '1000')
Config.set('graphics', 'height', '800')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
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
import schedule
import json
import os
import subprocess
import sys
from plyer import notification
import psutil

class AutoLockApp(App):
    """
    Auto Lock Timer Application
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
        # ScrollView للتأكد من ظهور كل المحتوى
        scroll = ScrollView(do_scroll_x=False, do_scroll_y=True)
        
        # التخطيط الرئيسي مع مساحات مضبوطة
        main_layout = BoxLayout(
            orientation='vertical', 
            padding=[30, 30, 30, 30], 
            spacing=25,
            size_hint_y=None
        )
        # ربط الارتفاع بالمحتوى
        main_layout.bind(minimum_height=main_layout.setter('height'))
        
        # العنوان الرئيسي مع حقوق الملكية
        header_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=140,
            spacing=5
        )
        
        title = Label(
            text='Auto Lock Timer Pro',
            font_size='32sp',
            color=(1, 1, 1, 1),
            bold=True,
            size_hint_y=None,
            height=60
        )
        
        subtitle = Label(
            text='Smart Device Protection System',
            font_size='16sp',
            color=(0.8, 0.8, 0.8, 1),
            size_hint_y=None,
            height=30
        )
        
        # إضافة حقوق الملكية في الواجهة
        copyright_label = Label(
            text='Copyright (c) 2025 Ahmed Selim Salama',
            font_size='12sp',
            color=(0.6, 0.6, 0.6, 1),
            size_hint_y=None,
            height=25
        )
        
        header_layout.add_widget(title)
        header_layout.add_widget(subtitle)
        header_layout.add_widget(copyright_label)
        main_layout.add_widget(header_layout)
        
        # خط فاصل
        separator1 = Label(
            text='=' * 50,
            color=(0.5, 0.5, 0.5, 1),
            size_hint_y=None,
            height=20
        )
        main_layout.add_widget(separator1)
        
        # قسم إعدادات الوقت
        time_section = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=150,
            spacing=15
        )
        
        time_title = Label(
            text='Schedule Settings',
            font_size='20sp',
            color=(0.9, 0.9, 1, 1),
            bold=True,
            size_hint_y=None,
            height=40
        )
        time_section.add_widget(time_title)
        
        # إدخال الوقت مع تخطيط أفضل
        time_input_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=60,
            spacing=20
        )
        
        # ساعة
        hour_layout = BoxLayout(orientation='vertical', spacing=5)
        hour_layout.add_widget(Label(
            text='Hour',
            color=(0.8, 0.8, 0.8, 1),
            size_hint_y=None,
            height=25
        ))
        
        self.hour_input = TextInput(
            text=str(self.get_saved_hour()),
            multiline=False,
            input_filter='int',
            background_color=(0.3, 0.3, 0.3, 1),
            foreground_color=(1, 1, 1, 1),
            font_size='18sp',
            halign='center',
            size_hint_y=None,
            height=40
        )
        hour_layout.add_widget(self.hour_input)
        time_input_layout.add_widget(hour_layout)
        
        # نقطتان
        time_input_layout.add_widget(Label(
            text=':',
            color=(1, 1, 1, 1),
            font_size='24sp',
            bold=True,
            size_hint_x=None,
            width=30
        ))
        
        # دقيقة
        minute_layout = BoxLayout(orientation='vertical', spacing=5)
        minute_layout.add_widget(Label(
            text='Minute',
            color=(0.8, 0.8, 0.8, 1),
            size_hint_y=None,
            height=25
        ))
        
        self.minute_input = TextInput(
            text=str(self.get_saved_minute()),
            multiline=False,
            input_filter='int',
            background_color=(0.3, 0.3, 0.3, 1),
            foreground_color=(1, 1, 1, 1),
            font_size='18sp',
            halign='center',
            size_hint_y=None,
            height=40
        )
        minute_layout.add_widget(self.minute_input)
        time_input_layout.add_widget(minute_layout)
        
        time_section.add_widget(time_input_layout)
        main_layout.add_widget(time_section)
        
        # خط فاصل
        separator2 = Label(
            text='=' * 50,
            color=(0.5, 0.5, 0.5, 1),
            size_hint_y=None,
            height=20
        )
        main_layout.add_widget(separator2)
        
        # قسم التحكم
        control_section = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=100,
            spacing=15
        )
        
        control_title = Label(
            text='Timer Control',
            font_size='20sp',
            color=(0.9, 0.9, 1, 1),
            bold=True,
            size_hint_y=None,
            height=40
        )
        control_section.add_widget(control_title)
        
        # مفتاح التفعيل
        switch_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=50,
            spacing=20
        )
        
        switch_layout.add_widget(Label(
            text='Enable Auto Lock:',
            color=(0.9, 0.9, 0.9, 1),
            font_size='18sp',
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
            text='=' * 50,
            color=(0.5, 0.5, 0.5, 1),
            size_hint_y=None,
            height=20
        )
        main_layout.add_widget(separator3)
        
        # أزرار العمليات
        buttons_section = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=180,
            spacing=15
        )
        
        buttons_title = Label(
            text='Actions',
            font_size='20sp',
            color=(0.9, 0.9, 1, 1),
            bold=True,
            size_hint_y=None,
            height=40
        )
        buttons_section.add_widget(buttons_title)
        
        # الصف الأول من الأزرار
        buttons_row1 = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=60,
            spacing=15
        )
        
        save_btn = Button(
            text='Save Settings',
            background_color=(0.2, 0.8, 0.3, 1),
            color=(1, 1, 1, 1),
            font_size='16sp',
            bold=True
        )
        save_btn.bind(on_press=self.save_timer_settings)
        buttons_row1.add_widget(save_btn)
        
        lock_now_btn = Button(
            text='Lock Now',
            background_color=(0.8, 0.3, 0.3, 1),
            color=(1, 1, 1, 1),
            font_size='16sp',
            bold=True
        )
        lock_now_btn.bind(on_press=self.lock_device_now)
        buttons_row1.add_widget(lock_now_btn)
        
        buttons_section.add_widget(buttons_row1)
        
        # الصف الثاني من الأزرار
        close_apps_btn = Button(
            text='Close All Apps',
            size_hint_y=None,
            height=60,
            background_color=(0.9, 0.6, 0.2, 1),
            color=(1, 1, 1, 1),
            font_size='16sp',
            bold=True
        )
        close_apps_btn.bind(on_press=self.close_all_apps)
        buttons_section.add_widget(close_apps_btn)
        
        main_layout.add_widget(buttons_section)
        
        # خط فاصل
        separator4 = Label(
            text='=' * 50,
            color=(0.5, 0.5, 0.5, 1),
            size_hint_y=None,
            height=20
        )
        main_layout.add_widget(separator4)
        
        # قسم الحالة
        status_section = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=300,
            spacing=15
        )
        
        status_title = Label(
            text='System Status',
            font_size='20sp',
            color=(0.9, 0.9, 1, 1),
            bold=True,
            size_hint_y=None,
            height=40
        )
        status_section.add_widget(status_title)
        
        self.status_label = Label(
            text=self.get_status_text(),
            color=(0.8, 0.9, 1, 1),
            font_size='14sp',
            halign='center',
            valign='top',
            size_hint_y=None,
            height=250
        )
        # ربط text_size بعرض الـ label
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
        """تفعيل أو إلغاء تفعيل المؤقت"""
        self.is_timer_active = value
        if value:
            self.start_timer()
            self.show_notification("Timer Enabled", "Device will lock at scheduled time")
        else:
            self.stop_timer()
            self.show_notification("Timer Disabled", "Auto lock cancelled")
    
    def save_timer_settings(self, instance):
        """حفظ إعدادات المؤقت"""
        try:
            hour = int(self.hour_input.text) if self.hour_input.text else 23
            minute = int(self.minute_input.text) if self.minute_input.text else 0
            
            # التحقق من صحة الوقت
            if not (0 <= hour <= 23) or not (0 <= minute <= 59):
                self.show_popup("Error", "Please enter valid time\n(Hour: 0-23, Minute: 0-59)")
                return
            
            self.scheduled_time = f"{hour:02d}:{minute:02d}"
            
            # حفظ الإعدادات مع حقوق الملكية
            settings = {
                'scheduled_time': self.scheduled_time,
                'is_active': self.is_timer_active,
                'hour': hour,
                'minute': minute,
                'developer': 'Ahmed Selim Salama',
                'copyright': '2025 Ahmed Selim Salama - All rights reserved'
            }
            
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
            
            self.show_popup("Success", f"Settings saved successfully!\nLock time: {self.scheduled_time}")
            
            # إعادة تشغيل المؤقت إذا كان مفعل
            if self.is_timer_active:
                self.start_timer()
                
        except ValueError:
            self.show_popup("Error", "Please enter valid numbers for time")
    
    def load_settings(self):
        """تحميل الإعدادات المحفوظة"""
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
        """بدء المؤقت"""
        if not self.scheduled_time:
            return
            
        # إيقاف المؤقت السابق
        self.stop_timer()
        
        # مسح الجدولة السابقة
        schedule.clear()
        
        # جدولة المهمة الجديدة
        schedule.every().day.at(self.scheduled_time).do(self.execute_lock_sequence)
        
        # بدء خيط المؤقت
        self.timer_thread = threading.Thread(target=self.run_scheduler, daemon=True)
        self.timer_thread.start()
        
        print(f"Timer started for: {self.scheduled_time}")
        print("Auto Lock Timer - Developed by Ahmed Selim Salama")
    
    def stop_timer(self):
        """إيقاف المؤقت"""
        schedule.clear()
        print("Timer stopped")
    
    def run_scheduler(self):
        """تشغيل المجدول في خيط منفصل"""
        while self.is_timer_active and schedule.get_jobs():
            schedule.run_pending()
            time.sleep(1)
    
    def execute_lock_sequence(self):
        """تنفيذ تسلسل القفل"""
        try:
            # إشعار قبل القفل بـ 30 ثانية
            self.show_notification(
                "Warning: Device will lock", 
                "Device will lock in 30 seconds"
            )
            
            # انتظار 30 ثانية
            time.sleep(30)
            
            # إغلاق التطبيقات
            self.close_all_apps(None)
            
            # انتظار قليل
            time.sleep(2)
            
            # قفل الجهاز
            self.lock_device_now(None)
            
        except Exception as e:
            print(f"Error in lock sequence: {e}")
    
    def close_all_apps(self, instance):
        """إغلاق كل التطبيقات غير الأساسية"""
        try:
            # قائمة العمليات التي لا يجب إغلاقها
            protected_processes = [
                'explorer.exe', 'winlogon.exe', 'csrss.exe', 'smss.exe',
                'wininit.exe', 'services.exe', 'lsass.exe', 'svchost.exe',
                'dwm.exe', 'conhost.exe', 'python.exe', 'pythonw.exe'
            ]
            
            closed_count = 0
            
            for proc in psutil.process_iter(['pid', 'name', 'exe']):
                try:
                    proc_name = proc.info['name'].lower()
                    
                    # تجاهل العمليات المحمية
                    if any(protected in proc_name for protected in protected_processes):
                        continue
                    
                    # إغلاق العملية
                    proc.terminate()
                    closed_count += 1
                    
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            
            self.show_notification(
                "Apps Closed", 
                f"Successfully closed {closed_count} applications"
            )
            
        except Exception as e:
            print(f"Error closing apps: {e}")
    
    def lock_device_now(self, instance):
        """قفل الجهاز فوراً"""
        try:
            # إشعار قبل القفل
            self.show_notification("Locking Device", "Device will lock now")
            
            # قفل الجهاز باستخدام Windows API
            if sys.platform == "win32":
                import ctypes
                ctypes.windll.user32.LockWorkStation()
            else:
                # للأنظمة الأخرى
                subprocess.run(['gnome-screensaver-command', '--lock'], check=False)
                
        except Exception as e:
            print(f"Error locking device: {e}")
            # طريقة بديلة
            try:
                subprocess.run(['rundll32.exe', 'user32.dll,LockWorkStation'], check=False)
            except:
                pass
    
    def show_notification(self, title, message):
        """عرض إشعار"""
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
        """عرض نافذة منبثقة"""
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        message_label = Label(
            text=message, 
            color=(1, 1, 1, 1),
            font_size='16sp',
            halign='center',
            valign='middle'
        )
        # ضبط text_size للنافذة المنبثقة أيضاً
        message_label.bind(width=lambda *x: message_label.setter('text_size')(message_label, (message_label.width, None)))
        content.add_widget(message_label)
        
        close_btn = Button(
            text='OK', 
            size_hint_y=None, 
            height=50,
            background_color=(0.2, 0.6, 0.9, 1),
            color=(1, 1, 1, 1),
            font_size='16sp',
            bold=True
        )
        content.add_widget(close_btn)
        
        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.7, 0.5),
            auto_dismiss=False
        )
        
        close_btn.bind(on_press=popup.dismiss)
        popup.open()
    
    def get_status_text(self):
        """الحصول على نص الحالة الحالية"""
        if not self.is_timer_active:
            return "Timer Status: DISABLED\n\nThe auto-lock feature is currently turned off.\nEnable the timer to protect your device.\n\nDeveloped by Ahmed Selim Salama"
        
        if not self.scheduled_time:
            return "Timer Status: NO TIME SET\n\nPlease set a lock time and save settings.\n\nDeveloped by Ahmed Selim Salama"
        
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        
        # حساب الوقت المتبقي
        try:
            target_hour, target_minute = map(int, self.scheduled_time.split(':'))
            target_time = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
            
            if target_time <= now:
                target_time += timedelta(days=1)
            
            time_remaining = target_time - now
            hours, remainder = divmod(time_remaining.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            
            return f"Timer Status: ACTIVE\n\nCurrent Time: {current_time}\nLock Scheduled: {self.scheduled_time}\nTime Remaining: {hours:02d}:{minutes:02d}:{seconds:02d}\n\nYour device will be automatically locked and secured at the scheduled time.\n\nDeveloped by Ahmed Selim Salama"
            
        except Exception as e:
            return f"Timer Status: ERROR\n\nTime calculation error: {e}\n\nDeveloped by Ahmed Selim Salama"
    
    def update_status(self, dt):
        """تحديث نص الحالة"""
        self.status_label.text = self.get_status_text()

# تشغيل التطبيق
if __name__ == '__main__':
    print("Auto Lock Timer Application")
    print("Copyright (c) 2025 Ahmed Selim Salama")
    print("All rights reserved.")
    print("=" * 50)
    AutoLockApp().run()
