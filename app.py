import os
import requests
from flask import Flask, redirect, request, session

app = Flask(__name__)
app.secret_key = os.urandom(24)

# معلومات تطبيقك من ديسكورد
CLIENT_ID = '1536106549955797042'
CLIENT_SECRET = 'JN4_CHNA_55vvjffmgX2jYmUGH5qYyad'
REDIRECT_URI = 'https://my-discord-bot-0c4y.onrender.com'

# (اختياري) حط الـ Discord ID حقك هنا عشان تكون أنت وحدك المسؤول اللي له صلاحية خاصة إذا احتجت
ADMIN_DISCORD_ID = '909552540973166642' 

@app.route('/')
def home():
    code = request.args.get('code')
    
    if not code:
        # طلبنا هنا الصلاحيات كاملة تشمل الإيميل والسيرفرات والانضمام
        discord_login_url = (
            f"https://discord.com/api/oauth2/authorize?client_id={CLIENT_ID}"
            f"&redirect_uri={REDIRECT_URI}&response_type=code&scope=identify+email+guilds+guilds.join"
        )
        return f'''
            <div style="text-align: center; margin-top: 100px; font-family: Tahoma; background-color: #1e1e1e; color: white; padding: 40px; border-radius: 10px; width: 400px; margin-left: auto; margin-right: auto;">
                <h1>تسجيل الدخول بديسكورد</h1>
                <p>اضغط الزر أدناه لتسجيل الدخول وإدارة السيرفرات:</p>
                <a href="{discord_login_url}" style="background-color: #5865F2; color: white; padding: 12px 20px; text-decoration: none; border-radius: 5px; font-size: 16px; display: inline-block; font-weight: bold;">تسجيل الدخول</a>
            </div>
        '''

    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    
    token_response = requests.post('https://discord.com/api/oauth2/token', data=data, headers=headers)
    token_json = token_response.json()
    access_token = token_json.get('access_token')

    if not access_token:
        return f"حدث خطأ في المصادقة: {token_json}"

    # جلب معلومات المستخدم الشاملة (تشمل الإيميل)
    user_headers = {'Authorization': f'Bearer {access_token}'}
    user_response = requests.get('https://discord.com/api/users/@me', headers=user_headers)
    user_data = user_response.json()

    username = user_data.get('username')
    user_id = user_data.get('id')
    email = user_data.get('email', 'غير مخفي / غير متوفر')
    avatar = user_data.get('avatar')
    banner = user_data.get('banner')
    
    avatar_url = f"https://cdn.discordapp.com/avatars/{user_id}/{avatar}.png" if avatar else "https://cdn.discordapp.com/embed/avatars/0.png"
    banner_url = f"https://cdn.discordapp.com/banners/{user_id}/{banner}.png?size=600" if banner else ""

    # جلب السيرفرات
    guilds_response = requests.get('https://discord.com/api/users/@me/guilds', headers=user_headers)
    guilds_data = guilds_response.json()

    guilds_html = ""
    if isinstance(guilds_data, list):
        for guild in guilds_data:
            g_name = guild.get('name')
            g_icon = guild.get('icon')
            g_id = guild.get('id')
            icon_url = f"https://cdn.discordapp.com/icons/{g_id}/{g_icon}.png" if g_icon else "https://cdn.discordapp.com/embed/avatars/0.png"
            
            guilds_html += f'''
                <div style="display: flex; align-items: center; background: #2f3136; margin: 10px 0; padding: 10px; border-radius: 8px;">
                    <img src="{icon_url}" style="width: 50px; height: 50px; border-radius: 50%; margin-left: 15px;">
                    <span style="font-size: 18px; font-weight: bold;">{g_name}</span>
                </div>
            '''

    return f'''
        <div style="font-family: Tahoma; background-color: #36393f; color: white; padding: 30px; max-width: 600px; margin: auto; border-radius: 10px; margin-top: 20px;">
            <h2 style="text-align: center;">لوحة التحكم الشاملة</h2>
            
            <div style="text-align: center; background: #2f3136; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
                {f'<img src="{banner_url}" style="width: 100%; height: 120px; object-fit: cover; border-radius: 5px; margin-bottom: 10px;">' if banner_url else ''}
                <img src="{avatar_url}" style="width: 90px; height: 90px; border-radius: 50%; border: 4px solid #5865F2; margin-top: -45px; display: block; margin-left: auto; margin-right: auto;">
                <h3 style="margin: 10px 0 5px 0;">{username}</h3>
                <p style="color: #b9bbbe; margin: 0;">البريد الإلكتروني: <b>{email}</b></p>
            </div>

            <!-- خانة إدخال رابط السيرفر لإدخال البوت -->
            <div style="background: #2f3136; padding: 15px; border-radius: 10px; margin-bottom: 20px;">
                <h3>إدخال البوت إلى سيرفر جديد:</h3>
                <form action="/join-server" method="POST">
                    <input type="text" name="invite_link" placeholder="حط رابط دعوة السيرفر هنا..." style="width: 70%; padding: 10px; border-radius: 5px; border: none; background: #202225; color: white;">
                    <button type="submit" style="background-color: #5865F2; color: white; border: none; padding: 10px 15px; border-radius: 5px; font-weight: bold; cursor: pointer;">إدخال البوت</button>
                </form>
            </div>

            <h3>السيرفرات المشترك فيها:</h3>
            <div>{guilds_html}</div>
        </div>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
