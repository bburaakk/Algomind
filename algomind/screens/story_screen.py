import os
import tempfile
import threading
from functools import partial
from algomind.helpers import masal_uret
from google.cloud import texttospeech
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivymd.uix.screen import MDScreen


class StoryScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.temp_files = []
        self.sound = None
        self.story_title = ""
        self.story_text = ""

    def generate_story(self, instance):
        if self.sound:
            self.sound.stop()
            self.sound = None

        topic = self.ids.topic_input.text.strip()
        if not topic:
            self.ids.story_label.text = "[color=ff0000]Lütfen bir konu girin.[/color]"
            return

        self.ids.story_label.text = ""
        self.ids.spinner.active = True
        self.ids.gen_btn.disabled = True
        self.ids.play_btn.disabled = True

        # Masal üretme ve seslendirme işlemini arka planda bir thread'de başlat
        threading.Thread(target=self.fetch_and_speak_story_thread, args=(topic,)).start()

    def fetch_and_speak_story_thread(self, topic):
        """
        Bu fonksiyon, masal üretme ve seslendirme işlemlerini
        arka planda ayrı bir iş parçacığında (thread) yürütür.
        """
        try:
            # 1. Masalı üret
            story = masal_uret(topic)
            lines = story.strip().split('\n')
            title = ""
            if lines and "**" in lines[0]:
                title = lines[0].replace("**", "").strip()
                story_body = "\n".join(lines[2:]).strip()
            else:
                story_body = story

            self.story_title = title
            self.story_text = story_body

            # Arayüzü ana iş parçacığında güncelle
            Clock.schedule_once(partial(self.update_story_ui, title, story_body))

            # 2. Masalı seslendir
            text_to_speak = f"{self.story_title}. {self.story_text}"
            text_to_speak = text_to_speak[:5000]  # API limit

            client = texttospeech.TextToSpeechClient()
            input_text = texttospeech.SynthesisInput(text=text_to_speak)
            voice = texttospeech.VoiceSelectionParams(
                language_code="tr-TR", name="tr-TR-Wavenet-A"
            )
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3
            )
            response = client.synthesize_speech(
                input=input_text, voice=voice, audio_config=audio_config
            )

            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            temp_file.write(response.audio_content)
            temp_file.close()
            self.temp_files.append(temp_file.name)

            # Sesi ana iş parçacığında oynat
            Clock.schedule_once(partial(self.play_audio, temp_file.name))

        except Exception as e:
            # Hatayı ana iş parçacığında göster
            Clock.schedule_once(partial(self.show_error, f"Bir hata oluştu: {e}"))
        finally:
            # Spinner'ı ana iş parçacığında devre dışı bırak
            Clock.schedule_once(self.deactivate_ui)

    def update_story_ui(self, title, story_body, *args):
        """Arayüzü güncellemek için ana iş parçacığında çağrılır."""
        self.ids.story_label.text = f"[b]{title}[/b]\n\n{story_body}"
        self.ids.scroll.scroll_y = 1

    def play_audio(self, audio_file, *args):
        """Sesi oynatmak için ana iş parçacığında çağrılır."""
        self.sound = SoundLoader.load(audio_file)
        if self.sound:
            self.sound.play()
            self.ids.play_btn.disabled = False
        else:
            self.show_error("Ses dosyası oynatılamadı.")

    def show_error(self, error_message, *args):
        """Hata mesajını göstermek için ana iş parçacığında çağrılır."""
        self.ids.story_label.text = f"[color=ff0000]{error_message}[/color]"

    def deactivate_ui(self, *args):
        """Spinner'ı durdurup düğmeleri aktif etmek için ana iş parçacığında çağrılır."""
        self.ids.spinner.active = False
        self.ids.gen_btn.disabled = False

    def replay_audio(self, instance):
        if self.sound:
            self.sound.stop()
            self.sound.play()

    def cleanup_temp_files(self):
        for f in self.temp_files:
            try:
                os.remove(f)
            except Exception:
                pass
        self.temp_files.clear()

    def on_stop(self):
        self.cleanup_temp_files()