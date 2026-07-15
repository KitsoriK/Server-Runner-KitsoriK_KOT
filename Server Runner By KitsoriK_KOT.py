from asyncio.windows_events import NULL
from math import e
import discord
from discord.ext import commands
from discord.ext import tasks
import subprocess
import json
import os
from mcrcon import MCRcon

ALLOWED_FILE = "allowed_users.json"
ADMIN_FILE = "admin_users.json"
CONFIG_FILE = "config_file.json"

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

def config():
    if not os.path.exists(CONFIG_FILE):
        None
    with open(CONFIG_FILE, "r") as f:
        settings = json.load(f)
    return settings

settings = config()

TOKEN = settings["TOKEN"]
OWNER_ID = settings["OWNER_ID"]

RCON_HOST = settings["RCON_HOST"]
RCON_PASSWORD = settings["RCON_PASSWORD"]
RCON_PORT = settings["RCON_PORT"]

server_path = settings["server_path"]
standard_server = settings["standard_server"]
russian = settings["russian"]

chanel_id = settings["chanel_id"]
chanel_cycle = settings["chanel_cycle"]
chanel_timer = settings["chanel_timer"]

def load_users(file):
    if not os.path.exists(file):
        return []
    with open(file, "r") as f:
        return json.load(f)

def save_users(users, file):
    with open(file, "w") as f:
        json.dump(users, f)

allowed_users = load_users(ALLOWED_FILE)
admin_users = load_users(ADMIN_FILE)

def is_owner(user_id):
    return user_id == OWNER_ID

def is_admin(user_id):
    return user_id in admin_users or is_owner(user_id)

def is_allowed(user_id):
    return user_id in allowed_users or is_admin(user_id) or is_owner(user_id)

def is_any_server_running():
    result = subprocess.run(
        "wmic process where name='java.exe' get CommandLine",
        capture_output=True,
        text=True,
        shell=True
    )

    cmd = result.stdout.lower()

    keywords = [
        "minecraft",
        "forge",
        "fabric",
        "neoforge",
        "server.jar",
        ".jar"
    ]

    return any(word in cmd for word in keywords)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Bot started like {bot.user}")

@tasks.loop(minutes=30)
async def send_message():
    channel = bot.get_channel(chanel_id)
    if channel and chanel_cycle:
        if russian:
            if is_any_server_running():
                await channel.send("🟢 Какой-то сервер работает", ephemeral=True)
            else:
                await channel.send("🔴 Все сервера остановлены", ephemeral=True)
        else:
            if is_any_server_running():
                await channel.send("🟢 Some server is running", ephemeral=True)
            else:
                await channel.send("🔴 Every server is running", ephemeral=True)

@bot.tree.command(name="run", description="Start a server")
async def run(interaction: discord.Interaction, server_name: str = ""):
    if not is_allowed(interaction.user.id):
        if russian:
            await interaction.response.send_message("Нет доступа", ephemeral=True)
            return
        else:
            await interaction.response.send_message("Access denied", ephemeral=True)
            return

    if server_name:
        bat_file = rf"{server_path}/{server_name}/Start.bat"
    else:
        bat_file = rf"{server_path}/{standard_server}/Start.bat"

    if not os.path.exists(bat_file):
        if russian:
            await interaction.response.send_message(f"❌ Неизвестный сервер `{server_name}`", ephemeral=False)
            return
        else:
            await interaction.response.send_message(f"❌ Unknown server `{server_name}`", ephemeral=False)
            return

    if is_any_server_running():
        if russian:
            await interaction.response.send_message("❌ Уже запущен этот или другой сервер", ephemeral=False)
            return
        else:
            await interaction.response.send_message("❌ Some server is already running", ephemeral=False)
            return

    try:
        subprocess.Popen(
            f'cmd /c "{bat_file}"',
            cwd=os.path.dirname(bat_file),
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )

        if russian:
            if server_name:
                await interaction.response.send_message(f"🟢 Запущен сервер `{server_name}`", ephemeral=False)
            else:
                await interaction.response.send_message(f"🟢 Запущен сервер `{standard_server}`", ephemeral=False)
        else:
            if server_name:
                await interaction.response.send_message(f"🟢 Started server `{server_name}`", ephemeral=False)
            else:
                await interaction.response.send_message(f"🟢 Started server `{standard_server}`", ephemeral=False)

    except Exception as e:
        if russian:
            await interaction.response.send_message(f"Ошибка запуска: {e}", ephemeral=False)
        else:
            await interaction.response.send_message(f"Starting error: {e}", ephemeral=False)

