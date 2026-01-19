import urllib.request
import json
import time

BASE_URL = "http://localhost:8000"

def request(method, endpoint, data=None, headers=None):
    if headers is None: headers = {}
    url = f"{BASE_URL}{endpoint}"
    req = urllib.request.Request(url, method=method)
    for k, v in headers.items(): req.add_header(k, v)
    if data:
        req.add_header("Content-Type", "application/json")
        req.data = json.dumps(data).encode("utf-8")
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        print(f"Error {endpoint}: {e.code} {e.reason}")
        try:
            print(f"Body: {e.read().decode()}")
        except:
            pass
        return None
    except Exception as e:
        print(f"Error {endpoint}: {e}")
        return None

def verify():
    # 1. Create User
    unique_id = int(time.time())
    user = request("POST", "/users", {"email": f"mem_{unique_id}@e.com", "api_key": f"k_{unique_id}"})
    headers = {"X-API-Key": user["api_key"]}
    print("User created.")

    # 2. Upload Doc
    doc = request("POST", "/documents", {
        "title": "Heroes", 
        "content": "Batman is a superhero who lives in Gotham City. He fights the Joker."
    }, headers)
    print("Document uploaded.")

    # 3. Chat: Q1
    print("\nQ1: Who lives in Gotham?")
    messages = [{"role": "user", "content": "Who lives in Gotham?"}]
    res1 = request("POST", "/assist", {"messages": messages}, headers)
    reply1 = res1["reply"]
    print(f"A1: {reply1}")
    messages.append({"role": "assistant", "content": reply1})

    # 4. Chat: Q2 (Contextual)
    print("\nQ2: Who does he fight? (Context: 'he' -> Batman)")
    messages.append({"role": "user", "content": "Who does he fight?"})
    res2 = request("POST", "/assist", {"messages": messages}, headers)
    reply2 = res2["reply"]
    print(f"A2: {reply2}")

    if "Joker" in reply2:
        print("\n[SUCCESS] Memory verified!")
    else:
        print("\n[FAILURE] Did not return Joker.")

if __name__ == "__main__":
    verify()
