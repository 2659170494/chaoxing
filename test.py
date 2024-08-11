from DrissionPage import ChromiumPage

try:
    global page
    page = ChromiumPage()
except FileNotFoundError:
    from DrissionPage import ChromiumOptions
    path = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'  # 请改为你电脑内包含Chromium内核的浏览器可执行文件路径
    ChromiumOptions().set_browser_path(path).save()
page.get('https://bot.sannysoft.com/') #
input("Wait")