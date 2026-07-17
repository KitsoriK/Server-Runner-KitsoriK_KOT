from asyncio.windows_events import NULL
from math import e
import discord
from discord.ext import commands
from discord.ext import tasks
import subprocess
import json
import os
from mcrcon import MCRcon

ALLOWED_USERS_FILE = "allowed_users.json"
ADMIN_USERS_FILE = "admin_users.json"

ALLOWED_ROLES_FILE = "allowed_roles.json"
ADMIN_ROLES_FILE = "admin_roles.json"

CONFIG_FILE = "config_file.json"

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

def config():
    if not os.path.exists(CONFIG_FILE):
        None
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
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
stopping_admin_feature = settings["stopping_admin_feature"]
russian = settings["russian"]

channel_check_id = settings["channel_check_id"]
channel_run_id = settings["channel_run_id"]
channel_stop_id = settings["channel_stop_id"]
channel_start = settings["start_message"]
channel_start_cfg = settings["channel_start"]
last_server_check = None

def load_users(file):
    if not os.path.exists(file):
        return []
    with open(file, "r") as f:
        return json.load(f)

def save_users(users, file):
    with open(file, "w") as f:
        json.dump(users, f)

allowed_users = load_users(ALLOWED_USERS_FILE)
admin_users = load_users(ADMIN_USERS_FILE)

allowed_roles = load_users(ALLOWED_ROLES_FILE)
admin_roles = load_users(ADMIN_ROLES_FILE)

def is_owner(user_id):
    return user_id == OWNER_ID

def is_admin(user_id, user_roles):
    return (user_id in admin_users or any(role.id in admin_roles for role in user_roles) or is_owner(user_id))

def is_allowed(user_id, user_roles):
    return (user_id in allowed_users or any(role.id in allowed_roles for role in user_roles) or is_admin(user_id, user_roles))

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

    await start_message()

    if not check_message.is_running():
        check_message.start()

    print(f"Bot started like {bot.user}")

async def start_message():
    channel = bot.get_channel(channel_start)
    if channel:
        await channel.send(channel_start_cfg)

@tasks.loop(seconds=60)
async def check_message():
    global last_server_check
    
    channel = bot.get_channel(channel_check_id)

    if channel:
        if russian:
            if is_any_server_running():
                if last_server_check == False or last_server_check == None:
                    await channel.send("🟢 Какой-то сервер работает")
                    last_server_check = True
            else:
                if last_server_check == True or last_server_check == None:
                    await channel.send("🔴 Не один сервер не активен")
                    last_server_check = False
        else:
            if is_any_server_running():
                if last_server_check == False or last_server_check == None:
                    await channel.send("🟢 Some server is running")
                    last_server_check = True
            else:
                if last_server_check == True or last_server_check == None:
                    await channel.send("🔴 There is no active servers")
                    last_server_check = False
                    
        if last_server_check:
            print("server is active")
        else:
            print("server isn't active")

    else:  
        print("channel dont exist")

