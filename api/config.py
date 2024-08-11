# -*- coding: utf-8 -*-
from DrissionPage import WebPage, ChromiumOptions, SessionOptions
from api.logger import logger

def start_session(mode,chromium_options):
    return WebPage(mode=mode,chromium_options=chromium_options)

class GlobalConst():
    debug = True
    logger.trace("开始启动Chromedriver，请稍等")
    _session = start_session("s",chromium_options=ChromiumOptions().headless())
    logger.trace("初始化Chromedriver和请求头，请稍等")
    _session.get("about:blank")
    temp_user_agent = str(_session.run_cdp('Runtime.evaluate', expression='navigator.userAgent;')['result']['value'])
    temp_sec_ch_ua = str(_session.run_cdp('Runtime.evaluate', expression=r'(()=>{var sdjklf = "";for (x in navigator.userAgentData.toJSON()["brands"]) {const a = navigator.userAgentData.toJSON()["brands"][x];sdjklf = sdjklf.concat(`"${a["brand"]}";v="${a["version"]}", `)};return(sdjklf.substring(0,sdjklf.length-2));})();')['result']['value'])
    #print(_session.run_cdp('Runtime.evaluate', expression=r'navigator.userAgentData'))
    AESKey = "u2oh6Vu^HWe4_AES"
    HEADERS = {
        "User-Agent": temp_user_agent,
        "Sec-Ch-Ua": temp_sec_ch_ua
    }
    COOKIES_PATH = "cookies.txt"
    VIDEO_HEADERS = {
        "User-Agent": temp_user_agent,
        "Sec-Ch-Ua": temp_sec_ch_ua,
        "Referer": "https://mooc1.chaoxing.com/ananas/modules/video/index.html?v=2023-1110-1610",
        "Host": "mooc1.chaoxing.com"
    }
    AUDIO_HEADERS = {
        "User-Agent": temp_user_agent,
        "Sec-Ch-Ua": temp_sec_ch_ua,
        "Referer": "https://mooc1.chaoxing.com/ananas/modules/audio/index_new.html?v=2023-0428-1705",
        "Host": "mooc1.chaoxing.com"
    }
    THRESHOLD = 3
    logger.trace("初始化Chromedriver和请求头完毕")
