import urllib.request
import json
import time
import sys

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

def verify():
    print("1. Checking Health...")
    hc = request("GET", "/healthz")
    if not hc:
        print("API not reachable.")
        return
    print("Health OK")

    print("\n2. Creating User...")
    user_payload = {
        "email": f"test_rag_{int(time.time())}@example.com",
        "api_key": f"secret-key-{int(time.time())}"
    }
    user = request("POST", "/users", user_payload)
    if not user:
        print("Failed to create user")
        return
    api_key = user["api_key"]
    print(f"User created. Key: {api_key}")

    print("\n3. Uploading Document...")
    doc_content = "The secret code for the super-vault is 8822. Remember it well."
    doc_payload = {
        "title": "Secret Codes",
        "content": doc_content
    }
    headers = {"X-API-Key": api_key}
    doc = request("POST", "/documents", doc_payload, headers)
    if not doc:
        print("Failed to upload document")
        return
    print(f"Document uploaded: {doc['id']}")

    print("\n4. Querying Assistant (RAG)...")
    query_payload = {"prompt": "What is the secret code for the vault?"}
    assist = request("POST", "/assist", query_payload, headers)
    
    if not assist:
        print("Assist call failed")
        return
    
    reply = assist["reply"]
    print(f"Reply: {reply}")

    if "8822" in reply:
        print("\n[SUCCESS] RAG verified! Found the secret code.")
    else:
        print("\n[FAILURE] RAG did not return the secret code.")

if __name__ == "__main__":
    try:
        verify()
    except KeyboardInterrupt:
        pass
