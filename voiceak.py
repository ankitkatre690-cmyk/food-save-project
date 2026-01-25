import speech_recognition as sr
import pyttsx3
import psutil
import pyautogui
import pygetwindow as gw
import time
import os
import subprocess
import threading
from datetime import datetime

class VoiceAssistant:
    def __init__(self):
        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Initialize text-to-speech
        self.tts_engine = pyttsx3.init()
        self.setup_tts()
        
        # Adjust for ambient noise
        print("Adjusting for ambient noise...")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
        
        self.is_listening = False
        self.wake_word = "assistant"
        
    def setup_tts(self):
        """Configure text-to-speech settings"""
        voices = self.tts_engine.getProperty('voices')
        if voices:
            self.tts_engine.setProperty('voice', voices[1].id)  # Female voice
        self.tts_engine.setProperty('rate', 150)
        self.tts_engine.setProperty('volume', 0.8)
    
    def speak(self, text):
        """Convert text to speech"""
        print(f"Assistant: {text}")
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()
    
    def listen(self):
        """Listen for voice input and convert to text"""
        try:
            with self.microphone as source:
                print("Listening...")
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
            
            text = self.recognizer.recognize_google(audio).lower()
            print(f"You said: {text}")
            return text
        except sr.WaitTimeoutError:
            return ""
        except sr.UnknownValueError:
            return ""
        except sr.RequestError as e:
            self.speak("Sorry, there was an error with the speech recognition service")
            return ""
    
    def handle_command(self, command):
        """Process and execute voice commands"""
        command = command.lower()
        
        # System commands
        if any(word in command for word in ["shutdown", "turn off", "power off"]):
            self.speak("Shutting down the system")
            os.system("shutdown /s /t 1" if os.name == 'nt' else "sudo shutdown -h now")
            
        elif any(word in command for word in ["restart", "reboot"]):
            self.speak("Restarting the system")
            os.system("shutdown /r /t 1" if os.name == 'nt' else "sudo reboot")
            
        elif any(word in command for word in ["sleep", "hibernate"]):
            self.speak("Putting system to sleep")
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0" if os.name == 'nt' else "systemctl suspend")
        
        # Volume control
        elif "volume up" in command:
            self.speak("Increasing volume")
            pyautogui.press('volumeup')
            
        elif "volume down" in command:
            self.speak("Decreasing volume")
            pyautogui.press('volumedown')
            
        elif "mute" in command or "unmute" in command:
            self.speak("Toggling mute")
            pyautogui.press('volumemute')
        
        # Application control
        elif "open notepad" in command:
            self.speak("Opening Notepad")
            subprocess.Popen("notepad.exe" if os.name == 'nt' else "gedit")
            
        elif "open calculator" in command:
            self.speak("Opening Calculator")
            subprocess.Popen("calc.exe" if os.name == 'nt' else "gnome-calculator")
            
        elif "open browser" in command or "open chrome" in command:
            self.speak("Opening web browser")
            subprocess.Popen("chrome.exe" if os.name == 'nt' else "google-chrome")
        
        # Window management
        elif "minimize" in command:
            self.speak("Minimizing current window")
            pyautogui.hotkey('win', 'down')
            
        elif "maximize" in command:
            self.speak("Maximizing current window")
            pyautogui.hotkey('win', 'up')
            
        elif "close window" in command:
            self.speak("Closing current window")
            pyautogui.hotkey('alt', 'f4')
        
        # Screen control
        elif "lock screen" in command:
            self.speak("Locking screen")
            pyautogui.hotkey('win', 'l')
            
        elif "take screenshot" in command:
            self.speak("Taking screenshot")
            screenshot = pyautogui.screenshot()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot.save(f"screenshot_{timestamp}.png")
        
        # System information
        elif "battery" in command:
            battery = psutil.sensors_battery()
            if battery:
                percent = battery.percent
                self.speak(f"Battery is at {percent} percent")
            else:
                self.speak("Battery information not available")
                
        elif "memory" in command or "ram" in command:
            memory = psutil.virtual_memory()
            used_gb = memory.used / (1024**3)
            total_gb = memory.total / (1024**3)
            self.speak(f"Memory usage is {used_gb:.1f} gigabytes out of {total_gb:.1f} gigabytes")
            
        elif "cpu" in command:
            cpu_percent = psutil.cpu_percent(interval=1)
            self.speak(f"CPU usage is {cpu_percent} percent")
        
        # Media control
        elif any(word in command for word in ["play", "pause"]):
            self.speak("Toggling play pause")
            pyautogui.press('playpause')
            
        elif "next" in command:
            self.speak("Playing next track")
            pyautogui.press('nexttrack')
            
        elif "previous" in command:
            self.speak("Playing previous track")
            pyautogui.press('prevtrack')
        
        # Help command
        elif "help" in command or "what can you do" in command:
            help_text = """
            I can help you with:
            - System control: shutdown, restart, sleep
            - Volume control: volume up, volume down, mute
            - Application control: open notepad, calculator, browser
            - Window management: minimize, maximize, close window
            - Screen control: lock screen, take screenshot
            - System info: battery, memory, CPU usage
            - Media control: play, pause, next, previous
            """
            self.speak("Here's what I can do. Check the console for details.")
            print(help_text)
        
        else:
            self.speak("Sorry, I didn't understand that command")
    
    def continuous_listen(self):
        """Continuously listen for wake word and commands"""
        self.is_listening = True
        self.speak("Voice assistant activated. Say 'assistant' followed by your command.")
        
        while self.is_listening:
            try:
                with self.microphone as source:
                    print("Waiting for wake word...")
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=3)
                
                text = self.recognizer.recognize_google(audio).lower()
                print(f"Heard: {text}")
                
                if self.wake_word in text:
                    self.speak("Yes? How can I help you?")
                    command = self.listen()
                    if command:
                        self.handle_command(command)
                    else:
                        self.speak("I didn't catch that. Please try again.")
                        
            except sr.WaitTimeoutError:
                continue
            except sr.UnknownValueError:
                continue
            except Exception as e:
                print(f"Error: {e}")
                continue
    
    def command_mode(self):
        """Run in command mode where you speak directly without wake word"""
        self.speak("Command mode activated. Speak your command directly.")
        
        while True:
            command = self.listen()
            if command:
                if "exit" in command or "stop" in command:
                    self.speak("Goodbye!")
                    break
                self.handle_command(command)

def main():
    assistant = VoiceAssistant()
    
    print("Voice Assistant Started!")
    print("Choose mode:")
    print("1. Wake word mode (say 'assistant' to activate)")
    print("2. Command mode (speak directly)")
    
    try:
        choice = input("Enter choice (1 or 2): ").strip()
        
        if choice == "1":
            assistant.continuous_listen()
        elif choice == "2":
            assistant.command_mode()
        else:
            print("Invalid choice. Starting in command mode.")
            assistant.command_mode()
            
    except KeyboardInterrupt:
        print("\nVoice assistant stopped.")
        assistant.speak("Goodbye!")

if __name__ == "__main__":
    main()