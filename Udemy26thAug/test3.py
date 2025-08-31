import requests
import json

# Load credentials from Authentication.json
auth_path = r"Authentication.json"
with open(auth_path, "r") as f:
    auth = json.load(f)

access_token = auth.get("access_token")
client_id = auth.get("client_id")
csrf_token = auth.get("csrf")

url = "https://www.udemy.com/assets/35357818/files/2021-08-07_08-10-23-f0420cdf436995091bef63c49990323a/2/aa00d84944423034059058c0302b6aa3a4bb.m3u8?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwYXRoIjoiMjAyMS0wOC0wN18wOC0xMC0yMy1mMDQyMGNkZjQzNjk5NTA5MWJlZjYzYzQ5OTkwMzIzYS8yLyIsImV4cCI6MTc1NjU4MDAxOX0.-PrNRHBgtyEihTixAxDaIB9xsLnsH5mekZ_l4qAL95w&provider=cdn77&v=1"

headers = {
    "authority": "www.udemy.com",
    "method": "GET",
    "path": "/assets/35357818/files/2021-08-07_08-10-23-f0420cdf436995091bef63c49990323a/2/aa00d84944423034059058c0302b6aa3a4bb.m3u8?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwYXRoIjoiMjAyMS0wOC0wN18wOC0xMC0yMy1mMDQyMGNkZjQzNjk5NTA5MWJlZjYzYzQ5OTkwMzIzYS8yLyIsImV4cCI6MTc1NjU4MDAxOX0.-PrNRHBgtyEihTixAxDaIB9xsLnsH5mekZ_l4qAL95w&provider=cdn77&v=1",
    "scheme": "https",
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
    "priority": "u=1, i",
    "sec-ch-ua": '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin"
}

