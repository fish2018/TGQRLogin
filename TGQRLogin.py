from telethon.sync import TelegramClient
from telethon.sessions import StringSession
import telethon
import jsonpickle
import json
import base64
import signal
from qrcode import QRCode, constants
import os
import asyncio

api_id = 6627460
api_hash = '27a53a0965e486a2bc1b1fcde473b1c4'

async def to_v2(v1,client):
    '''
    v1_stringsession_base64字符串 转 v2_stringsession_base64字符串
    可以接收v1 stringsession登录，再传入client
    '''
    user = await client.get_me()
    user_id = user.id
    # dc_id = user.photo.dc_id
    v1 = StringSession(v1)
    v1_json = json.loads(jsonpickle.encode(v1))
    dc_id = v1_json.get('_dc_id')
    ipv4 = v1_json.get('_server_address')
    port = v1_json.get('_port')
    auth_key = v1_json.get('_auth_key').get('_key')

    v2_json = json.dumps({
        "py/object": "telethon._impl.session.session.Session",
        "dcs": [{
            "py/object": "telethon._impl.session.session.DataCenter",
            "id": dc_id,
            "ipv4_addr": f"{ipv4}:{port}",
            "ipv6_addr": None,
            "auth": auth_key
        }],
        "user": {
            "py/object": "telethon._impl.session.session.User",
            "id": user_id,
            "dc": dc_id,
            "bot": False,
            "username": None
        },
        "state": {
        }
    })
    v2 = base64.b64encode(v2_json.encode('utf-8')).decode('utf-8')

    return v2

def show_qr(url):
    file_path = 'img/qr_code.jpg'
    print(f'QR code saved to {file_path}')
    qr = QRCode(
        version=1,
        error_correction=constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.clear()
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    img.save(file_path)

# 定义一个信号处理函数
def signal_handler(signum, frame):
    print("程序已运行超过1分钟，即将强制退出...")
    exit(0)

# 设置信号处理函数
signal.signal(signal.SIGALRM, signal_handler)

# 设置定时器，1分钟后发送SIGALRM信号
signal.alarm(60)

# 扫码登录获取v1和v2
async def main(client: telethon.TelegramClient):
    if not client.is_connected():
        await client.connect()
    await client.connect()
    qr_login = await client.qr_login()

    r = False
    while not r:
        show_qr(qr_login.url)
        # 等待登录完成
        try:
            r = await qr_login.wait(50)
        except:
            await qr_login.recreate()

    v1 = qr_login._client.session.save()
    print(f'v1: {v1}')
    # 转v2
    v2 = await to_v2(v1,client)
    print(f'v2: {v2}')

# 直接v1转v2
async def v1_to_v2(v1):
    async with TelegramClient(StringSession(v1), api_id, api_hash) as client:
        v2 = await to_v2(v1,client)
        print(f'v2: {v2}')

if __name__=='__main__':
    v1 = ''
    # v1 = "1BVtsOKMBu6_VDsOklhEyPD3gTwZa3GPO9ROBQHlktCICM5dcarPFD7BrTdE="
    if v1:
        asyncio.run(v1_to_v2(v1))
    else:
        try:
            client = TelegramClient(StringSession(), api_id, api_hash)
            client.loop.run_until_complete(main(client))
        except KeyboardInterrupt:
            print("程序被用户中断")
        except Exception as e:
            print(f"程序运行中出现错误: {e}")
        finally:
            # 关闭定时器
            signal.alarm(0)
            print("程序已退出")
