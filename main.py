import os
import uiautomator2 as u2
import datetime
import time
import keyboard
import cv2 as cv

# deviceName = os.popen('adb devices').read()
d = u2.connect('127.0.0.1:62001')


# d = u2.connect()
#  公用左上角返回
# d.click(0.022, 0.046)     #返回
# time.sleep(1)
# d.click(0.498, 0.754)     #活动积分确认
# time.sleep(1)
# d.click(0.498, 0.754)     #活动积分确认
# d.click(0.074, 0.871)     #探险
# d.click(0.948, 0.409)     #菜单
# d.click(0.472, 0.402)     #商店
# d.click(0.28, 0.067)      #进入邀请赛
# d.click(0.5, 0.75)        # 确认


def cvcheck(filename, uiname):
    # 读取货物图片
    template = cv.imread('./pictemplate/' + filename)
    # 获取货物图片的长宽信息
    th, tw = template.shape[:2]
    Flag = True
    min_loc = 0
    global screen
    while Flag:
        d.screenshot('./screen/' + uiname + '.jpg', format='opencv')
        screen = cv.imread('./screen/' + uiname + '.jpg')
        # 调用 OpenCV 的模版匹配方法
        res = cv.matchTemplate(screen, template, cv.TM_SQDIFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)
        if min_val <= 0.16:
            d.click(0.28, 0.067)  # 进入邀请赛
            print('找到了', min_val)
            Flag = False
            # min_val 可用来判断是否检测到货物
            # 矩形左上角坐标
            tl = min_loc
            # 矩形右下角坐标
            br = (tl[0] + tw, tl[1] + th)
            cv.rectangle(screen, tl, br, (0, 0, 255), 2)
            cv.imwrite('cvcheck.jpg', screen)
            return False  # 找到了我就返回
        else:
            print('没找到', min_val)
    # min_val 可用来判断是否检测到货物
    # 矩形左上角坐标
    tl = min_loc
    # 矩形右下角坐标
    br = (tl[0] + tw, tl[1] + th)
    cv.rectangle(screen, tl, br, (0, 0, 255), 2)
    cv.imwrite('Result.jpg', screen)


def cvcheckGuiLai(filename, uiname):
    template = cv.imread('./pictemplate/' + filename)
    # 获取货物图片的长宽信息
    th, tw = template.shape[:2]
    Flag = True
    min_loc = 0
    global screen
    while Flag:
        d.screenshot('./screen/' + uiname + '.jpg', format='pillow')
        screen = cv.imread('./screen/' + uiname + '.jpg')
        # 调用 OpenCV 的模版匹配方法
        res = cv.matchTemplate(screen, template, cv.TM_SQDIFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)
        if min_val <= 0.2:
            print('找到了，已截图到根目录下cvcheckGuiLai.jpg', min_val)
            d.click(0.848, 0.238)  # 进入守护者归来
            Flag = False
            # min_val 可用来判断是否检测到货物
            # 矩形左上角坐标
            tl = min_loc
            # 矩形右下角坐标
            br = (tl[0] + tw, tl[1] + th)
            cv.rectangle(screen, tl, br, (0, 0, 255), 2)
            cv.imwrite('cvcheckGuiLai.jpg', screen)
            return False  # 找到了我就返回
        else:
            print('没找到，继续找', min_val)


def cvcheckBingo(filename, uiname):
    # 读取货物图片
    template = cv.imread('./pictemplate/' + filename)
    # 获取货物图片的长宽信息
    th, tw = template.shape[:2]
    Flag = True
    min_loc = 0
    global screen
    while Flag:
        d.screenshot('./screen/' + uiname + '.jpg', format='opencv')
        screen = cv.imread('./screen/' + uiname + '.jpg')
        # 调用 OpenCV 的模版匹配方法
        res = cv.matchTemplate(screen, template, cv.TM_SQDIFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)
        if min_val <= 0.18:
            print('找到了，已截图到根目录下cvcheckBingo.jpg', min_val)
            d.click(0.848, 0.238)  # 进入开心宾果乐
            d.click(0.848, 0.238)  # 进入开心宾果乐
            Flag = False
            # min_val 可用来判断是否检测到货物
            # 矩形左上角坐标
            tl = min_loc
            # 矩形右下角坐标
            br = (tl[0] + tw, tl[1] + th)
            cv.rectangle(screen, tl, br, (0, 0, 255), 2)
            cv.imwrite('cvcheckBingo.jpg', screen)
            return False  # 找到了我就返回
        else:
            print('没找到，继续找', min_val)