@bot.tree.command(name="run", description="Start a server")
async def run(interaction: discord.Interaction, server_name: str = ""):

    user_id = interaction.user.id

    if not is_allowed(interaction.user.id, interaction.user.roles):
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
            await interaction.response.send_message(f"❌ Неизвестный сервер `{server_name}`", ephemeral=True)
            return
        else:
            await interaction.response.send_message(f"❌ Unknown server `{server_name}`", ephemeral=True)
            return

    if is_any_server_running():
        if russian:
            await interaction.response.send_message("❌ Уже запущен этот или другой сервер", ephemeral=True)
            return
        else:
            await interaction.response.send_message("❌ Some server is already running", ephemeral=True)
            return

    try:
        subprocess.Popen(
            f'cmd /c "{bat_file}"',
            cwd=os.path.dirname(bat_file),
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        channel = bot.get_channel(channel_run_id)
        if russian:
            if server_name:
                if channel:
                    await channel.send(f"🟢 <@{user_id}> Запустил '{server_name}'")
                    await interaction.response.send_message(f"🟢 <@{user_id}> Запустил '{server_name}'", ephemeral=True)
                else:
                    await interaction.response.send_message(f"🟢 <@{user_id}> Запустил '{server_name}`", ephemeral=False)
            else:
                if channel:
                    await channel.send(f"🟢 <@{user_id}> Запустил '{standard_server}'")
                    await interaction.response.send_message(f"🟢 <@{user_id}> Запустил '{standard_server}'", ephemeral=True)
                else:
                    await interaction.response.send_message(f"🟢 <@{user_id}> Запустил '{standard_server}'", ephemeral=False)
        else:
            if server_name:
                if channel:
                    await channel.send(f"🟢 <@{user_id}> has started '{server_name}'")
                    await interaction.response.send_message(f"🟢 <@{user_id}> has started '{server_name}'", ephemeral=True)
                else:
                    await interaction.response.send_message(f"🟢 <@{user_id}> has started '{server_name}'", ephemeral=False)
            else:
                if channel:
                    await channel.send(f"🟢 <@{user_id}> has started '{standard_server}'")
                    await interaction.response.send_message(f"🟢 <@{user_id}> has started '{standard_server}'", ephemeral=True)
                else:
                    await interaction.response.send_message(f"🟢 <@{user_id}> has started '{standard_server}'", ephemeral=False)

    except Exception as e:
        if russian:
            await interaction.response.send_message(f"Ошибка запуска: {e}", ephemeral=True)
        else:
            await interaction.response.send_message(f"Starting error: {e}", ephemeral=True)

@bot.tree.command(name="status", description="Check server status")
async def status_command(interaction: discord.Interaction):
    if russian:
        if is_any_server_running():
            await interaction.response.send_message("🟢 Какой-то сервер работает", ephemeral=True)
        else:
            await interaction.response.send_message("🔴 Не один сервер не активен", ephemeral=True)
    else:
        if is_any_server_running():
            await interaction.response.send_message("🟢 Some server is running", ephemeral=True)
        else:
            await interaction.response.send_message("🔴 There is no active servers", ephemeral=True)


@bot.tree.command(name="stop", description="Stop a server")
async def stop_command(interaction: discord.Interaction):

    user_id = interaction.user.id

    if stopping_admin_feature:
        if not is_admin(interaction.user.id, interaction.user.roles):
            if russian:
                await interaction.response.send_message("Только админ может останавливать", ephemeral=True)
                return
            else:
                await interaction.response.send_message("Only admin can stop", ephemeral=True)
                return
    else:
        if not is_allowed(interaction.user.id, interaction.user.roles):
            if russian:
                await interaction.response.send_message("Нет доступа", ephemeral=True)
                return
            else:
                await interaction.response.send_message("Access denied", ephemeral=True)
                return
    
    if is_any_server_running:
        try:
            with MCRcon(RCON_HOST, RCON_PASSWORD, port=RCON_PORT) as mcr:
                mcr.command("stop")

            channel = bot.get_channel(channel_stop_id)
            if russian:
                if channel:
                    await channel.send(f"❌ <@{user_id}> Остановил сервер!!!")
                    await interaction.response.send_message(f"❌ <@{user_id}> Остановил сервер!!!", ephemeral=True)
                else:
                    await interaction.response.send_message(f"❌ <@{user_id}> Остановил сервер!!!", ephemeral=False)
            else:
                if channel:
                    await channel.send(f"❌ <@{user_id}> Stopped the server!!!")
                    await interaction.response.send_message(f"❌ <@{user_id}> Stopped the server!!!", ephemeral=True)
                else:
                    await interaction.response.send_message(f"❌ <@{user_id}> Stopped the server!!!", ephemeral=False)
    
        except Exception as e:
            if russian:
                await interaction.response.send_message(f"Ошибка запуска: {e}", ephemeral=True)
            else:
                await interaction.response.send_message(f"Starting error: {e}", ephemeral=True)
                
    else:
        if russian:
            await interaction.response.send_message("🔴 Не один сервер не активен", ephemeral=True)
            return
        else:
            await interaction.response.send_message("🔴 There is no active servers", ephemeral=True)
            return



@bot.tree.command(name="add", description="Add user")
async def add_command(interaction: discord.Interaction, user: discord.User | None = None, role: discord.Role | None = None):

    if not is_admin(interaction.user.id, interaction.user.roles):
        if russian:
            await interaction.response.send_message("Только админ может добавлять", ephemeral=True)
            return
        else:
            await interaction.response.send_message("Only admin can add", ephemeral=True)
            return
    
    if user is None and role is None:
        if russian:
            await interaction.response.send_message("Выберите пользователя или роль",ephemeral=True)
            return
        else:
            await interaction.response.send_message("Choose a user or a role.",ephemeral=True)
            return

    if user is not None:
        if user.id in allowed_users:
            if russian:
                await interaction.response.send_message("Уже есть в списке", ephemeral=True)
                return
            else:
                await interaction.response.send_message("Already in the list", ephemeral=True)
                return
            
        allowed_users.append(user.id)
        save_users(allowed_users, ALLOWED_USERS_FILE)
        if russian:
            await interaction.response.send_message(f"Пользователь <@{user.id}> добавлен", ephemeral=False)
        else:
            await interaction.response.send_message(f"User <@{user.id}> added", ephemeral=False)
    
    if role is not None:
        if role.id in allowed_roles:
            if russian:
                await interaction.response.send_message("Уже есть в списке", ephemeral=True)
                return
            else:
                await interaction.response.send_message("Already in the list", ephemeral=True)
                return
            
        allowed_roles.append(role.id)
        save_users(allowed_roles, ALLOWED_ROLES_FILE)
        if russian:
            await interaction.response.send_message(f"Роль <@&{role.id}> добавлена", ephemeral=False)
        else:
            await interaction.response.send_message(f"Role <@&{role.id}> added", ephemeral=False)



@bot.tree.command(name="remove", description="Remove user")
async def remove_command(interaction: discord.Interaction, user: discord.User | None = None, role: discord.Role | None = None):

    if not is_admin(interaction.user.id, interaction.user.roles):
        if russian:
            await interaction.response.send_message("Только админ может удалять", ephemeral=True)
            return
        else:
            await interaction.response.send_message("Only admin can remove", ephemeral=True)
            return

    if user is None and role is None:
        if russian:
            await interaction.response.send_message("Выберите пользователя или роль",ephemeral=True)
            return
        else:
            await interaction.response.send_message("Choose a user or a role.",ephemeral=True)
            return

    if user is not None:
        if user.id not in allowed_users:
            if russian:
                await interaction.response.send_message("Его нет в списке", ephemeral=True)
                return
            else:
                await interaction.response.send_message("Not in the list", ephemeral=True)
                return

        allowed_users.remove(user.id)
        save_users(allowed_users, ALLOWED_USERS_FILE)
        if russian:
            await interaction.response.send_message(f"Пользователь <@{user.id}> удалён", ephemeral=False)
        else:
            await interaction.response.send_message(f"User <@{user.id}> removed", ephemeral=False)

    if role is not None:
        if role.id not in allowed_roles:
            if russian:
                await interaction.response.send_message("Её нет в списке", ephemeral=True)
                return
            else:
                await interaction.response.send_message("Not in the list", ephemeral=True)
                return

        allowed_roles.remove(role.id)
        save_users(allowed_roles, ALLOWED_ROLES_FILE)
        if russian:
            await interaction.response.send_message(f"Роль <@&{role.id}> удалена", ephemeral=False)
        else:
            await interaction.response.send_message(f"Role <@&{role.id}> removed", ephemeral=False)


@bot.tree.command(name="list", description="Show allowed users and roles")
async def list_command(interaction: discord.Interaction):

    if not is_allowed(interaction.user.id, interaction.user.roles):
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
    roles = "\n".join([f"<@&{uid}>" for uid in allowed_roles])

    if russian:
        await interaction.response.send_message(f"Разрешённые:\n{users}\n{roles}", ephemeral=True)
    else:
        await interaction.response.send_message(f"Allowed:\n{users}\n{roles}", ephemeral=True)

@bot.tree.command(name="addadmin", description="Add admin")
async def addadmin_command(interaction: discord.Interaction, user: discord.User | None = None, role: discord.Role | None = None):

    if not is_owner(interaction.user.id):
        if russian:
            await interaction.response.send_message("Только владелец может добавлять админов", ephemeral=True)
            return
        else:
            await interaction.response.send_message("Only owner can add admins", ephemeral=True)
            return

    if user is None and role is None:
        if russian:
            await interaction.response.send_message("Выберите пользователя или роль",ephemeral=True)
            return
        else:
            await interaction.response.send_message("Choose a user or a role.",ephemeral=True)
            return

    if user is not None:
        if user.id in admin_users:
            if russian:
                await interaction.response.send_message("Уже есть в списке", ephemeral=True)
                return
            else:
                await interaction.response.send_message("Already in the list", ephemeral=True)
                return

        admin_users.append(user.id)
        save_users(admin_users, ADMIN_USERS_FILE)
        if russian:
            await interaction.response.send_message(f"Пользователь <@{user.id}> добавлен в админы", ephemeral=False)
        else:
            await interaction.response.send_message(f"User <@{user.id}> was added to admins", ephemeral=False)

    if role is not None:
        if role.id in admin_roles:
            if russian:
                await interaction.response.send_message("Уже есть в списке", ephemeral=True)
                return
            else:
                await interaction.response.send_message("Already in the list", ephemeral=True)
                return

        admin_roles.append(role.id)
        save_users(admin_roles, ADMIN_ROLES_FILE)
        if russian:
            await interaction.response.send_message(f"Роль <@&{role.id}> добавлена в админы", ephemeral=False)
        else:
            await interaction.response.send_message(f"Role <@&{role.id}> was added to admins", ephemeral=False)


@bot.tree.command(name="removeadmin", description="Remove admin")
async def removeadmin_command(interaction: discord.Interaction, user: discord.User | None = None, role: discord.Role | None = None):

    if not is_owner(interaction.user.id):
        if russian:
            await interaction.response.send_message("Только владелец может удалять админов", ephemeral=True) 
            return
        else:
            await interaction.response.send_message("Only owner can remove admins", ephemeral=True) 
            return
        
    if user is None and role is None:
        if russian:
            await interaction.response.send_message("Выберите пользователя или роль",ephemeral=True)
            return
        else:
            await interaction.response.send_message("Choose a user or a role.",ephemeral=True)
            return

    if user is not None:
        if user.id not in admin_users:
            if russian:
                await interaction.response.send_message("Его нет в списке", ephemeral=True)
                return
            else:
                await interaction.response.send_message("He is not in the list", ephemeral=True)
                return

        admin_users.remove(user.id)
        save_users(admin_users, ADMIN_USERS_FILE)
        if russian:
            await interaction.response.send_message(f"Пользователь <@{user.id}> удалён из админов", ephemeral=False)
        else:
            await interaction.response.send_message(f"User <@{user.id}> is not admin anymore", ephemeral=False)

    if role is not None:
        if role.id not in admin_roles:
            if russian:
                await interaction.response.send_message("Его нет в списке", ephemeral=True)
                return
            else:
                await interaction.response.send_message("He is not in the list", ephemeral=True)
                return

        admin_roles.remove(role.id)
        save_users(admin_roles, ADMIN_ROLES_FILE)
        if russian:
            await interaction.response.send_message(f"Роль <@&{role.id}> удалёна из админов", ephemeral=False)
        else:
            await interaction.response.send_message(f"Role <@&{role.id}> is not admin anymore", ephemeral=False)


@bot.tree.command(name="listadmin", description="Show admnis list")
async def listadmin_command(interaction: discord.Interaction):

    if not is_allowed(interaction.user.id, interaction.user.roles):
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
    roles = "\n".join([f"<@&{uid}>" for uid in admin_roles])

    if russian:
        await interaction.response.send_message(f"Администраторы:\n{users}\n{roles}", ephemeral=True)
    else:
        await interaction.response.send_message(f"Admins:\n{users}\n{roles}", ephemeral=True)


@bot.tree.command(name="help", description="Показать доступные команды")
async def help_command(interaction: discord.Interaction):

    if russian:
        if is_owner(interaction.user.id):

            help_message = """
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

        elif is_admin(interaction.user.id, interaction.user.roles):

            help_message = """
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

        elif is_allowed(interaction.user.id, interaction.user.roles):

            help_message = """
**Команды для пользователей:**
 - `/run [server_name]` - Запустить сервер
 - `/status` - Проверить статус сервера
 - `/list` - Показать разрешённых пользователей
 - `/listadmin` - Показать администраторов
 - Автор бота <@1014876512274620469>
"""

        else:
            help_message = "Нет доступа"
    else:
        if is_owner(interaction.user.id):

            help_message = """
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

        elif is_admin(interaction.user.id, interaction.user.roles):

            help_message = """
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

        elif is_allowed(interaction.user.id, interaction.user.roles):

            help_message = """
**User commands:**
 - `/run [server_name]` - Start a server
 - `/status` - Check server status
 - `/list` - Show allowed users
 - `/listadmin` - Show administrators
 - Bot author <@1014876512274620469>
"""
        else:
            help_message = "Access denied"
    await interaction.response.send_message(help_message, ephemeral=True)

bot.run(TOKEN)