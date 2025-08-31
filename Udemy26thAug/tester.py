import requests
import json

# Load client_id and access_token from Authentication.json
auth_path = r"C:\Users\giris\OneDrive\Documents\GitHub\nseUdemyPythonProject25thAug_Avi\Udemy26thAug\Authentication.json"
with open(auth_path, "r") as f:
    auth = json.load(f)

client_id = auth.get("client_id")
access_token = auth.get("access_token")
csrf_token = auth.get("csrf")

url = "https://www.udemy.com/api-2.0/users/me/subscribed-courses/1144906/lectures/6694874/"
params = {
    "fields[lecture]": "asset,description,download_url,is_free,last_watched_second",
    "fields[asset]": "asset_type,length,media_license_token,course_is_drmed,media_sources,captions,thumbnail_sprite,slides,slide_urls,download_urls,external_url",
    "q": "0.7656153970602966"
}

headers = {
    "accept": "application/json, text/plain, */*",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-IN",
    "dwn-profiling": "Cg1Bc2lhL0NhbGN1dHRhEMoCGMoCIgtHb29nbGUgSW5jLigIOIAMQOAGSgVXaW4zMlIGeDg2XzY0WgVlbi1HQmIFZW4tR0JqBmNocm9tZXABehC7XVpIk/wjH2kzGFM/xsBOggEQ8VWliX0sHiboB1DqzUnQJIgBGJgBAaABAKgBALABALgBDMABAMgBANABANgBAOABAfgBAYACAYgCAJACEpoCEFVPNApns9U0kH9cZRfnTfClAmfm7kKtAmfm7kK1Amfm7kK9As1s5kLFAs1swkLNAjMz70DVAjOT7ELaAhDAXiArdH9UcFAzqZFC/Y5s4AIA6AIA8AIy+AIAgAMBkgMQoVnZtOuZanuasXzsGN6oHpgDBaIDEMFCs3nKAY71lrpO2K/Hn0uqA1FBTkdMRSAoQU1ELCBBTUQgUmFkZW9uKFRNKSBHcmFwaGljcyAoMHgwMDAwMTY0QykgRGlyZWN0M0QxMSB2c181XzAgcHNfNV8wLCBEM0QxMSmyAxFHb29nbGUgSW5jLiAoQU1EKcADAcgDt73hzY8z0APtyeHNjzPYA4W7ucuPM+IDfE1Ga3dFd1lIS29aSXpqMENBUVlJS29aSXpqMERBUWNEUWdBRTYzWUdIS1NpdThyS1VCQXBYT1hBbnNCeERQV3daaG9WbUdBdU5IeTFtMWJWNW1ad2dGODV6Y1ppV2ozYWNBNGE0VVRYL1B5MHN4dHcwNEtCdjNjTXlnPT3qA2BNRVlDSVFDaE9id21ZY1crU005dUdnTm5ZdXBiUHhSSklPRFVVTUtpU0ZzbkRnSndkUUloQVBYTmNvZzBqbVdXVFJjdGdveE5lK0Z4UU9pMWhEK3c0RFFjSllJSkNQeGuKBCBhMGQ1YTk1YjBmZGU0OTAzOTE2ZDA1MWU0MjcxY2FlOZoE9AEIARAAGAFCIAgBFUQ/M0MdRD8zQyVEPzNDLf///381////fz0AAAAAQiAIAhVZCTJDHVkJMkMlWQkyQy3///9/Nf///389AAAAAEIgCAMVAAB0Qh0AAHRCJQAAdEIt////fzX///9/PQAAAABCIAgEFQQQPEAdBBA8QCUEEDxALf///381////fz0AAAAAQiAIBRX2D147HfYPXjsl9g9eOy3///9/Nf///389AAAAAEIgCAYVAAAAAB0AAAAAJQAAAAAt////fzX///9/PQAAAABCIAgHFQAAQEAdAACgQCUiIoJALQAAAAA1AACAQD0i0BI/qgQECAIQAsIEIDNkODI1YmMxZmUwMDQ5MzI5ZWUzN2FmMjllNDgwY2IyygQHaW5kZXhEQtIEBUVDRFNB2gQOU0VDVVJFX0lEX1NFTlTiBAdXaW5kb3dz6gQCMTHyBAZDaHJvbWX6BAMxMzmKBSBmMWNlNmM2ZWEyNTY0MzJlOGIyMGY2OTgzNzRlYmM2N5IFHhUAAGhCHQAAdEIlvLtvQi0AAAAANQAAcEI9ItASP5oFDHYxLjUuMjEtMTgwNaoFEhDQgwQglcXhzY8zKO3J4c2PM8IFBAECLgPKBQEB0AUC2AW3veHNjzPgBe3J4c2PM4oGCzIwMi42Mi44My4xmgYaCLm4ARD7h92ABBihg6kuINmqjSgogIDw/w+oBgE=",
    "priority": "u=1, i",
    "sec-ch-ua": '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "x-requested-with": "XMLHttpRequest",
    "x-udemy-cache-brand": "INen_US",
    "x-udemy-cache-campaign-code": "KEEPLEARNING",
    "x-udemy-cache-device": "None",
    "x-udemy-cache-language": "en",
    "x-udemy-cache-logged-in": "1",
    "x-udemy-cache-marketplace-country": "IN",
    "x-udemy-cache-price-country": "IN",
    "x-udemy-cache-release": "7250e930798675e5f2ea",
    "x-udemy-cache-user": "161182582",
    "x-udemy-cache-version": "1"
}

