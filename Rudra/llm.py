import subprocess
import time
import json
import urllib.request
import urllib.error

LM_STUDIO_BASE_URL = "http://localhost:1234/v1"

class LLMEngine:
    def __init__(self, base_url: str = LM_STUDIO_BASE_URL):
        self.base_url = base_url.rstrip("/")
        self.current_model = None

    def check_server_status(self) -> bool:
        """Pings LM Studio local server to see if it is running."""
        try:
            url = f"{self.base_url}/models"
            req = urllib.request.Request(url, headers={"User-Agent": "RudraAI/1.0"})
            with urllib.request.urlopen(req, timeout=3) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    models = data.get("data", [])
                    if models:
                        self.current_model = models[0].get("id")
                    return True
        except Exception:
            return False
        return False

    def start_lms_server(self) -> bool:
        """Attempts to start LM Studio local server using 'lms' CLI."""
        print("[+] LM Studio server not detected. Attempting auto-start via 'lms' CLI...")
        try:
            subprocess.Popen(["lms", "server", "start"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            print("[+] Waiting for LM Studio server to come online...", end="", flush=True)
            for _ in range(12):
                time.sleep(1)
                print(".", end="", flush=True)
                if self.check_server_status():
                    print("\n[+] LM Studio server started successfully!")
                    return True
            print("\n[-] Server start timed out. Please ensure LM Studio local server is started manually.")
            return False
        except FileNotFoundError:
            print("\n[-] 'lms' CLI tool not found in PATH.")
            print("    Please enable CLI in LM Studio Settings or start the server manually in LM Studio.")
            return False
        except Exception as e:
            print(f"\n[-] Error starting lms server: {e}")
            return False

    def ensure_server_running(self) -> bool:
        """Ensures local LM Studio server is running, attempting auto-start if needed."""
        if self.check_server_status():
            return True
        return self.start_lms_server()

    def get_loaded_model(self) -> str:
        """Retrieves currently loaded model ID from LM Studio."""
        try:
            url = f"{self.base_url}/models"
            req = urllib.request.Request(url, headers={"User-Agent": "RudraAI/1.0"})
            with urllib.request.urlopen(req, timeout=3) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                models = data.get("data", [])
                if models:
                    model_id = models[0].get("id", "local-model")
                    self.current_model = model_id
                    return model_id
        except Exception:
            pass
        return "local-model"

    def chat_stream(self, messages: list):
        """Sends chat request to LM Studio and yields streaming text chunks."""
        model_id = self.current_model or self.get_loaded_model()
        url = f"{self.base_url}/chat/completions"
        
        payload = {
            "model": model_id,
            "messages": messages,
            "stream": True,
            "temperature": 0.7
        }
        
        data_bytes = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data_bytes,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "RudraAI/1.0"
            },
            method="POST"
        )

        try:
            with urllib.request.urlopen(req) as resp:
                for line in resp:
                    line_str = line.decode("utf-8").strip()
                    if not line_str or line_str.startswith(":"):
                        continue
                    if line_str == "data: [DONE]":
                        break
                    if line_str.startswith("data: "):
                        content_json = line_str[6:]
                        try:
                            chunk_data = json.loads(content_json)
                            choices = chunk_data.get("choices", [])
                            if choices:
                                delta = choices[0].get("delta", {})
                                content = delta.get("content", "")
                                if content:
                                    yield content
                        except json.JSONDecodeError:
                            continue
        except urllib.error.URLError as e:
            yield f"\n[-] Connection Error to LM Studio: {e.reason}"
        except Exception as e:
            yield f"\n[-] Error communicating with LLM: {e}"