def confirm(filename, uiname, dx, dy):
    # 读取货物图片
    template = cv.imread('./pictemplate/' + filename)
    # 获取货物图片的长宽信息
    th, tw = template.shape[:2]
    Flag = True
    min_loc = 0
    global screen
    while Flag:
        d.screenshot('./screen/' + uiname + '.jpg', format='opencv')
        screen = cv.imread('./screen/' + uiname + '.jpg')
        # 调用 OpenCV 的模版匹配方法
        res = cv.matchTemplate(screen, template, cv.TM_SQDIFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)
        if min_val <= 0.05:
            print('找到了，已截图到根目录下confirm.jpg', min_val)
            d.click(dx, dy)  # 点击确认按钮
            Flag = False
            # min_val 可用来判断是否检测到货物
            # 矩形左上角坐标
            tl = min_loc
            # 矩形右下角坐标
            br = (tl[0] + tw, tl[1] + th)
            cv.rectangle(screen, tl, br, (0, 0, 255), 2)
            cv.imwrite('confirm.jpg', screen)
            return False  # 找到了我就返回
        else:
            print('没找到，继续找', min_val)
    # min_val 可用来判断是否检测到货物
    # 矩形左上角坐标
    tl = min_loc
    # 矩形右下角坐标
    br = (tl[0] + tw, tl[1] + th)
    cv.rectangle(screen, tl, br, (0, 0, 255), 2)
    cv.imwrite('ConfirmResult.jpg', screen)


def confirmLimit(filename, uiname, dx, dy):
    # 读取货物图片
    template = cv.imread('./pictemplate/' + filename)
    # 获取货物图片的长宽信息
    th, tw = template.shape[:2]
    Flag = True
    min_loc = 0
    global screen
    count = 10
    while count != 0:
        count = count - 1
        d.screenshot('./screen/' + uiname + '.jpg', format='opencv')
        screen = cv.imread('./screen/' + uiname + '.jpg')
        # 调用 OpenCV 的模版匹配方法
        res = cv.matchTemplate(screen, template, cv.TM_SQDIFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)
        if min_val <= 0.16:
            print('找到了，已截图到根目录下confirmLimit.jpg', min_val)
            d.click(dx, dy)  # 点击确认按钮
            Flag = False
            # min_val 可用来判断是否检测到货物
            # 矩形左上角坐标
            tl = min_loc
            # 矩形右下角坐标
            br = (tl[0] + tw, tl[1] + th)
            cv.rectangle(screen, tl, br, (0, 0, 255), 2)
            cv.imwrite('confirmLimit.jpg', screen)
            return False  # 找到了我就返回
        else:
            print('没找到-2500，继续找', min_val)
    # min_val 可用来判断是否检测到货物
    # 矩形左上角坐标
    tl = min_loc
    # 矩形右下角坐标
    br = (tl[0] + tw, tl[1] + th)
    cv.rectangle(screen, tl, br, (0, 0, 255), 2)
    cv.imwrite('ConfirmResult.jpg', screen)