@bot.tree.command(name="status", description="Check server status")
async def status_command(interaction: discord.Interaction):
    if russian:
        if is_any_server_running():
            await interaction.response.send_message("🟢 Какой-то сервер работает", ephemeral=True)
        else:
            await interaction.response.send_message("🔴 Все сервера остановлены", ephemeral=True)
    else:
        if is_any_server_running():
            await interaction.response.send_message("🟢 Some server is running", ephemeral=True)
        else:
            await interaction.response.send_message("🔴 Every server is running", ephemeral=True)


@bot.tree.command(name="stop", description="Stop a server")
async def stop_command(interaction: discord.Interaction):
    if not is_admin(interaction.user.id):
        if russian:
            await interaction.response.send_message("Только админ может останавливать", ephemeral=True)
            return
        else:
            await interaction.response.send_message("Only admin can stop", ephemeral=True)
            return

    if russian:
        await interaction.response.send_message("❌ Остановка сервера!!!", ephemeral=False)
    else:
        await interaction.response.send_message("❌ Stopping!!!", ephemeral=False)

    with MCRcon(RCON_HOST, RCON_PASSWORD, RCON_PORT=RCON_PORT) as mcr:
        mcr.command("stop")


@bot.tree.command(name="add", description="Add user")
async def add_command(interaction: discord.Interaction, user: discord.User):

    if not is_admin(interaction.user.id):
        if russian:
            await interaction.response.send_message("Только админ может добавлять", ephemeral=True)
            return
        else:
            await interaction.response.send_message("Only admin can add", ephemeral=True)
            return

    if user.id in allowed_users:
        if russian:
            await interaction.response.send_message("Уже есть в списке", ephemeral=True)
            return
        else:
            await interaction.response.send_message("Already in the list", ephemeral=True)
            return

    allowed_users.append(user.id)
    save_users(allowed_users, ALLOWED_FILE)

    if russian:
        await interaction.response.send_message(f"<@{user.id}> добавлен", ephemeral=False)
    else:
        await interaction.response.send_message(f"<@{user.id}> added", ephemeral=False)


@bot.tree.command(name="remove", description="Remove user")
async def remove_command(interaction: discord.Interaction, user: discord.User):

    if not is_admin(interaction.user.id):
        if russian:
            await interaction.response.send_message("Только админ может удалять", ephemeral=True)
            return
        else:
            await interaction.response.send_message("Only admin can remove", ephemeral=True)
            return

    if user.id not in allowed_users:
        if russian:
            await interaction.response.send_message("Его нет в списке", ephemeral=True)
            return
        else:
            await interaction.response.send_message("Not in the list", ephemeral=True)
            return

    allowed_users.remove(user.id)
    save_users(allowed_users, ALLOWED_FILE)

    if russian:
        await interaction.response.send_message(f"<@{user.id}> удалён", ephemeral=False)
    else:
        await interaction.response.send_message(f"<@{user.id}> removed", ephemeral=False)


@bot.tree.command(name="list", description="Show allowed users")
async def list_command(interaction: discord.Interaction):

    if not is_allowed(interaction.user.id):
        if russian:
            await interaction.response.send_message("Нет доступа", ephemeral=True)
            return
        else:
            await interaction.response.send_message("Access denied", ephemeral=True)
            return

    if not allowed_users:
        if russian:
            await interaction.response.send_message("Список пуст", ephemeral=True)
            return
        else:
            await interaction.response.send_message("List is empty", ephemeral=True)
            return

    users = "\n".join([f"<@{uid}>" for uid in allowed_users])

    if russian:
        await interaction.response.send_message(f"Разрешённые:\n{users}", ephemeral=True)
    else:
        await interaction.response.send_message(f"Allowed:\n{users}", ephemeral=True)

@bot.tree.command(name="addadmin", description="Add admin")
async def addadmin_command(interaction: discord.Interaction, user: discord.User):

    if not is_owner(interaction.user.id):
        if russian:
            await interaction.response.send_message("Только владелец может добавлять админов", ephemeral=True)
            return
        else:
            await interaction.response.send_message("Only owner can add admins", ephemeral=True)
            return

    if user.id in admin_users:
        if russian:
            await interaction.response.send_message("Уже есть в списке", ephemeral=True)
            return
        else:
            await interaction.response.send_message("Already in the list", ephemeral=True)
            return

    admin_users.append(user.id)
    save_users(admin_users, ADMIN_FILE)

    if russian:
        await interaction.response.send_message(f"<@{user.id}> добавлен в админы", ephemeral=False)
    else:
        await interaction.response.send_message(f"<@{user.id}> was added to admins", ephemeral=False)


