from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackContext
from telegram.error import RetryAfter
import config as cfg
from time import sleep

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


def sendLink(video, link, filename, update, context, destChatID):
    if 'title' in video:
        downloadingMessage = update.message.reply_text(
            'Downloading ' + link + '...', disable_web_page_preview=True)
        
        # Download the file via youtube-dl
        try:
            download.download(link, filename+'.mp4')
        except Exception as e:
            print(e)
            downloadingMessage.edit_text('Error while downloading ' + link + ' - ' + str(e))
            try:
                os.remove(filename+'.mp4')
            except:
                pass
            
            return

        downloadingMessage.delete()

        if not os.stat(filename + '.mp4'):
            update.message.reply_text('Error while downloading ' + link)
            return

        # Open the file to upload it
        f = open(filename + '.mp4', 'rb')

        # Send the uploading message
        uploadingMessage = update.message.reply_text(
            'Uploading ' + link + '...', disable_web_page_preview=True)

        # Create the button
        buttons = InlineKeyboardMarkup([[InlineKeyboardButton("Link", link)]])

        if 'thumbnail' in video:
            # Download the thumb
            thumbFile = open(filename+'.jpg', 'wb+')
            thumbFile.write(get(video['thumbnail']).content)
            thumbFile.seek(0, os.SEEK_SET)
            
            # Send the video
            context.bot.send_video(chat_id=destChatID, video=f, caption=video['title'], reply_markup=buttons, supports_streaming=True, width=video['width'], height=video['height'], thumb=thumbFile, write_timeout=60)
            thumbFile.close()
            os.remove(filename+'.jpg')
        else:
            context.bot.send_video(chat_id=destChatID, video=f, caption=video['title'], reply_markup=buttons, supports_streaming=True, width=video['width'], height=video['height'], write_timeout=60)

        uploadingMessage.delete()
        # Delete the temp file
        f.close()
        os.remove(filename + '.mp4')


def sendVideo(update: Update, context: CallbackContext, args: list, destChatID=None):
    if destChatID is None:
        destChatID = update.message.chat_id
    
    if len(args) >= 1:
        for link in args:
            res = download.getDownloadLink(link)
            if res is not False:
                filename = workingDirectory + '/' + slugify(res['title'])

                try:
                    sendLink(res, link, filename, update, context, destChatID)
                except RetryAfter as e:
                    sleep(e.retry_after + 1)

                
                # Retry removing the files, in case the function got an error
                try:
                    os.remove(filename + '.jpg')
                except Exception:
                    pass

                try:
                    os.remove(filename + '.mp4')
                except Exception:
                    pass
                    
            else:
                update.message.reply_text('Error with Youtube DL!')

def downloadChannel(update: Update, context: CallbackContext, args: list, destChatID=None):
    if destChatID is None:
        destChatID = update.message.chat_id
    
    if len(args) >= 1:
        for channel in args:
            crawlingMessage = update.message.reply_text(
                            'Crawling the videos...')
            videos = download.getChannelVideos(channel)
            crawlingMessage.delete()

            if videos is not False:
                for video in videos:
                    link = video['webpage_url']
                    filename = workingDirectory + '/' + slugify(video['title'])

                    try:
                        sendLink(video, link, filename, update, context, destChatID)
                    except RetryAfter as e:
                        sleep(e.retry_after + 1)

                    
                    # Retry removing the files, in case the function got an error
                    try:
                        os.remove(filename + '.jpg')
                    except Exception:
                        pass

                    try:
                        os.remove(filename + '.mp4')
                    except Exception:
                        pass
                    
            else:
                update.message.reply_text('Error with Youtube DL!')


def download_handler(update: Update, context: CallbackContext):
    sendVideo(update, context, context.args)

def cdownload_handler(update: Update, context: CallbackContext):
    sendVideo(update, context, context.args, destChatID=cfg.chatID)

def channel_handler(update: Update, context: CallbackContext):
    downloadChannel(update, context, context.args)

def cchannel_handler(update: Update, context: CallbackContext):
    downloadChannel(update, context, context.args, destChatID=cfg.chatID)

def help(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Commands:\n- /download: Download the media and send it in this chat\n- /cdownload: Download the media and send it to the chat whose ID is in the config file\n-/channel: Download all the media of a channel and send it in this chat\n-/cchannel: Download all the media of a channel and send it to the chat whose ID is in the config file')


updater = Updater(token=cfg.botToken, base_url=cfg.endpoint)
updater.dispatcher.add_handler(CommandHandler('start', help))
updater.dispatcher.add_handler(CommandHandler('help', help))
updater.dispatcher.add_handler(CommandHandler('download', download_handler))
updater.dispatcher.add_handler(CommandHandler('cdownload', cdownload_handler))
updater.dispatcher.add_handler(CommandHandler('channel', channel_handler))
updater.dispatcher.add_handler(CommandHandler('cchannel', cchannel_handler))

updater.start_polling()
updater.idle()
