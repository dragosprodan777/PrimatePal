# Primate Pal Bot

Welcome to Primate Pal Bot, your friendly Discord bot designed to bring fun and utility to your server. Primate Pal Bot is built with modularity in mind, using Discord.py cogs to organize and manage various bot functionalities. This README will introduce you to the bot's features and explain how the use of cogs makes it easy to extend and customize.

## Introduction

Primate Pal Bot is a versatile Discord bot that offers a range of commands and features for your server. Whether you want to greet users, play text-to-speech messages, or simply manage voice channels, this bot has you covered.

## Summary of Features

- **Greet and Socialize:** Primate Pal Bot includes friendly greeting commands to make your server feel welcoming. Say hello, hi, or engage in conversations with your bot.
- **Text-to-Speech (TTS):** Enjoy text-to-speech functionality to have the bot speak any text you provide in voice channels. The language can be changed via specific module.
- **Voice Channel Management:** Easily move the bot in and out of voice channels using the leave command.

## Modularity with Cogs

One of the standout features of Primate Pal Bot is its use of cogs to organize and manage different functionalities. Here's how it works:

- Each bot feature or command is implemented as a separate cog.
- Cogs are stored in separate Python files within folders inside the `modules` directory.
- The bot automatically detects and loads new cogs from these folders, making it easy to add, remove, or customize specific features.

## Getting Started

To get started with Primate Pal Bot, follow these steps:

1. Clone or download this repository to your local machine.
2. Install the required dependencies listed in `requirements.txt` using `pip install -r requirements.txt`.
3. Set up your Discord bot and obtain a bot token.
4. Save your bot token locally in the OS and add your bot token as follows:

    ```
    BOT_TOKEN=your_bot_token_here
    ```

5. Run the bot using the `main.py` script. You can run it from the terminal using the following command:

    ```
    python3 main.py
    ```

   Alternatively, you can create a run configuration in your development environment.

## Adding Custom Cogs

You can extend Primate Pal Bot by adding custom cogs for additional functionality. Here's how to do it:

1. Create a new folder inside the `modules` directory, e.g., `your_new_feature`.
2. Within the new folder, add a `cog.py` file where you implement your custom commands and features.
3. The bot will automatically detect and load the new cog, making your custom commands available.

## Contributing

Contributions to Primate Pal Bot are welcome! If you have ideas for new features, improvements, or bug fixes, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE.md) file for details.
