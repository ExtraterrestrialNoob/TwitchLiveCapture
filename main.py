import json
import requests
import re
import random
import m3u8
import subprocess

# Variables 
FFMPEG_PATH = "D:\\ffmpeg\\bin\\ffmpeg.exe"
SLEEP_TIME = 1000


class urlExtractor():
    def __init__(self,url) -> None:
        self.USHERBASE = "https://usher.ttvnw.net"
        self.HLS_API = "/api/channel/hls/"
        self.URL = url
        self.STREAMER = str(self.URL.split("/")[3])
        self.CLIENT_ID = "kimne78kx3ncx6brgo4mv6wki5h1ko"

    def isLive(self):
        try:
            islive = True if (re.search('"isLiveBroadcast":true',str(self.html.content))) else False
        except:
            print("error -> func:isLive : Regex mismatch")
            islive = False
        return islive

    def refreshpage(self):
        self.extractInfo()

    def extractInfo(self):
        self.page = requests.session()
        self.html = self.page.get(self.URL)
    
    def get_gql(self):
        Cookies = {
            "Accept-Language": "en-US",
            "Client-ID": self.CLIENT_ID,
            "Content-Type": "text/plain; charset=UTF-8",
            "Authorization": "",
            "Device-ID" : self.page.cookies.get("unique_id"),
        }

        data = {"query":'''{  streamPlaybackAccessToken(channelName: "%s" , params: {platform: "web", playerBackend: "mediaplayer", playerType: "site"}){    value    signature    __typename  }}''' 
        % (self.STREAMER)}

        gql = requests.post("https://gql.twitch.tv/gql", data=json.dumps(data).encode(), headers=Cookies)
        if gql.status_code == 200:
            gql_data = json.loads(gql.content.decode("utf-8"))
        else:
            print("something went wrong")
            gql_data = None
        return gql_data

    def getm3u8(self):
        gql = self.get_gql()
        query = {
            'allow_source': 'true',
            'allow_audio_only': 'true',
            'allow_spectre': 'true',
            'p': random.randint(1000000, 10000000),
            'player': 'twitchweb',
            'playlist_include_framerate': 'true',
            'segment_preference': '4',
            'sig': gql["data"]["streamPlaybackAccessToken"]['signature'],
            'token': gql["data"]["streamPlaybackAccessToken"]["value"],
        }
        url = self.USHERBASE + self.HLS_API + self.STREAMER + ".m3u8"
        response = requests.get(url, params=query)
        return m3u8.loads(response.content.decode("utf-8"))



xlive = urlExtractor("https://www.twitch.tv/cmgriffing")
xlive.extractInfo()
if (xlive.isLive()):
    playlist = xlive.getm3u8()
    link_list = []
    count = 0;
    for i in playlist.playlists:
        if not i.stream_info.resolution == None:
            print(str(count) + " =", i.stream_info.resolution)
            link_list.append(i.uri)
            count += 1
    req_quality = int(input('quality: '))
    if req_quality<= count and req_quality >= 0:
        print(link_list[req_quality])
        command = [FFMPEG_PATH, "-i", link_list[req_quality], "-c", "copy", "-bsf:a", "aac_adtstoasc", "output.mp4"]
        subprocess.call(command)
        print("FFMPEG Running.... ")

# m3u8_ = xlive.getm3u8()
# xlive.m3u8parser(m3u8_)
# print(m3u8_)
# playlist = m3u8.loads(m3u8_)