# All cookies from your PowerShell session
cookies = {
    "__udmy_2_v57r": "21d808a4df36451498adce3d96c46555",
    "ud_cache_brand": "INen_US",
    "ud_cache_marketplace_country": "IN",
    "ud_cache_price_country": "IN",
    "ud_cache_release": "7250e930798675e5f2ea",
    "ud_cache_version": "1",
    "ud_cache_language": "en",
    "ud_cache_device": "None",
    "blisspoint_fpc": "f88f4f30-0d55-4961-a6ab-19cc813a24a3",
    "_fbp": "fb.1.1756531405042.199967023860133657",
    "ud_firstvisit": "2025-08-30T05:23:26.336650+00:00:1usE3j:MFR0N8GMglq7RYWvaVSInuyZhlgNvFF5p03lVfwb_tw",
    "IR_gbd": "udemy.com",
    "_yjsu_yjad": "1756531409.56ab5015-2962-48ea-b931-daaf57187bac",
    "dwnjrn": "ec9c84a431ef08dcbd2be67860aee215d910b18ec98d4878511dbbdf2c34f817",
    "dwndvc": "3fbc941ee54bb26f7e35d6dfab685250592c8e7507bf4b2a157e31d6fd4a12e9",
    "FPAU": "1.1.525819779.1756531403",
    "_gid": "GA1.2.1102185268.1756531416",
    "__ssid": "61b89f82f18bbac363b5a21452b6cbf",
    "ki_r": "",
    "__stripe_mid": "90901f68-9c10-4808-ad2b-355d937447d818bff8",
    "__stripe_sid": "193fc945-330a-404c-93f6-83f48bff4a07afedba",
    "_gcl_au": "1.1.525819779.1756531403.690459848.1756531428.1756531456",
    "client_id": client_id,
    "access_token": access_token,
    "ud_last_auth_information": "{\"backend\": \"udemy-passwordless\", \"suggested_user_email\": \"avniarya8@gmail.com\", \"suggested_user_name\": \"Avni\", \"suggested_user_avatar\": \"https://img-c.udemycdn.com/user/50x50/anonymous_3.png\", \"suggested_user_phone_number\": null}:1usE4X:mpRGB_53YKj-D4ej_vtO2nkL1FCEWyQnH7g3ooHcbH4",
    "ud_user_jwt": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MTYxMTgyNTgyLCJlbWFpbCI6ImF2bmlhcnlhOEBnbWFpbC5jb20iLCJpc19zdXBlcnVzZXIiOmZhbHNlLCJncm91cF9pZHMiOltdfQ.tN02JMM2Py5In-USaRz3qn93aC1rHmE-idopivoNhoU",
    "ud_locale": "en_IN",
    "ud_cache_user": "161182582",
    "ud_cache_logged_in": "1",
    "ud_credit_unseen": "0",
    "ud_credit_last_seen": "None",
    "csrftoken": csrf_token,
    "dj_session_id": "thnbia4ob6o74rx3qdb1x27a73boir3u",
    "ud_cache_campaign_code": "KEEPLEARNING",
    "ab.storage.deviceId.5cefca91-d218-4b04-8bdd-c8876ec1908d": "%7B%22g%22%3A%22c21f402c-fce3-d359-f054-d19d1da1f822%22%2C%22c%22%3A1756531402169%2C%22l%22%3A1756531464328%7D",
    "ab.storage.userId.5cefca91-d218-4b04-8bdd-c8876ec1908d": "%7B%22g%22%3A%22161182582%22%2C%22c%22%3A1756531464325%2C%22l%22%3A1756531464329%7D",
    "ud_cmp_ctp_vc": "1",
    "ud_cmp_ctp_vclts": "1756533211",
    "mute": "0",
    "get_app_modal_closed": "1",
    "__cfruid": "2e38d5fdfa9f1d3158fe20b7ff915b30ab98d21f-1756535169",
    "__cf_bm": "Y3IWW_2oN7SKK.MM4amu4CCqumbFebkrysoJi1fhoVs-1756536074-1.0.1.1-HHb9fvXbUPY4qIajPfTGi2pS_8pPeJeBeJghvmq2RjNAFNBDyX8SX1mf60IDoe9QQtC3RpmgU7qet_9RyVwFzkNZwDxe68tztZ1mLDNNWxA",
    "ud_country_code": "IN",
    # Add other cookies as needed
}

session = requests.Session()
session.headers.update(headers)
session.cookies.update(cookies)

response = session.get(url, params=params)
print("Status code:", response.status_code)

if response.status_code == 200:
    try:
        data = response.json()
        # Safely navigate to the src value
        src = None
        # Example: asset > media_sources > list of dicts with 'src'
        asset = data.get("asset", {})
        media_sources = asset.get("media_sources", [])
        for source in media_sources:
            if source.get("type") == "application/x-mpegURL" and "src" in source:
                src = source["src"]
                break
        print("Extracted src:", src)
    except Exception:
        print("Response is not JSON. Raw response:")
        print(response.text)
else:
    print("Request failed. Raw response:")
    print(response.text)