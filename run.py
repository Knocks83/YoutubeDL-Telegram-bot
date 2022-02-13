from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackContext, Dispatcher
import config as cfg

import unicodedata
import re

import download
from requests import get
import os


workingDirectory = os.path.dirname(os.path.realpath(__file__))


# Brutally stolen from Django (https://github.com/django/django/blob/main/django/utils/text.py)
def slugify(value, allow_unicode=True):
    """
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize("NFKC", value)
    else:
        value = (
            unicodedata.normalize("NFKD", value)
            .encode("ascii", "ignore")
            .decode("ascii")
        )
    value = re.sub(r"[^\w\s-]", "", value.lower())
    return re.sub(r"[-\s]+", "-", value).strip("-_")


def sendVideo(update: Update, context: CallbackContext, args: list, destChatID=None):
    if destChatID is None:
        destChatID = update.message.chat_id
    
    if len(args) >= 1:
        for link in args:
            res = download.getDownloadLink(link)
            if res is not False:
                if 'title' in res:
                    # Open a file that's going to contain the download
                    filename = slugify(workingDirectory + '/' + res['title'])
                    f = open(filename + '.mp4', 'wb+')

                    downloadingMessage = update.message.reply_text(
                        'Downloading ' + link + '... 0%', disable_web_page_preview=True)
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
                                          (downloaded_bytes/total_size_in_bytes*100)) # %% is the percent sign
                            if downloadingMessage.text != text:
                                try:
                                    downloadingMessage.edit_text(text, disable_web_page_preview=True)
                                except:
                                    pass

                            f.write(data)  # Write to file

                    except Exception as e:
                        # Send the error and delete the file
                        downloadingMessage.edit_text(
                            "Error while downloading! " + str(e))
                        f.close()
                        os.remove(filename)
                        return

                    downloadingMessage.delete()

                    # Set the pointer back to the start of the file
                    f.seek(0, os.SEEK_SET)

                    # Send the uploading message
                    uploadingMessage = update.message.reply_text(
                        'Uploading ' + link + '...', disable_web_page_preview=True)

                    # Create the button
                    buttons = InlineKeyboardMarkup([[InlineKeyboardButton("Link", link)]])

                    if 'thumbnail' in res:
                        # Download the thumb
                        thumbFile = open(filename+'.jpg', 'wb+')
                        thumbFile.write(get(res['thumbnail']).content)
                        thumbFile.seek(0, os.SEEK_SET)
                        
                        # Send the video
                        context.bot.send_video(chat_id=destChatID, video=f, thumb=thumbFile, caption=res['title'], reply_markup=buttons, supports_streaming=True)
                        thumbFile.close()
                        os.remove(filename+'.jpg')
                    else:
                        context.bot.send_video(chat_id=destChatID, video=f, caption=res['title'], reply_markup=buttons, supports_streaming=True)

                    uploadingMessage.delete()
                    # Delete the temp file
                    f.close()
                    os.remove(filename + '.mp4')
            else:
                update.message.reply_text('Error with Youtube DL!')


def download_handler(update: Update, context: CallbackContext):
    sendVideo(update, context, context.args)

def cdownload_handler(update: Update, context: CallbackContext):
    sendVideo(update, context, context.args, destChatID=cfg.chatID)

def help(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Commands:\n- /download: Download the media and send it in this chat\n- /cdownload: Download the media and send it to the chat whose ID is in the file')


updater = Updater(token=cfg.botToken, base_url=cfg.endpoint)
updater.dispatcher.add_handler(CommandHandler('start', help))
updater.dispatcher.add_handler(CommandHandler('help', help))
updater.dispatcher.add_handler(CommandHandler('download', download_handler))
updater.dispatcher.add_handler(CommandHandler('cdownload', cdownload_handler))

updater.start_polling()
updater.idle()
