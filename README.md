So how to set up my bot

1. Create a Discord Bot
Go to the Discord Developer Portal.
Create a new application.
Open the Bot tab and create a bot.
Copy your bot token (click Reset Token if needed).
Open OAuth2 - URL Generator.
Select the following scopes:
bot
applications.commands
Choose the permissions your bot needs.
Copy the generated invite link and use it to add the bot to your server.
2. Prepare Your Minecraft Servers
Place all of your server folders inside a single directory.
Example:

    C:\servers\
├── Server1\
│   └── Start.bat

    ├── Server2\
│   └── Start.bat

    └── Server3\
    └── Start.bat

    For every server:

    Rename the startup script to Start.bat (if it isn't already).

    Open server.properties and configure RCON:
    enable-rcon=true
    rcon.password=your_password
    rcon.port=25575
    It is recommended to keep the RCON port at 25575 unless you have a reason to change it.

3. Configure the Bot
    Open config_file.json and edit the following values:
    TOKEN - Your Discord bot token.
    You can get it from the Bot page in the Discord Developer Portal.

    OWNER_ID - Your Discord user ID.
    Enable Developer Mode in Discord, click your profile, and choose Copy User ID.

    RCON_HOST - Usually 127.0.0.1
    RCON_PORT - Your RCON port (usually 25575).
    RCON_PASSWORD - The same password you set in server.properties.

    server_path - The folder containing all of your Minecraft servers.
    Example:"server_path": "C:/servers" WARNING: dont use \ intead use / 

    standard_server - The server that starts when you use /run without specifying a server name.
    Leave this empty if you don't want a default server.

    if you want the bot to say every N minutes is server running set chanel_cycle - true. 
    chanel_id - on chanel id where you want the bot to send message. 
    To get the id enable Developer Mode in Discord, right-click chanel, and choose Copy Chanel ID.
    chanel_timer set on number of minutes between messages


    russian - true - Bot messages will be in Russian. false - Bot messages will be in English.

4. Start the Bot
    Run the bot.

    Once it's online, use /help to see all available commands and how to use them.

    Enjoy!
 
   
