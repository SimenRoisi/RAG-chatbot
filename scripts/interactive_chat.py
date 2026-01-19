import urllib.request
import json
import time
import sys
import os

BASE_URL = "http://localhost:8000"

def request(method, endpoint, data=None, headers=None):
    if headers is None:
        headers = {}
    
    url = f"{BASE_URL}{endpoint}"
    req = urllib.request.Request(url, method=method)
    
    for k, v in headers.items():
        req.add_header(k, v)
        
    if data:
        json_data = json.dumps(data).encode("utf-8")
        req.add_header("Content-Type", "application/json")
        req.data = json_data
        
    try:
        with urllib.request.urlopen(req) as response:
            if response.status >= 400:
                print(f"Error {response.status}: {response.read().decode()}")
                return None
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.read().decode()}")
        return None
    except Exception as e:
        print(f"Request failed: {e}")
        return None

def main():
    print("--- RAG Chatbot CLI ---")
    print("Checking API health...")
    if not request("GET", "/healthz"):
        print("API is not running. Please run 'docker compose up' first.")
        return

    # Create a session user
    print("Creating temporary user session...")
    user_payload = {
        "email": f"cli_user_{int(time.time())}@example.com",
        "api_key": f"cli-key-{int(time.time())}"
    }
    user = request("POST", "/users", user_payload)
    if not user:
        print("Failed to create user.")
        return
    
    api_key = user["api_key"]
    headers = {"X-API-Key": api_key}
    print(f"Session ready. User ID: {user['id']}")
    print("\nCommands:")
    print("  /upload <path_to_text_file>  - Upload a document for RAG")
    print("  /quit                        - Exit")
    print("  <any text>                   - Chat with the bot")
    print("-" * 30)

    while True:
        try:
            user_input = input("\n> ").strip()
            if not user_input:
                continue
            
            if user_input.lower() in ["/quit", "/exit"]:
                break
                
            if user_input.startswith("/upload "):
                filepath = user_input[8:].strip()
                if not os.path.exists(filepath):
                    print(f"File not found: {filepath}")
                    continue
                
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()
                    
                    doc_payload = {"title": os.path.basename(filepath), "content": content}
                    res = request("POST", "/documents", doc_payload, headers)
                    if res:
                        print(f"Document uploaded successfully! (ID: {res['id']})")
                except Exception as e:
                    print(f"Failed to read file: {e}")
                continue

            # Chat
            # Show a spinner-ish thing? Nah, just wait.
            print("Thinking...", end="", flush=True)
            res = request("POST", "/assist", {"prompt": user_input}, headers)
            print("\r" + " " * 20 + "\r", end="", flush=True) # clear "Thinking..."
            
            if res:
                print(f"Bot: {res['reply']}")

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
