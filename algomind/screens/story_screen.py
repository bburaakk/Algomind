import os
import tempfile
import threading
from functools import partial
import httpx  # HTTP istek için
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

        self.story_api_url = "http://35.202.188.175:8080/story/"
        self.tts_api_url = "http://35.202.188.175:8080/tts/"

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

        threading.Thread(target=self.fetch_and_speak_story_thread, args=(topic,), daemon=True).start()

    def fetch_and_speak_story_thread(self, topic):
        try:
            # 1. API'ye uygun prompt oluştur
            prompt_text = (
                f"Lütfen sadece çocuklara yönelik, eğitici ve yaratıcı bir hikaye yaz. "
                f"Hikayenin konusu: {topic}.\n\n"
                "Hikayede başlık da olsun. Sadece hikaye içeriği ver, yorum ya da açıklama ekleme.\n\n"
                "Örnek gibi:\n\n"
                "Tavşan Pamuk ve Sincap Fındık(başlık)\n\n"
                "Yeşil bir ormanda, Tavşan Pamuk yaşarmış...\n\n"
                "Başlığı yazdıktan sonra bir satır aşağıya geç\n\n"
                "ve maksimum 1000 karakterli olsun\n\n"
                "Format şöyle olsun:\n\n"
                "**Başlık**\n\n"
                "(Bir satır boşluk bırak)\n\n"
                "Hikaye içeriği buraya gelsin...\n\n"
                "Hikayelerde Elif ismini kullanma\n\n"
                "Vızzz gibi ttsnin okuyamayacağı şeyler yazma"
            )

            # 2. Story API'ye POST et
            with httpx.Client(timeout=30) as client:
                response = client.post(self.story_api_url, json={"prompt": prompt_text})

            if response.status_code != 200:
                raise Exception(f"Story API error: {response.status_code} {response.text}")

            story = response.json().get("story", "")
            lines = story.strip().split('\n')

            title = ""
            if lines and "**" in lines[0]:
                title = lines[0].replace("**", "").strip()
                story_body = "\n".join(lines[2:]).strip()
            else:
                story_body = story

            self.story_title = title
            self.story_text = story_body

            Clock.schedule_once(partial(self.update_story_ui, title, story_body))

            # 3. TTS için metni hazırla ve API çağrısı yap
            text_to_speak = f"{self.story_title}. {self.story_text}"
            text_to_speak = text_to_speak[:5000]  # API limit

            with httpx.Client(timeout=30) as client:
                tts_response = client.post(self.tts_api_url, json={"text": text_to_speak})

            if tts_response.status_code != 200:
                raise Exception(f"TTS API error: {tts_response.status_code} {tts_response.text}")

            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            temp_file.write(tts_response.content)
            temp_file.close()
            self.temp_files.append(temp_file.name)

            Clock.schedule_once(partial(self.play_audio, temp_file.name))

        except Exception as e:
            Clock.schedule_once(partial(self.show_error, f"Bir hata oluştu: {e}"))
        finally:
            Clock.schedule_once(self.deactivate_ui)

    def update_story_ui(self, title, story_body, *args):
        self.ids.story_label.text = f"[b]{title}[/b]\n\n{story_body}"
        self.ids.scroll.scroll_y = 1

    def play_audio(self, audio_file, *args):
        self.sound = SoundLoader.load(audio_file)
        if self.sound:
            self.sound.play()
            self.ids.play_btn.disabled = False
        else:
            self.show_error("Ses dosyası oynatılamadı.")

    def show_error(self, error_message, *args):
        self.ids.story_label.text = f"[color=ff0000]{error_message}[/color]"

    def deactivate_ui(self, *args):
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