def close(filename, uiname, dx, dy):
    # 读取货物图片
    template = cv.imread('./pictemplate/' + filename)
    # 获取货物图片的长宽信息
    th, tw = template.shape[:2]
    Flag = True
    min_loc = 0
    global screen
    count = 10
    while count != 0:
        count = count - 1
        d.screenshot('./screen/' + uiname + '.jpg', format='opencv')
        screen = cv.imread('./screen/' + uiname + '.jpg')
        # 调用 OpenCV 的模版匹配方法
        res = cv.matchTemplate(screen, template, cv.TM_SQDIFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)
        if min_val <= 0.05:
            print('找到了，已截图到根目录下confirm.jpg', min_val)
            d.click(dx, dy)  # 点击确认按钮
            Flag = False
            # min_val 可用来判断是否检测到货物
            # 矩形左上角坐标
            tl = min_loc
            # 矩形右下角坐标
            br = (tl[0] + tw, tl[1] + th)
            cv.rectangle(screen, tl, br, (0, 0, 255), 2)
            cv.imwrite('close.jpg', screen)
            return False  # 找到了我就返回
        else:
            print('没找到，继续找', min_val)
    # min_val 可用来判断是否检测到货物
    # 矩形左上角坐标
    tl = min_loc
    # 矩形右下角坐标
    br = (tl[0] + tw, tl[1] + th)
    cv.rectangle(screen, tl, br, (0, 0, 255), 2)
    cv.imwrite('ConfirmResult.jpg', screen)


def first():
    d.app_start('com.bilibili.snake')
    print('打开程序')
    time.sleep(7)
    d.click(0.496, 0.882)  # 点击进入
    time.sleep(3)
    d.click(0.496, 0.882)  # 点击进入
    time.sleep(3)
    d.click(0.496, 0.882)  # 点击进入
    print('进入界面1')
    time.sleep(3)
    d.click(0.496, 0.882)  # 点击进入
    print('等待10秒')
    time.sleep(15)
    d.click(0.512, 0.701)  # 点击进入
    d.click(0.512, 0.701)  # 点击进入
    print('进入主界面')
    time.sleep(23)


def qd():
    c1 = 'close.jpg'
    c2 = 'close'
    time.sleep(2.5)
    print('关闭公告')
    close(c1, c2, 0.966, 0.11)
    time.sleep(2)
    print('点旁边')
    d.click(0.784, 0.889)
    time.sleep(1)
    print('领取奖励')
    d.click(0.498, 0.864)  # 领取签到奖励
    time.sleep(1)
    print('确认奖励')
    d.click(0.504, 0.761)  # 确认奖励
    time.sleep(1)
    d.click(0.5, 0.739)  # 领取奖励
    time.sleep(0.2)
    d.click(0.5, 0.75)  # 确认奖励
    time.sleep(0.2)
    d.click(0.499, 0.733)
    print('签到结束')
    time.sleep(0.7)


def Email():
    d.click(0.92, 0.039)  # 进入邮件
    time.sleep(1)
    d.click(0.918, 0.886)  # 全部接收
    time.sleep(1)
    d.click(0.496, 0.754)  # 全部接收确认
    time.sleep(1)
    d.click(0.022, 0.046)  # 返回家园
    time.sleep(2)
    print('邮件领取完成')


def store():
    time.sleep(1)
    d.click(0.948, 0.409)  # 菜单
    time.sleep(1)
    d.click(0.472, 0.402)  # 商店
    time.sleep(2)
    d.click(0.082, 0.338)  # 资源
    time.sleep(1)
    d.click(0.5, 0.626)  # 金币
    time.sleep(1)
    d.click(0.584, 0.8)  # 金币确认
    time.sleep(1)
    d.click(0.5, 0.75)  # 确认
    time.sleep(1)
    # 每周
    # d.click(0.102, 0.469)     #英雄成长
    # time.sleep(1)
    # d.click(0.312, 0.569)     #传说觉醒石
    # time.sleep(1)
    # d.swipe(0.33, 0.626, 0.676, 0.626)  # 购买三个
    # time.sleep(1.5)
    # d.click(0.572, 0.85)      #确认
    # time.sleep(1)
    # d.click(0.496, 0.747)     #确认
    # time.sleep(1)
    d.click(0.026, 0.046)  # 返回家园
    time.sleep(1)
    d.click(521, 370)
    time.sleep(3)
    print('商店奖励领取完毕')


