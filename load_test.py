import concurrent.futures
import requests
import time

URL = "https://meena-agencies-trusted-pharma-wholesale-partner.streamlit.app/"
NUM_USERS = 50

def hit_app(user_id):
    start = time.time()
    try:
        res = requests.get(URL, timeout=15)
        end = time.time()
        return (user_id, res.status_code, round((end - start)*1000, 2))
    except Exception as e:
        return (user_id, "ERROR", str(e))

print(f"🚀 Simulating {NUM_USERS} concurrent users opening the app...")
start_test = time.time()

with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_USERS) as executor:
    results = list(executor.map(hit_app, range(1, NUM_USERS + 1)))

end_test = time.time()

success = sum(1 for r in results if r[1] == 200)
errors = sum(1 for r in results if r[1] != 200)
total_time = round((end_test - start_test) * 1000, 2)

print(f"\n📊 LOAD TEST RESULTS:")
print(f"   ✅ Successful Requests: {success}")
print(f"   ❌ Failed Requests: {errors}")
print(f"   ⏱️ Total Time for {NUM_USERS} users: {total_time} ms")
print(f"   ⚡ Average Time per user: {round(total_time / NUM_USERS, 2)} ms")

if errors == 0:
    print("\n🎉 PASS: The app can handle 50 concurrent users without crashing!")
else:
    print("\n⚠️ WARNING: The app struggled with 50 concurrent users. Streamlit Cloud Free Tier has limits.")
