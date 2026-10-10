import os
import sys
import asyncio
import datetime
import discord
from discord import app_commands
from discord.ext import commands, tasks
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
NOTIFY_CHANNEL_ID = int(os.getenv("NOTIFY_CHANNEL_ID", 0))
SCHEDULE_CHANNEL_ID = int(os.getenv("SCHEDULE_CHANNEL_ID", 0))
ADMIN_USER_ID = int(os.getenv("ADMIN_USER_ID", 0))

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)
sent_links = set()
sys.stdout.reconfigure(encoding="utf-8")

streamer = []

def get_chrome_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--lang=zh-TW") 
    return webdriver.Chrome(options=options)

@bot.event
async def on_ready():
    print(f'{bot.user} 已上線')
    await read_links()
    
    try:
        synced = await bot.tree.sync()
        print(f"{len(synced)} 個指令")
    except Exception as e:
        print(f"同步指令失敗: {e}")

async def read_links():
    try:
        with open("link.txt", "r") as file:
            for line in file:
                if line.strip():
                    streamer.append(line.strip())
    except FileNotFoundError:
        print("沒有直播連結")

async def write_links(url):
      with open("link.txt", "a") as file:
            file.write(url + "\n")

async def cover_links():
      with open("link.txt", "w") as file:
            for link in streamer:
                  file.write(link + "\n")


@bot.tree.command(name="addlink", description="新增要追蹤的 YouTube 頻道連結")
async def addlink(interaction: discord.Interaction, url: str):
    streamer.append(url)
    await write_links(url)
    await interaction.response.send_message(f"已成功添加頻道連結：{url}")

@bot.tree.command(name="showlinks", description="顯示目前追蹤的所有頻道連結")
async def showlinks(interaction: discord.Interaction):
    if streamer:
        link_list = '\n'.join([f"{number + 1}. {link}" for number, link in enumerate(streamer)])
        await interaction.response.send_message(f"目前已添加的連結：\n```{link_list}```")
    else:
        await interaction.response.send_message("目前沒有任何連結")   

@bot.tree.command(name="deletelink", description="刪除指定編號的追蹤連結")
async def deletelink(interaction: discord.Interaction, number: int):
    if 0 < number <= len(streamer):
        deleted_link = streamer.pop(number - 1)
        await cover_links()
        await interaction.response.send_message(f"已刪除連結：{deleted_link}")
    else:
        await interaction.response.send_message("請提供有效的編號 (可使用 /showlinks 查詢)")


def check_streaming(url):
    driver = get_chrome_driver()
    try:
        driver.get(url)
        driver.implicitly_wait(5) 
        
        try:
            driver.find_element(By.CSS_SELECTOR, "[aria-label='輕觸即可觀看直播影片']")
        except:
            return False, None, None

        name = driver.find_element(By.CSS_SELECTOR, "h1.dynamicTextViewModelH1 span[role='text']").text
        
        return True, name, url
        
    except Exception as e:
        print(f"[{url}] error: {e}")
        return False, None, None
    finally:
        driver.quit()

def run_schedule():
    driver = get_chrome_driver()
    schedule = ""
    try:
        driver.get("https://hololive.hololivepro.com/en/schedule")
        driver.implicitly_wait(3)

        titles = [el.text for el in driver.find_elements(By.CLASS_NAME, "txt")]
        names = [el.text for el in driver.find_elements(By.CLASS_NAME, "name")]
        times = [el.text for el in driver.find_elements(By.CLASS_NAME, "start")]
        play_count = len(driver.find_elements(By.CLASS_NAME, "start.now"))

        for title, name, t in zip(titles, names, times):
            if not title or not name:
                continue
            if play_count > 0:
                schedule += f"\n🔴 [直播中] {t} - < {name} >\n{title}\n"
                play_count -= 1
            else:
                schedule += f"\n{t} - < {name} >\n{title}\n"
    except Exception as e:
        schedule = f"獲取行程失敗: {e}"
    finally:
        driver.quit()
    return schedule


async def send_long_message(channel, message):
    max_length = 1900  
    chunks = [message[i:i+max_length] for i in range(0, len(message), max_length)]
    for chunk in chunks:
        await channel.send(f"```{chunk}```")

@bot.tree.command(name="schedule", description="手動查詢今日 Hololive 行程表")
async def schedule_cmd(interaction: discord.Interaction):
    await interaction.response.defer() 
    schedule_message = await asyncio.to_thread(run_schedule)
    await send_long_message(interaction.channel, schedule_message)
    await interaction.followup.send("行程表查詢完畢")

@bot.tree.command(name="stream", description="手動檢查清單內的頻道是否正在直播")
async def stream_cmd(interaction: discord.Interaction):
    await interaction.response.defer()
    found_any = False
    
    for url in streamer:
        is_streaming, name, link = await asyncio.to_thread(check_streaming, url)
        if is_streaming and link not in sent_links:
            sent_links.add(link)
            await interaction.followup.send(f"Hey , 現在 < {name} > 直播中 !\n 連結 : {link}")
            found_any = True
            
    if not found_any:
        await interaction.followup.send("檢查完畢，目前無人直播")


@tasks.loop(minutes=5)
async def streaming_task():
    channel = bot.get_channel(NOTIFY_CHANNEL_ID)
    if not channel: return
    for url in streamer:
        is_streaming, name, link = await asyncio.to_thread(check_streaming, url)
        if is_streaming and link not in sent_links:
            sent_links.add(link)
            await channel.send(f"Hey , 現在 < {name} > 直播中 ! \n 連結 : {link}")

tz = datetime.timezone(datetime.timedelta(hours=8))
@tasks.loop(seconds=60)  
async def schedule_once_day():
    now = datetime.datetime.now(tz)
    if now.hour == 0 and now.minute == 0:
        sent_links.clear()
        schedule_message = await asyncio.to_thread(run_schedule)
        channel = bot.get_channel(SCHEDULE_CHANNEL_ID) 
        if channel:
            await send_long_message(channel, schedule_message)

@bot.tree.command(name="startstreaming", description="開啟 5 分鐘自動直播輪詢通知")
async def startstreaming(interaction: discord.Interaction):
    streaming_task.start()
    await interaction.response.send_message("▶️已開始自動直播通知")
    
@bot.tree.command(name="stopstreaming", description="關閉自動直播通知")
async def stopstreaming(interaction: discord.Interaction):
    streaming_task.stop()
    await interaction.response.send_message("⏸️已停止自動直播通知")

@bot.tree.command(name="startschedule", description="開啟每日自動發送行程表")
async def startschedule(interaction: discord.Interaction):
    schedule_once_day.start()
    await interaction.response.send_message("▶️已開始每日行程表推播")
    
@bot.tree.command(name="stopschedule", description="關閉每日行程表推播")
async def stopschedule(interaction: discord.Interaction):
    schedule_once_day.stop()
    await interaction.response.send_message("⏸️已停止每日行程表推播")

if __name__ == "__main__":
    bot.run(TOKEN)