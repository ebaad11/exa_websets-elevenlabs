import os
from dotenv import load_dotenv
import requests

class ElevenLabsTTS:
    def __init__(self, script_file: str, voice_id: str, model_id: str = "eleven_monolingual_v1"):
        # Load .env and grab your API key
        load_dotenv()
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        if not self.api_key:
            raise RuntimeError("ELEVENLABS_API_KEY not found in environment")
        
        self.script_file = script_file
        self.voice_id = voice_id
        self.model_id = model_id
        self.endpoint = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}"

    def generate_audio(
        self,
        output_path: str,
        stability: float = 0.6,
        similarity_boost: float = 0.75,
        style: float = 0.2,
        use_speaker_boost: bool = True
    ) -> str:
        # Read the text you want to synthesize
        with open(self.script_file, "r", encoding="utf-8") as f:
            text = f.read()

        payload = {
            "text": text,
            "model_id": self.model_id,
            "voice_settings": {
                "stability": stability,
                "similarity_boost": similarity_boost,
                "style": style,
                "use_speaker_boost": use_speaker_boost
            }
        }
        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }

        resp = requests.post(self.endpoint, json=payload, headers=headers)
        resp.raise_for_status()

        # Save returned audio bytes to file
        with open(output_path, "wb") as out:
            out.write(resp.content)

        return output_path
