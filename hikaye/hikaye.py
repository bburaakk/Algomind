import os
import tempfile
import atexit
from create_story import masal_uret
from google.cloud import texttospeech
from kivy.app import App
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle
from kivy.lang import Builder

# Google Cloud TTS credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\eelif\Downloads\btkyarisma-467517-f60dc6263208.json"

Window.clearcolor = (0.95, 0.97, 1, 1)
MAIN_COLOR = (53/255, 122/255, 189/255, 1)

Builder.load_file("hikaye.kv")


class ModernButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)
        self.color = (1, 1, 1, 1)
        self.font_size = '18sp'
        self.markup = True
        self.bind(size=self.update_graphics, pos=self.update_graphics)

    def update_graphics(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*MAIN_COLOR)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[20])


class StoryReader(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.temp_files = []
        self.sound = None
        self.story_title = ""
        self.story_text = ""

    def _on_focus(self, instance, value):
        self.ids.topic_input.halign = 'center'

    def _update_label_height(self, *args):
        self.ids.story_label.height = self.ids.story_label.texture_size[1] + 30

    def generate_story(self, instance):
        if self.sound:
            self.sound.stop()
            self.sound = None

        topic = self.ids.topic_input.text.strip()
        if not topic:
            self.ids.story_label.text = "[color=ff0000]Konu girmeniz gerekiyor![/color]"
            return

        self.ids.story_label.text = "[i]Masal oluşturuluyor...[/i]"
        self.ids.gen_btn.disabled = True
        self.ids.play_btn.disabled = True
        Clock.schedule_once(lambda dt: self.fetch_story(topic), 0.5)

    def fetch_story(self, topic):
        try:
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
            self.ids.story_title_label.text = f"[b]{title}[/b]"
            self.ids.story_label.text = story_body
            self.ids.scroll.scroll_y = 1

            Clock.schedule_once(self.speak_story, 0.5)

        except Exception as e:
            self.ids.story_label.text = f"[color=ff0000]Masal oluşturulamadı: {e}[/color]"
            self.ids.gen_btn.disabled = False

    def speak_story(self, dt):
        try:
            text = f"{self.story_title}. {self.story_text}"
            text = text[:5000]

            client = texttospeech.TextToSpeechClient()
            input_text = texttospeech.SynthesisInput(text=text)

            voice = texttospeech.VoiceSelectionParams(
                language_code="tr-TR",
                name="tr-TR-Wavenet-A",
                ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
            )

            audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)

            response = client.synthesize_speech(input=input_text, voice=voice, audio_config=audio_config)

            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            temp_file.write(response.audio_content)
            temp_file.close()
            self.temp_files.append(temp_file.name)

            self.sound = SoundLoader.load(temp_file.name)
            if self.sound:
                self.sound.play()
                self.ids.play_btn.disabled = False
            else:
                self.ids.story_label.text = "[color=ff0000]Ses oynatılamadı![/color]"
        except Exception as e:
            self.ids.story_label.text = f"[color=ff0000]TTS Hatası: {e}[/color]"
        finally:
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


class MasalApp(App):
    def build(self):
        self.reader = StoryReader()
        return self.reader

    def on_stop(self):
        if hasattr(self, "reader"):
            self.reader.cleanup_temp_files()


if __name__ == "__main__":
    app = MasalApp()
    atexit.register(app.on_stop)
    app.run()
