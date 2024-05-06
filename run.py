from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackContext, Application
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


async def sendLink(video, link, filename, update, context, destChatID):
    if 'title' in video:
        downloadingMessage = await update.message.reply_text('Downloading ' + link + '...', disable_web_page_preview=True)
        
        # Download the file via youtube-dl
        try:
            download.download(link, filename+'.mp4')
        except Exception as e:
            print(e)
            await downloadingMessage.edit_text('Error while downloading ' + link + ' - ' + str(e))
            try:
                os.remove(filename+'.mp4')
            except:
                pass
            
            return

        await downloadingMessage.delete()

        if not os.stat(filename + '.mp4'):
            await update.message.reply_text('Error while downloading ' + link)
            return

        # Open the file to upload it
        f = open(filename + '.mp4', 'rb')

        # Send the uploading message
        uploadingMessage = await update.message.reply_text('Uploading ' + link + '...', disable_web_page_preview=True)

        # Create the button
        buttons = InlineKeyboardMarkup([[InlineKeyboardButton("Link", link)]])

        if 'thumbnail' in video:
            # Download the thumb
            thumbFile = open(filename+'.jpg', 'wb+')
            thumbFile.write(get(video['thumbnail']).content)
            thumbFile.seek(0, os.SEEK_SET)
            
            # Send the video
            await context.bot.send_video(chat_id=destChatID, video=f, caption=video['title'], reply_markup=buttons, supports_streaming=True, width=video['width'], height=video['height'], thumbnail=thumbFile)
            thumbFile.close()
            os.remove(filename+'.jpg')
        else:
            await context.bot.send_video(chat_id=destChatID, video=f, caption=video['title'], reply_markup=buttons, supports_streaming=True, width=video['width'], height=video['height'])

        await uploadingMessage.edit_text('Upload complete! ✅')

        # Delete the temp file
        f.close()
        os.remove(filename + '.mp4')


async def sendVideo(update: Update, context: CallbackContext, args: list, destChatID=None):
    if destChatID is None:
        destChatID = update.message.chat_id
    
    if len(args) >= 1:
        for link in args:
            res = download.getDownloadLink(link)
            if res is not False:
                filename = workingDirectory + '/' + slugify(res['title'])

                try:
                    await sendLink(res, link, filename, update, context, destChatID)
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
                await update.message.reply_text('Error with Youtube DL!')

async def downloadChannel(update: Update, context: CallbackContext, args: list, destChatID=None):
    if destChatID is None:
        destChatID = update.message.chat_id
    
    if len(args) >= 1:
        for channel in args:
            crawlingMessage = await update.message.reply_text('Crawling the videos...')
            videos = download.getChannelVideos(channel)
            crawlingMessage.delete()

            if videos is not False:
                for video in videos:
                    link = video['webpage_url']
                    filename = workingDirectory + '/' + slugify(video['title'])

                    try:
                        await sendLink(video, link, filename, update, context, destChatID)
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
                await update.message.reply_text('Error with Youtube DL!')


async def download_handler(update: Update, context: CallbackContext):
    await sendVideo(update, context, context.args)

async def cdownload_handler(update: Update, context: CallbackContext):
    await sendVideo(update, context, context.args, destChatID=cfg.chatID)

async def channel_handler(update: Update, context: CallbackContext):
    await downloadChannel(update, context, context.args)

async def cchannel_handler(update: Update, context: CallbackContext):
    await downloadChannel(update, context, context.args, destChatID=cfg.chatID)

async def help(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('Commands:\n- /download: Download the media and send it in this chat\n- /cdownload: Download the media and send it to the chat whose ID is in the config file\n-/channel: Download all the media of a channel and send it in this chat\n-/cchannel: Download all the media of a channel and send it to the chat whose ID is in the config file')


application = (
    Application.builder()
    .base_url(cfg.endpoint)
    .token(cfg.botToken)
    .write_timeout(60)
    .build()
)

application.add_handler(CommandHandler('start', help))
application.add_handler(CommandHandler('help', help))
application.add_handler(CommandHandler('download', download_handler))
application.add_handler(CommandHandler('cdownload', cdownload_handler))
application.add_handler(CommandHandler('channel', channel_handler))
application.add_handler(CommandHandler('cchannel', cchannel_handler))

application.run_polling()
