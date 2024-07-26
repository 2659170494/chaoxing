# -*- coding: utf-8 -*-
import argparse
import configparser
import os
from api.logger import logger
from api.base import Chaoxing, Account

from api.exceptions import LoginError, FormatError, JSONDecodeError, DriverNotFoundError
from api.config import GlobalConst as gc

debug = gc.debug
default_driver = 1
default_d_function = 0

def init_config():
    parser = argparse.ArgumentParser(description='Samueli924/chaoxing')  # 命令行传参
    parser.add_argument("-c", "--config", type=str, default=None, help="使用配置文件运行程序")
    parser.add_argument("-u", "--username", type=str, default=None, help="手机号账号")
    parser.add_argument("-p", "--password", type=str, default=None, help="登录密码")
    parser.add_argument("-l", "--list", type=str, default=None, help="要学习的课程ID列表")
    parser.add_argument("-s", "--speed", type=int, default=1, help="视频播放倍速(默认1，最大2)")
    parser.add_argument("-cdc","--chromedriver",type=str,default="",help="指定Chromedriver路径位置")
    parser.add_argument("-drv","--driver",type=int,default=default_driver,help="指定使用哪个驱动器(默认0=requests，1=DrissionPage)")
    args = parser.parse_args()
    if args.config:
        config = configparser.ConfigParser()
        config.read(args.config, encoding="utf8")
        return (config.get("common", "username"),
                config.get("common", "password"),
                str(config.get("common", "course_list")).split(",") if config.get("common", "course_list") else None,
                int(config.get("common", "speed")),
                str(config.get("common","chromedriver")) if config.get("common","chromedriver") else "",
                int(config.get("common","driver")) if config.get("common","driver") else default_driver)
    else:
        return (args.username, args.password, args.list.split(",") if args.list else None, int(args.speed) if args.speed else 1, args.chromedriver if args.chromedriver else "", int(args.driver) if args.driver else default_driver)


if __name__ == '__main__':
    # 初始化登录信息
    username, password, course_list, speed, cdc_path, driver= init_config()
    # 强行限制倍速最大为2倍速
    speed = 2 if speed > 2 else speed
    # 若有账号密码输入则抛弃cookies并重新登陆（需要完善下逻辑）
    if cdc_path:
        from DrissionPage import ChromiumOptions
        ChromiumOptions().set_browser_path(cdc_path).save()
    if username or password:
        # if os.path.lexists(gc.COOKIES_PATH) and os.path.getsize(gc.COOKIES_PATH):
        #     if username and password:
        #         input("检测到终端目录有cookies.txt存在，若继续登录将会清除该cookies。\n请按回车键继续。。。")
        #     else:
        #         print("检测到终端目录有cookies.txt存在，若继续登录将会清除该cookies。")
        chaoxing = "need_login"
    #cookies存在则直接使用
    elif os.path.lexists(gc.COOKIES_PATH) and os.path.getsize(gc.COOKIES_PATH):
        chaoxing = Chaoxing(driver=driver)
    #什么都没用默认当工具启动
    else:
        chaoxing = "need_login"
    if chaoxing == "need_login":
        if (not username) :
            username = input("请输入你的手机号，按回车确认\n手机号:")
        if (not password) :
            password = input("请输入你的密码，按回车确认\n密码:")
        account = Account(username, password)
        # 实例化超星API
        chaoxing = Chaoxing(driver=driver,account=account)
        # 检查当前登录状态，并检查账号密码
        _login_state = chaoxing.login()
        if not _login_state["status"]:
            raise LoginError(_login_state["msg"])
    # 获取所有的课程列表
    all_course = chaoxing.get_course_list()
    course_task = []
    # 手动输入要学习的课程ID列表
    if not course_list:
        print("*"*10 + "课程列表" + "*"*10)
        for course in all_course:
            print(f"ID: {course['courseId']} 课程名: {course['title']}")
        print("*" * 28)
        try:
            course_list = str(input("请输入想要学习的课程列表,以逗号分隔,例: 2151141,189191,198198\n")).split(",")
        except:
            raise FormatError("输入格式错误")
    # 筛选需要学习的课程
    for course in all_course:
        if course["courseId"] in course_list:
            course_task.append(course)
    if not course_task:
        course_task = all_course
    # 开始遍历要学习的课程列表
    logger.info(f"课程列表过滤完毕，当前课程任务数量: {len(course_task)}")
    for course in course_task:
        # 获取当前课程的所有章节
        point_list = chaoxing.get_course_point(course["courseId"], course["clazzId"], course["cpi"])
        for point in point_list["points"]:
            # 获取当前章节的所有任务点
            jobs = []
            job_info = None
            jobs, job_info = chaoxing.get_job_list(course["clazzId"], course["courseId"], course["cpi"], point["id"])
            # 可能存在章节无任何内容的情况
            if not jobs:
                continue
            # 遍历所有任务点
            for job in jobs:
                # 视频任务
                if job["type"] == "video":
                    logger.trace(f"识别到视频任务, 任务章节: {course['title']} 任务ID: {job['jobid']}")
                    # 超星的接口没有返回当前任务是否为Audio音频任务
                    isAudio = False
                    try:
                        # 若调试启动，以chromedriver方式挂课
                        if driver == default_d_function:
                            chaoxing.study_video_d(course, job, job_info, _speed=speed, _type="Video")
                        # 否则以协议挂课
                        else:
                            chaoxing.study_video(course, job, job_info, _speed=speed, _type="Video")
                    except JSONDecodeError as e:
                        logger.warning("当前任务非视频任务，正在尝试音频任务解码")
                        isAudio = True
                    if isAudio:
                        try:
                            #同上，调试开启chromedriver启动
                            if driver == default_d_function:
                                chaoxing.study_video_d(course, job, job_info, _speed=speed, _type="Audio")
                            #同上上，调试关闭协议启动
                            else:
                                chaoxing.study_video(course, job, job_info, _speed=speed, _type="Audio")
                        except JSONDecodeError as e:
                            logger.warning(f"出现异常任务 -> 任务章节: {course['title']} 任务ID: {job['jobid']}, 已跳过")
                # 文档任务
                elif job["type"] == "document":
                    logger.trace(f"识别到文档任务, 任务章节: {course['title']} 任务ID: {job['jobid']}")
                    chaoxing.study_document(course, job)
                # 测验任务
                elif job["type"] == "workid":
                    logger.trace(f"识别到测验任务, 任务章节: {course['title']}")
                    pass
