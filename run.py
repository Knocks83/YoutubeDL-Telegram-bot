import botogram
from requests import get, post, head
import os
from random import randint
import json
import download
import config as cfg

botToken = "1614607267:AAGnzUBwEGmSCgxgd-aJmPd24sc8sTHp7Es"
chatID = -1001338642998

workingDirectory = os.path.dirname(os.path.realpath(__file__))

# END CONFIGURATION

bot = botogram.Bot(botogram.api.TelegramAPI(
    api_key=cfg.botToken, endpoint=cfg.endpoint))


@bot.command("start")
def hello_command(chat, message, args):
    """Say hello to the world!"""
    chat.send("Commands:\n- /download: Download the media and send it in this chat\n- /cdownload: Download the media and send it to the chat whose ID is in the file\n- /batchdownload: Download a list of media and send it to this chat\n- /cbatchdownload Download a list of media and send it to the chat whose ID is in the file")


@bot.command("download")
def download_command(chat, message, args):
    sendVideo(bot, botogram, chat, message, args, chat.id)


@bot.command("cdownload")
def cdownload_command(chat, message, args):
    sendVideo(bot, botogram, chat, message, args, cfg.chatID)


@bot.command("batchdownload")
def batchdownload_command(chat, message, args):
    batchSend(bot, botogram, chat, args, chat.id)


@bot.command("cbatchdownload")
def cbatchdownload_command(chat, message, args):
    batchSend(bot, botogram, chat, args, cfg.chatID)


def sendVideo(bot, botogram, chat, message, args, destChatID):
    """Download the video and upload it to the chat"""
    if len(args) == 1:
        res = download.getDownloadLink(args[0])
        if res is not False:
            if 'title' in res:
                # Open a file that's going to contain the download
                filename = workingDirectory + \
                    "/youtubedlbot" + str(randint(0, 1000000))
                f = open(filename, 'wb+')

                downloadingMessage = message.reply('Downloading... 0%')
                try:
                    # Download the URL provided by Youtube_DL
                    video = get(res['url'], stream=True)

                    # Get the size of the file, plus set a variable that'll contain how much has already been downloaded in bytes
                    total_size_in_bytes = int(
                        video.headers.get('content-length', 0))
                    downloaded_bytes = 0

                    # Every 10 megabytes
                    for data in video.iter_content(1024*1024*10):
                        # Increase the downloaded bytes counter
                        downloaded_bytes += len(data)
                        text = format('Downloading... %.0f%%' %
                                      (downloaded_bytes/total_size_in_bytes*100))
                        if downloadingMessage.text != text:
                            # %% is the percent sign
                            downloadingMessage.edit(text)

                        f.write(data)  # Write to file

                except Exception as e:
                    # Send the error and delete the file
                    downloadingMessage.edit(
                        "Error while downloading! " + str(e))
                    f.close()
                    os.remove(filename)
                    return

                chat.delete_message(downloadingMessage)

                # Set the pointer back to the start of the file
                f.seek(0, os.SEEK_SET)
                # Send the uploading message
                uploadingMessage = message.reply('Uploading...')

                # Create the button
                buttons = botogram.Buttons()
                buttons[0].url("Link", args[0])

                # Send the video
                bot.chat(destChatID).send_video(path=filename,
                                                caption=res['title'], attach=buttons)

                chat.delete_message(uploadingMessage)
                # Delete the temp file
                f.close()
                os.remove(filename)
        else:
            chat.send('Error with Youtube DL!')


def batchSend(bot, botogram, chat, args, destChatID):
    if len(args) >= 1:
        for link in args:
            res = download.getDownloadLink(link)
            if res is not False:
                if 'title' in res:
                    # Open a file that's going to contain the download
                    filename = workingDirectory + \
                        "/youtubedlbot" + str(randint(0, 1000000))
                    f = open(filename, 'wb+')

                    downloadingMessage = chat.send(
                        'Downloading ' + link + '... 0%', preview=False)
                    try:
                        # Download the URL provided by Youtube_DL
                        video = get(res['url'], stream=True)

                        # Get the size of the file, plus set a variable that'll contain how much has already been downloaded in bytes
                        total_size_in_bytes = int(
                            video.headers.get('content-length', 0))
                        downloaded_bytes = 0

                        # Every 10 megabytes
                        for data in video.iter_content(1024*1024*10):
                            # Increase the downloaded bytes counter
                            downloaded_bytes += len(data)
                            text = format('Downloading ' + link + '... %.0f%%' %
                                          (downloaded_bytes/total_size_in_bytes*100))
                            if downloadingMessage.text != text:
                                # %% is the percent sign
                                downloadingMessage.edit(text)

                            f.write(data)  # Write to file

                    except Exception as e:
                        # Send the error and delete the file
                        downloadingMessage.edit(
                            "Error while downloading! " + str(e))
                        f.close()
                        os.remove(filename)
                        return

                    chat.delete_message(downloadingMessage)

                    # Set the pointer back to the start of the file
                    f.seek(0, os.SEEK_SET)
                    # Send the uploading message
                    uploadingMessage = chat.send(
                        'Uploading ' + link + '...', preview=False)
                    # Create the button
                    buttons = botogram.Buttons()
                    buttons[0].url("Link", link)

                    # Send the video
                    bot.chat(destChatID).send_video(path=filename,
                                                    caption=res['title'], attach=buttons)

                    chat.delete_message(uploadingMessage)
                    # Delete the temp file
                    f.close()
                    os.remove(filename)
            else:
                chat.send('Error with Youtube DL!')


if __name__ == "__main__":
    bot.run()