def jiayuan():
    d.click(0.446, 0.58)  # 旅馆
    print('进入旅馆')
    time.sleep(1)
    print('一键领取')
    d.click(0.664, 0.857)  # 一键领取
    time.sleep(1)
    print('向下拖动1')
    d.drag(0.51, 0.523, 0.512, 0.021, 0.2)  # 向下拖动
    time.sleep(1)
    print('向下拖动1')
    d.drag(0.51, 0.523, 0.512, 0.021, 0.2)  # 向下拖动
    time.sleep(1)
    print('守护者')
    d.click(0.512, 0.647)  # 守护者基地
    time.sleep(1)
    print('守护者领取')
    d.click(0.828, 0.871)  # 领取
    time.sleep(1)
    print('守护者领取确认')
    d.click(0.5, 0.74)  # 确认
    time.sleep(1)
    print('守护者领取关闭')
    d.click(0.888, 0.103)  # 关闭
    time.sleep(1)
    print('向上')
    d.swipe(0.5, 0.469, 0.5, 0.900, 0.5)  # 向上
    time.sleep(1)
    print('向上')
    d.swipe(0.5, 0.469, 0.5, 0.900, 0.5)  # 向上
    time.sleep(3)
    d.click(0.508, 0.626)  # 小公主
    time.sleep(2)
    d.click(0.5, 0.75)  # 确认
    print('家园奖励领取完成')


def liehen(flag, status):
    print('探险')
    d.click(0.074, 0.871)  # 探险
    time.sleep(2)
    print('裂痕')
    d.click(0.056, 0.266)  # 裂痕
    time.sleep(1)
    if flag == 1:
        print('进入单人进化石')
        d.click(0.778, 0.533)  # 单人进化石
        time.sleep(1)
        print('80光')
        d.click(0.792, 0.48)  # 80光
        time.sleep(1)
    elif flag == 2:
        print('进入伤害减免副本')
        d.click(0.801, 0.845)  # 伤害减免副本
        time.sleep(1)
        print('80暗')
        d.click(0.792, 0.48)  # 80暗
        time.sleep(1)
    elif flag == 3:
        print('进入强化技能副本')
        d.click(0.802, 0.272)  # 强化技能副本
        time.sleep(1)
        print('80虚')
        d.click(0.817, 0.64)  # 80土
        time.sleep(1)
    elif flag == 4:
        print('进入伤害减免副本')
        d.click(0.801, 0.845)  # 伤害减免副本
        time.sleep(1)
        print('80水')
        d.click(1321, 573)  # 80水
        time.sleep(1)
    else:
        pass
    print('自动战斗')
    d.click(0.93, 0.893)  # 自动战斗
    time.sleep(1)
    print('战斗次数')
    d.swipe(0.372, 0.498, 0.636, 0.498)  # 战斗次数
    time.sleep(1)
    print('扫荡')
    d.click(0.656, 0.782)  # 扫荡
    time.sleep(5)
    print('扫荡确认')
    d.click(0.504, 0.832)  # 确认
    time.sleep(1)
    print('活动积分确认')
    d.click(0.424, 0.725)  # 活动积分确认
    time.sleep(1)
    print('活动积分确认1')
    d.click(0.424, 0.725)  # 活动积分确认
    print('单人进化石完成')
    time.sleep(1)
    print('返回裂痕')
    d.click(0.022, 0.046)  # 返回裂痕
    time.sleep(1)
    if status == 1:
        d.click(0.022, 0.046)  # 返回世界地图
        time.sleep(1)
        d.click(0.022, 0.046)  # 返回世界地图
        print('返回世界地图')
        time.sleep(1)
        return
    else:
        pass
    d.click(0.298, 0.747)  # 觉醒副本
    time.sleep(1)
    d.click(0.816, 0.612)  # 70觉醒
    time.sleep(1)
    d.click(0.93, 0.893)  # 自动战斗
    time.sleep(1)
    print('战斗次数3次')
    d.click(0.676, 0.491)  # 战斗次数3次
    time.sleep(0.2)
    d.click(0.676, 0.491)
    time.sleep(1)
    print('扫荡')
    d.click(0.656, 0.782)  # 扫荡
    time.sleep(7)
    print('扫荡确认')
    d.click(0.504, 0.832)  # 确认
    time.sleep(1)
    print('活动积分确认')
    d.click(0.424, 0.725)  # 活动积分确认
    time.sleep(1)
    print('活动积分确认1')
    d.click(0.424, 0.725)  # 活动积分确认
    print('觉醒完成返回裂痕')
    time.sleep(1)
    d.click(0.022, 0.046)  # 返回裂痕
    time.sleep(1)
    print('返回世界地图')
    d.click(0.022, 0.046)  # 返回世界地图
    time.sleep(1)
    print('返回')
    d.click(0.022, 0.046)  # 返回世界地图
    time.sleep(1)
    print('裂痕完成')


