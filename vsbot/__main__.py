import os


if not os.path.exists("volumes"):
    os.mkdir("volumes")


if __name__ == '__main__':
    import vsbot.bot
    vsbot.bot.run()
