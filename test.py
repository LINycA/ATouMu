import requests


url = "https://compass.jinritemai.com/compass_api/author/live/live_room_detail/flow/trend_analysis_v2?index_selected=watch_ucnt&trend_gap=minute&live_room_id=7345360503415376691&X-Bogus=DFSzsdVuhCvANSvEtLIdAZHGDJ4d"
headers = {
    "user-agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "cookie":"LUOPAN_DT=session_7340163080334098740; domain=compass.jinritemai.com; path=/; secure; SameSite=None"
}

res = requests.get(url=url,headers=headers)
print(res.text)