def yuanxing():
    print('圆形开始')
    time.sleep(2)
    d.click(0.074, 0.871)  # 探险
    time.sleep(2)
    d.click(0.058, 0.576)  # 进入圆形
    time.sleep(4)
    d.click(0.572, 0.918)  # 受到攻击确认
    time.sleep(2)
    d.click(0.5, 0.75)  # 赛季奖励确认
    yx1 = 'confirmbtn.jpg'
    yx2 = 'confirmbtn'
    # 796, 806
    dx1 = 796
    dy1 = 675  # 段位升级确认坐标
    dx2 = 796
    dy2 = 806  # 下方确认坐标
    dx3 = 793
    dy3 = 678
    for i in range(1, 6):
        time.sleep(1)
        print('选择敌人')
        d.click(0.89, 0.455)  # 选择敌人
        time.sleep(1)
        print('开始战斗')
        d.click(0.618, 0.893)  # 开始战斗
        time.sleep(7)
        print('段位升级确认中')
        confirm(yx1, yx2, dx1, dy1)  # 段位升级确认
        print('段位升级确认完毕')
        time.sleep(1)
        print('战斗完成点击确认')
        confirm(yx1, yx2, dx2, dy2)  # 确认
        print('战斗完成确认点击完成')
        time.sleep(3)
        print('活动积分检测确认')
        confirm(yx1,yx2,dx3,dy3)
        # d.click(0.498, 0.754)  # 活动积分确认 793, 678
        print('活动积分确认完成')
        time.sleep(1)
        d.click(0.498, 0.754)  # 活动积分确认
        time.sleep(2)
        d.click(0.942, 0.313)  # 刷新敌人
    time.sleep(1)
    d.click(0.022, 0.046)  # 返回
    time.sleep(1)
    d.click(0.022, 0.046)  # 返回家园
    time.sleep(3)
    print('圆形结束')


def gonghui():
    d.click(0.924, 0.633)  # 工会
    time.sleep(1)
    d.click(0.59, 0.758)  # 确认进入
    time.sleep(10)
    d.click(0.498, 0.864)  # 讨伐确认
    time.sleep(1)
    d.long_click(0.144, 0.608, 0.5)
    time.sleep(1)
    d.click(0.904, 0.814)  # 对话
    time.sleep(1)
    d.click(0.398, 0.385)  # 签到
    time.sleep(0.5)
    d.click(0.398, 0.441)  # 签到  往下点
    time.sleep(1)
    d.click(0.392, 0.576)  # 签到
    time.sleep(1)
    d.click(0.408, 0.708)  # 签到
    time.sleep(1)
    d.click(0.404, 0.839)  # 签到
    time.sleep(1)
    print('签到确认')
    d.click(0.5, 0.754)  # 签到确认
    time.sleep(1)
    d.click(0.942, 0.17)  # 签到关闭或者进入协力讨伐
    time.sleep(2)
    d.click(0.5, 0.807)  # 协力奖励领取
    time.sleep(1)
    print('返回主城')
    d.click(0.964, 0.056)  # 返回主城
    time.sleep(2)
    print('返回主城确认')
    d.click(0.59, 0.754)  # 返回主城确认
    time.sleep(7)