@bot.tree.command(name="removeadmin", description="Remove admin")
async def removeadmin_command(interaction: discord.Interaction, user: discord.User):

    if not is_owner(interaction.user.id):
        if russian:
            await interaction.response.send_message("Только владелец может удалять админов", ephemeral=True) 
            return
        else:
            await interaction.response.send_message("Only owner can remove admins", ephemeral=True) 
            return
    if user.id not in admin_users:
        if russian:
            await interaction.response.send_message("Его нет в списке", ephemeral=True)
            return
        else:
            await interaction.response.send_message("He is not in the list", ephemeral=True)
            return

    admin_users.remove(user.id)
    save_users(admin_users, ADMIN_FILE)

    if russian:
        await interaction.response.send_message(f"<@{user.id}> удалён из админов", ephemeral=False)
    else:
        await interaction.response.send_message(f"<@{user.id}> is not admin anymore", ephemeral=False)


@bot.tree.command(name="listadmin", description="Show admnis list")
async def listadmin_command(interaction: discord.Interaction):

    if not is_allowed(interaction.user.id):
        if russian:
            await interaction.response.send_message("Нет доступа", ephemeral=True)
            return
        else:
            await interaction.response.send_message("Access denied", ephemeral=True)
            return

    if not admin_users:
        if russian:
            await interaction.response.send_message("Список админов пуст", ephemeral=True)
            return
        else:
            await interaction.response.send_message("Admin list is empty", ephemeral=True)
            return

    users = "\n".join([f"<@{uid}>" for uid in admin_users])

    if russian:
        await interaction.response.send_message(f"Администраторы:\n{users}", ephemeral=True)
    else:
        await interaction.response.send_message(f"Admins:\n{users}", ephemeral=True)


@bot.tree.command(name="help", description="Показать доступные команды")
async def help_command(interaction: discord.Interaction):

    if russian:
        if is_owner(interaction.user.id):

            help_msg = """
**Команды для всех пользователей:**
 - `/run [server_name]` - Запустить сервер
 - `/status` - Проверить статус сервера
 - `/list` - Показать разрешённых пользователей
 - `/listadmin` - Показать администраторов

**Команды для администраторов:**
 - `/stop` - Остановить сервер
 - `/add` - Добавить пользователя
 - `/remove` - Удалить пользователя

**Команды владельца:**
 - `/addadmin` - Добавить администратора
 - `/removeadmin` - Удалить администратора
 - Автор бота <@1014876512274620469>
"""

        elif is_admin(interaction.user.id):

            help_msg = """
**Команды для всех пользователей:**
 - `/run [server_name]` - Запустить сервер
 - `/status` - Проверить статус сервера
 - `/list` - Показать разрешённых пользователей
 - `/listadmin` - Показать администраторов

**Команды для администраторов:**
 - `/stop` - Остановить сервер
 - `/add` - Добавить пользователя
 - `/remove` - Удалить пользователя
 - Автор бота <@1014876512274620469>
"""

        elif is_allowed(interaction.user.id):

            help_msg = """
**Команды для пользователей:**
 - `/run [server_name]` - Запустить сервер
 - `/status` - Проверить статус сервера
 - `/list` - Показать разрешённых пользователей
 - `/listadmin` - Показать администраторов
 - Автор бота <@1014876512274620469>
"""

        else:
            help_msg = "Нет доступа"
    else:
        if is_owner(interaction.user.id):

            help_msg = """
**Commands for all users:**
 - `/run [server_name]` - Start a server
 - `/status` - Check server status
 - `/list` - Show allowed users
 - `/listadmin` - Show administrators

**Owner commands:**
 - `/stop` - Stop the server
 - `/add` - Add a user
 - `/remove` - Remove a user

**Owner-only commands:**
 - `/addadmin` - Add an administrator
 - `/removeadmin` - Remove an administrator
 - Bot author <@1014876512274620469>
"""

        elif is_admin(interaction.user.id):

            help_msg = """
**Commands for all users:**
 - `/run [server_name]` - Start a server
 - `/status` - Check server status
 - `/list` - Show allowed users
 - `/listadmin` - Show administrators

**Administrator commands:**
 - `/stop` - Stop the server
 - `/add` - Add a user
 - `/remove` - Remove a user
 - Bot author <@1014876512274620469>
"""

        elif is_allowed(interaction.user.id):

            help_msg = """
**User commands:**
 - `/run [server_name]` - Start a server
 - `/status` - Check server status
 - `/list` - Show allowed users
 - `/listadmin` - Show administrators
 - Bot author <@1014876512274620469>
"""
        else:
            help_msg = "Access denied"
    await interaction.response.send_message(help_msg, ephemeral=True)

bot.run(TOKEN)