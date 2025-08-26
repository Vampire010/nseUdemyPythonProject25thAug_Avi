import requests

url = "https://www.udemy.com/api-2.0/users/me/subscribed-courses/1144906/lectures/6693238/?fields[lecture]=asset,description,download_url,is_free,last_watched_second&fields[asset]=asset_type,length,media_license_token,course_is_drmed,media_sources,captions,thumbnail_sprite,slides,slide_urls,download_urls,external_url&q=0.3250202019274441"

headers = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "en-US",
    "referer": "https://www.udemy.com/course/introduction-to-data-exractionweb-scraping-in-python/learn/lecture/6693238?start=0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
    "x-requested-with": "XMLHttpRequest",
    "x-udemy-cache-brand": "INen_US",
    "x-udemy-cache-campaign-code": "MT260825G2",
    "x-udemy-cache-device": "None",
    "x-udemy-cache-language": "en",
    "x-udemy-cache-logged-in": "1",
    "x-udemy-cache-marketplace-country": "IN",
    "x-udemy-cache-price-country": "IN",
    "x-udemy-cache-release": "1271ac12e57e737b6c5b",
    "x-udemy-cache-user": "161182582",
    "x-udemy-cache-version": "1"
}

cookies = {
    # ⚠️ You must paste your valid cookies here from your browser DevTools
    "access_token": "XjwKsRG5OJuqCtARD1+HUJqgAXZrr88RvVnbs7t3/5w:Ps5FDWuudsj45tYx1lD9T7/NJ09gKgkRYT1tkQoUqzA",
    "ud_user_jwt": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MTYxMTgyNTgyLCJlbWFpbCI6ImF2bmlhcnlhOEBnbWFpbC5jb20iLCJpc19zdXBlcnVzZXIiOmZhbHNlLCJncm91cF9pZHMiOltdfQ.tN02JMM2Py5In-USaRz3qn93aC1rHmE-idopivoNhoU",
    "csrftoken": "qKBNLnoMv5CRtKO0p22pfv8sdMEtBUSe",
    "dj_session_id": "nvvfpjbabbdd5oepwbk6d4yknl7vdu4q"
    # … add others if needed
}

resp = requests.get(url, headers=headers, cookies=cookies)

if resp.status_code == 200:
    print("✅ Success")
    print(resp.json())  # lecture info, including asset/media_sources
else:
    print("❌ Failed", resp.status_code, resp.text)