def guilai():
    back1 = 'shouhuzhe.jpg'
    back2 = 'shouhuzhe'
    cvcheckGuiLai(back1, back2)
    print("回归奖励开始")
    # d.click(0.848, 0.238)
    d.click(0.427, 0.435)
    time.sleep(0.5)
    d.click(0.501, 0.758)
    print('第一天领取')
    d.click(0.582, 0.435)
    time.sleep(0.5)
    d.click(0.501, 0.758)
    print('第二天领取')
    d.click(0.729, 0.432)
    time.sleep(0.5)
    d.click(0.501, 0.758)
    print('第三天领取')
    d.click(0.427, 0.756)
    time.sleep(0.5)
    d.click(0.501, 0.758)
    print('第四天领取')
    d.click(0.574, 0.77)
    time.sleep(0.5)
    d.click(0.501, 0.758)
    print('第五天领取')
    d.click(0.73, 0.763)
    time.sleep(0.5)
    d.click(0.501, 0.758)
    print('第六天领取')
    d.click(0.878, 0.564)
    time.sleep(0.5)
    d.click(0.501, 0.758)
    print('第七天领取')
    time.sleep(1)
    d.click(0.654, 0.165)
    time.sleep(0.5)
    d.click(0.897, 0.901)
    time.sleep(0.5)
    d.click(0.505, 0.801)
    time.sleep(0.5)
    d.click(0.022, 0.046)
    print('回归奖励完毕')
    time.sleep(2)


def hapyybingo():
    # 0.497, 0.796
    dx = 800
    dy = 715
    print('开心宾果乐开始')
    hp1 = 'happy.jpg'
    hp2 = 'happy'
    hp3 = 'confirmbtn.jpg'
    hp4 = 'confirmbtn'
    hp5 = 'happy2500.jpg'
    hp6 = 'happy2500'
    cvcheckBingo(hp1, hp2)  # 检测BINGO轮播
    time.sleep(5)
    d.click(0.263, 0.896)  # 点击2500
    time.sleep(0.2)
    d.click(0.476, 0.752)  # 奖励确认或2500不够点击确认
    confirmLimit(hp3, hp4, dx, dy)  # 点击2500后，实时检测确认按钮
    time.sleep(0.4)
    if happyconfirm(hp5, hp6):  # 检测够不够2500，不够直接返回 如果够 继续进行
        print('happyconfirm IF循环')
        d.click(0.022, 0.046)  # 返回
        time.sleep(2)
        return
    else:
        pass
    d.click(0.504, 0.799)
    time.sleep(0.2)
    d.click(0.263, 0.896)
    time.sleep(0.2)
    d.click(0.476, 0.752)
    confirmLimit(hp3, hp4, dx, dy)
    time.sleep(1)
    d.click(0.504, 0.799)
    time.sleep(0.2)
    d.click(0.022, 0.046)  # 返回
    time.sleep(2)


def happyconfirm(filename, uiname):
    # 读取图片
    template = cv.imread('./pictemplate/' + filename)
    # 获取图片的长宽信息
    th, tw = template.shape[:2]
    Flag = True
    min_loc = 0
    global screen
    while Flag:
        d.screenshot('./screen/' + uiname + '.jpg', format='opencv')
        screen = cv.imread('./screen/' + uiname + '.jpg')
        # 调用 OpenCV 的模版匹配方法
        res = cv.matchTemplate(screen, template, cv.TM_SQDIFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)
        if min_val <= 0.1:
            print('找到了，已截图到根目录下Result.jpg', min_val)
            Flag = False
            tl = min_loc
            # 矩形右下角坐标
            br = (tl[0] + tw, tl[1] + th)
            cv.rectangle(screen, tl, br, (0, 0, 255), 2)
            cv.imwrite('ConfirmResult.jpg', screen)
            return True  # 找到了我就返回
        else:
            print('没找到，继续找', min_val)

    # 矩形左上角坐标
    tl = min_loc
    # 矩形右下角坐标
    br = (tl[0] + tw, tl[1] + th)
    cv.rectangle(screen, tl, br, (0, 0, 255), 2)
    cv.imwrite('ConfirmResult.jpg', screen)