cookies = {
    "__udmy_2_v57r": "dd353e7a63ff41d2af094ce4a18e18e4",
    "__cfruid": "9f4c5737f4e047daa744a1cf8bba5ccb338002b2-1756562568",
    "ud_cache_brand": "INen_US",
    "ud_cache_marketplace_country": "IN",
    "ud_cache_price_country": "IN",
    "ud_cache_release": "7250e930798675e5f2ea",
    "ud_cache_version": "1",
    "ud_cache_language": "en",
    "ud_cache_device": "None",
    "blisspoint_fpc": "8f867ee4-f739-42eb-9dcd-9bbb2f64bac8",
    "IR_gbd": "udemy.com",
    "_yjsu_yjad": "1756562570.928c527c-5e01-450f-8cdd-b150270acf30",
    "ki_r": "aHR0cHM6Ly93d3cuZ29vZ2xlLmNvbS8%3D",
    "ud_firstvisit": "2025-08-30T14:02:50.679819+00:00:1usMAN:uIC_CyH9pyqMI42dApEShOUZ3sTSaONzCNupzzEIzFM",
    "dwnjrn": "60c152bdeb1ade6a0a9642fe0ca2384fb0817de7849b29c79a298be21eb1862e",
    "dwndvc": "a4d23f6f0fe2ee648d5663ba4623e62cdcdc745f63eb5f6d131d5fb8c9d89689",
    "_gid": "GA1.2.1228473361.1756562573",
    "__stripe_mid": "42860e05-c315-408a-ba62-d623daac8ce0fd3b53",
    "__stripe_sid": "d4ffff97-6424-4338-8d3d-c181467a8e1fcf9235",
    "__ssid": "2a0ff42bcbd68dd2101f118b0e55379",
    "_fbp": "fb.1.1756562576007.14305091392884717",
    "FPAU": "1.1.115583067.1756562570",
    "_gcl_au": "1.1.115583067.1756562570.1897788449.1756562587.1756562655",
    "client_id": client_id,
    "access_token": access_token,
    "ud_last_auth_information": '{"backend": "udemy-passwordless", "suggested_user_email": "avniarya8@gmail.com", "suggested_user_name": "Avni", "suggested_user_avatar": "https://img-c.udemycdn.com/user/50x50/anonymous_3.png", "suggested_user_phone_number": null}:1usMBk:T47EzNddl4dmAtHnNmozbsgxkDP6ajq2NizprvcznxY',
    "ud_user_jwt": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MTYxMTgyNTgyLCJlbWFpbCI6ImF2bmlhcnlhOEBnbWFpbC5jb20iLCJpc19zdXBlcnVzZXIiOmZhbHNlLCJncm91cF9pZHMiOltdfQ.tN02JMM2Py5In-USaRz3qn93aC1rHmE-idopivoNhoU",
    "ud_locale": "en_IN",
    "ud_cache_user": "161182582",
    "ud_cache_logged_in": "1",
    "ud_credit_unseen": "0",
    "ud_credit_last_seen": "None",
    "csrftoken": csrf_token,
    "dj_session_id": "ulg3e4b8fjthr964hfzjjgoyrx05k7qm",
    "ud_cache_campaign_code": "KEEPLEARNING",
    "ab.storage.deviceId.5cefca91-d218-4b04-8bdd-c8876ec1908d": "%7B%22g%22%3A%22edb4e1b9-c9ff-cd09-0ec9-f05535a819e5%22%2C%22c%22%3A1756562569549%2C%22l%22%3A1756562662892%7D",
    "ab.storage.userId.5cefca91-d218-4b04-8bdd-c8876ec1908d": "%7B%22g%22%3A%22161182582%22%2C%22c%22%3A1756562662891%2C%22l%22%3A1756562662893%7D",
    "ud_cmp_ctp_vc": "1",
    "ud_cmp_ctp_vclts": "1756562743",
    "mute": "0",
    "quality_general": "360",
    "new_user": "true",
    "existing_user": "true",
    "optimizelyEndUserId": "oeu1756563302312r0.39190526263133174",
    "cf_clearance": "2imchhVlsOFDkG5m2k.LzCBzjjzCZcjN1gmgCUL5Qyk-1756563302-1.2.1.1-zauc1wNZvd7ZmdC4XwZyDUGDImSqWw.0874kfwp45wTlpzkZi6zIk3YAVai07.BvhuhxCka8xd8JOh54sW7czGx7aCfQNN0.Nx64yVHs9vnvGx_.fa3RevZgRbYK9.zSp2TFTBuBN2JBc2Oc.ef4XqBeIHwAIQJOrtbA5gW6FTpIODVrdUDPdP9ESZK6SUUMjYjmxe_yzYux8817Zg5xZXztmNxczlXh7YfsjUYYNio",
    "_ga_DFDMXRYPXY": "GS2.1.s1756563198$o1$g1$t1756563439$j56$l0$h0",
    "__cf_bm": "q.hUNiLhVN_3brtwQtludG6nf4G8uYyHwkQb2qRwRyE-1756563472-1.0.1.1-T.3OvdtG41KBjXK4AQrNdgCZrTxPRbQyirfg0kMx0ry3I0hh0Vc7_FGil0KmCW0xiDnt6c3.J50LKem2F4bc9kh7tMT.VUbosDNzS0LlqWs",
    "OptanonConsent": "isGpcEnabled=0&datestamp=Sat+Aug+30+2025+19%3A48%3A02+GMT%2B0530+(India+Standard+Time)&version=202407.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=819f898f-b79e-4c6d-864a-2529072c28b8&interactionCount=1&isAnonUser=1&landingPath=NotLandingPage&groups=C0003%3A1%2CC0005%3A1%2CC0004%3A1%2CC0001%3A1%2CC0002%3A1&AwaitingReconsent=false",
    "ab.storage.sessionId.5cefca91-d218-4b04-8bdd-c8876ec1908d": "%7B%22g%22%3A%2226727857-cb07-0b5e-d5e0-98710464b835%22%2C%22e%22%3A1756565285186%2C%22c%22%3A1756562662892%2C%22l%22%3A1756563485186%7D",
    "_rdt_uuid": "1756562570240.43cbd05f-d226-45a4-9af4-763de5379cef",
    "IR_39854": "1756563485406%7C0%7C1756563485406%7C%7C",
    "IR_PI": "03c17594-85aa-11f0-bee6-1b52c6ee8ce6%7C1756649885406",
    "ki_t": "1756562571051%3B1756562571051%3B1756563485585%3B1%3B8",
    "cto_bundle": "5ac4919mTEZoSENoM0oxSnBwbHN6dmhaWXBOaFglMkJSMUhrWWJHaE5nYXdxRUdmUDFBb1ZZSEtvUHFoSldya3BUZ2JyTUw2eXB2a2xYWFhGU1htaTZJczRTS0tKanZIS0trWWp5N3ZUaklYWW5UaWxCMCUyQnFDa3JSWkVMOVJxSUlIJTJGYnpaS3N1WGJpS1RsSHMwalVybllIY3IwY3clM0QlM0Q",
    "_ga_7YMFEFLR6Q": "GS2.1.s1756562576$o1$g1$t1756563485$j32$l0$h0",
    "muxData": "=undefined&mux_viewer_id=b514680e-dc2c-495d-b4e1-97a2fb4c6ef3&msn=0.866809262402911&sid=a4f85c96-944c-4faf-943f-9883fb4c73b0&sst=1756562748336&sex=1756564985937",
    "_uetsid": "03e1fd3085aa11f09606d7013933d6f8|1kq0xb1|2|fyw|0|2068",
    "_uetvid": "03e242e085aa11f08a0671b7fc35cc7b|vc1xg|1756563486884|8|1|bat.bing.com/p/insights/c/d",
    "_ga": "GA1.2.1059827093.1756562573",
    "_dd_s": "rum=0&expire=1756564718863",
    "ud_country_code": "IN",
    "eventing_session_id": "M2JjODllNzUtNjRiNy00Nm-1756565619417",
    "evi": "3@y0vRf1vUh4gtYYZhWa5UgenTrw34vfrEwXgefBaveQT5h4KNcAnEIKXC",
    "ud_rule_vars": "eJx1jsFqAyEQQH8leG0TRkfXXb9lQSY6ptI0UnVzCfn3CE2h0BbmNMx7b26iUz1x5-ivueVeqosRDbKlCVPSMipKsOjAmuTMY7QLpbxnFm4nbqtIubb-xfpIndexX4UCZfYw7xF2UjtQTi8HaY21-gXAAazidVydaaC9bOHN90op5eBb2Wpgf6Wa6Xh-2ko90SWHH1Dlz43b_0WFDkfRTDjNv4phNBo_f-7540-DtM7Iw7ygQvttuIv7A3jwWp0=:1usMUV:Ch7A5DQ2auaBqjNvgoacn_XwXYfMpTatK0O6aR9Jqgs"
}

session = requests.Session()
session.headers.update(headers)
session.cookies.update(cookies)

response = session.get(url)
print("Status code:", response.status_code)

if response.status_code == 200:
    lines = response.text.splitlines()
    target_bandwidth = "BANDWIDTH=214570"
    url_found = None
    for i, line in enumerate(lines):
        if line.startswith("#EXT-X-STREAM-INF:") and target_bandwidth in line:
            # The next line should be the URL
            if i + 1 < len(lines):
                url_found = lines[i + 1]
            break
    print("URL for BANDWIDTH=214570:")
    print(url_found)
else:
    print("Request failed. Raw response:")
    print(response.text)