def yaoqingsai():
    print('邀请赛开始')
    yqs = 'mainUI'
    shouhu = 'shouhu.jpg'
    cvcheck(shouhu, yqs)
    # d.click(0.28, 0.067)  # 进入邀请赛
    time.sleep(1)
    d.click(0.824, 0.234)  # 邀请函目标
    time.sleep(0.5)
    d.click(0.884, 0.896)  # 全部领取
    time.sleep(0.5)
    d.click(0.492, 0.754)  # 确认领取
    time.sleep(15)
    d.click(0.494, 0.231)  # 邀请函奖励
    time.sleep(0.5)
    d.click(0.884, 0.896)  # 全部领取
    time.sleep(0.5)
    d.click(0.492, 0.754)  # 确认领取
    time.sleep(1)
    d.click(0.022, 0.046)  # 返回
    d.click(0.022, 0.046)  # 返回
    time.sleep(2)
    print('邀请赛完成')


def richang():
    time.sleep(1)
    d.click(0.296, 0.889)  # 进入日常
    time.sleep(2)
    d.click(0.878, 0.889)  # 全部领取
    time.sleep(1)
    d.click(0.486, 0.782)  # 奖励确认
    time.sleep(1)
    d.click(0.486, 0.782)  # 奖励确认
    time.sleep(1)
    d.click(0.616, 0.149)  # 进入挑战
    time.sleep(1)
    d.click(0.878, 0.889)  # 全部领取
    time.sleep(1)
    d.click(0.486, 0.782)  # 奖励确认
    time.sleep(1)
    d.click(0.486, 0.782)  # 奖励确认
    time.sleep(1)
    d.click(0.844, 0.16)  # 活动
    time.sleep(1)
    d.click(0.878, 0.889)  # 全部领取
    time.sleep(1)
    d.click(0.486, 0.782)  # 奖励确认
    time.sleep(1)
    d.click(0.486, 0.782)  # 奖励确认
    time.sleep(1)
    d.click(0.022, 0.046)  # 返回
    time.sleep(1)
    print('日常结束')


def changeaccount1(name):
    d.app_stop("com.bilibili.snake")
    time.sleep(3)
    d.app_start('com.bilibili.snake')
    print('打开程序')
    time.sleep(7)
    d.click(0.496, 0.882)  # 点击进入
    d.click(0.496, 0.882)  # 点击进入
    d.click(0.496, 0.882)  # 点击进入
    time.sleep(4)
    d.click(0.496, 0.882)  # 点击进入
    time.sleep(10)
    print('切换账号')
    d.click(0.884, 0.06)
    time.sleep(2)
    d.click(0.884, 0.06)
    time.sleep(6)
    d.xpath('//*[@resource-id="com.bilibili.snake:id/rl_gsc_recode_login"]/android.widget.ImageView[2]').click()
    time.sleep(2)
    path = '//*[@text="' + name + '"]'
    d.xpath(path).click()
    # d.xpath('//*[@text="是祁天不是齐天"]').click()
    time.sleep(2)
    d.xpath('//*[@resource-id="com.bilibili.snake:id/tv_gsc_record_login"]').click()  # 登录
    print('手动进行验证码')
    time.sleep(15)


def allAuto(flag):
    qd()
    Email()
    jiayuan()
    yuanxing()
    gonghui()
    guilai()
    hapyybingo()
    liehen(flag, 0)
    richang()
    yaoqingsai()
    store()
    guilai()
    liehen(flag, 1)
    richang()


def qitian():
    time.sleep(5)  # 预热
    first()
    allAuto(4)
    changeaccount1('nee0631')


def nee():
    allAuto(1)
    changeaccount1('uye6153')
    time.sleep(15)


def uye():
    allAuto(1)
    changeaccount1('是祁天不是齐天')
    time.sleep(10)
    d.app_stop("com.bilibili.snake")
    print('脚本完成')


if __name__ == '__main__':
    d = u2.connect('127.0.0.1:62001')
    qitian()
    nee()
    uye()
