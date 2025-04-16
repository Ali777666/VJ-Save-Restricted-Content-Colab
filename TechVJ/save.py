# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import asyncio 
import pyrogram
from pyrogram import Client, filters
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, UserAlreadyParticipant, InviteHashExpired, UsernameNotOccupied
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message 
import time
import os
import threading
import json
from config import API_ID, API_HASH
from database.db import database 
from TechVJ.strings import strings, HELP_TXT

def get(obj, key, default=None):
    try:
        return obj[key]
    except:
        return default


async def downstatus(client: Client, statusfile, message):
    while True:
        if os.path.exists(statusfile):
            break

        await asyncio.sleep(3)
      
    while os.path.exists(statusfile):
        with open(statusfile, "r") as downread:
            txt = downread.read()
        try:
            await client.edit_message_text(message.chat.id, message.id, f"Downloaded : {txt}")
            await asyncio.sleep(10)
        except:
            await asyncio.sleep(5)


# upload status
async def upstatus(client: Client, statusfile, message):
    while True:
        if os.path.exists(statusfile):
            break

        await asyncio.sleep(3)      
    while os.path.exists(statusfile):
        with open(statusfile, "r") as upread:
            txt = upread.read()
        try:
            await client.edit_message_text(message.chat.id, message.id, f"Uploaded : {txt}")
            await asyncio.sleep(10)
        except:
            await asyncio.sleep(5)


# progress writer
def progress(current, total, message, type):
    with open(f'{message.id}{type}status.txt', "w") as fileup:
        fileup.write(f"{current * 100 / total:.1f}%")


# start command
@Client.on_message(filters.command(["start"]))
async def send_start(client: Client, message: Message):
    await client.send_message(message.chat.id, f"<b>👋 Hi {message.from_user.mention}, I am Save Restricted Content Bot, I can send you restricted content by its post link.\n\nFor downloading restricted content, send me the link of the post you want to save.</b>")
    return


# help command
@Client.on_message(filters.command(["help"]))
async def send_help(client: Client, message: Message):
    await client.send_message(message.chat.id, f"{HELP_TXT}")
# cancel command
@Client.on_message(filters.command(["cancel"]))
async def cancel_command(client: Client, message: Message):
    task = user_tasks.get(message.chat.id)
    if task:
        task.cancel()
        del user_tasks[message.chat.id]
        await client.send_message(message.chat.id, "Your task has been cancelled.", reply_to_message_id=message.id)
    else:
        await client.send_message(message.chat.id, "There is no ongoing task to cancel.", reply_to_message_id=message.id)

@Client.on_message(filters.text & filters.private)
async def save(client: Client, message: Message):
    if "https://t.me/" in message.text:
        datas = message.text.split("/")
        temp = datas[-1].replace("?single","").split("-")
        fromID = int(temp[0].strip())
        try:
            toID = int(temp[1].strip())
        except:
            toID = fromID
        for msgid in range(fromID, toID+1):
            # private
            if "https://t.me/c/" in message.text:
                user_data = database.find_one({'chat_id': message.chat.id})
                if not get(user_data, 'logged_in', False) or user_data['session'] is None:
                    await client.send_message(message.chat.id, strings['need_login'])
                    return
                acc = Client("saverestricted", session_string=user_data['session'], api_hash=API_HASH, api_id=API_ID)
                await acc.connect()
                chatid = int("-100" + datas[4])
                await handle_private(client, acc, message, chatid, msgid)
    
            # bot
            elif "https://t.me/b/" in message.text:
                user_data = database.find_one({"chat_id": message.chat.id})
                if not get(user_data, 'logged_in', False) or user_data['session'] is None:
                    await client.send_message(message.chat.id, strings['need_login'])
                    return
                acc = Client("saverestricted", session_string=user_data['session'], api_hash=API_HASH, api_id=API_ID)
                await acc.connect()
                username = datas[4]
                try:
                    await handle_private(client, acc, message, username, msgid)
                except Exception as e:
                    await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)
            
	        # public
            else:
                username = datas[3]

                try:
                    msg = await client.get_messages(username, msgid)
                except UsernameNotOccupied: 
                    await client.send_message(message.chat.id, "The username is not occupied by anyone", reply_to_message_id=message.id)
                    return
                try:
                    await client.copy_message(message.chat.id, msg.chat.id, msg.id, reply_to_message_id=message.id)
                except:
                    try:    
                        user_data = database.find_one({"chat_id": message.chat.id})
                        if not get(user_data, 'logged_in', False) or user_data['session'] is None:
                            await client.send_message(message.chat.id, strings['need_login'])
                            return
                        acc = Client("saverestricted", session_string=user_data['session'], api_hash=API_HASH, api_id=API_ID)
                        await acc.connect()
                        await handle_private(client, acc, message, username, msgid)
                        
                    except Exception as e:
                        await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)

            # wait time
            await asyncio.sleep(3)


# handle private
async def handle_private(client: Client, acc, message: Message, chatid: int, msgid: int):
    msg: Message = await acc.get_messages(chatid, msgid)
    msg_type = get_message_type(msg)
    chat = message.chat.id

    if "Text" == msg_type:
        try:
            await client.send_message(chat, msg.text, entities=msg.entities, reply_to_message_id=message.id)
        except Exception as e:
            await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)
            return

    smsg = await client.send_message(message.chat.id, 'Downloading', reply_to_message_id=message.id)
    dosta = asyncio.create_task(downstatus(client, f'{message.id}downstatus.txt', smsg))
    try:
        file = await acc.download_media(msg, progress=progress, progress_args=[message, "down"])
        os.remove(f'{message.id}downstatus.txt')
    except Exception as e:
        await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)
        return

    upsta = asyncio.create_task(upstatus(client, f'{message.id}upstatus.txt', smsg))

    # Handling captions
    caption = msg.caption if msg.caption else None
    if caption and len(caption) > 1024:  # Telegram caption limit
        first_caption = caption[:1024]
        second_caption = caption[1024:]
    else:
        first_caption = caption
        second_caption = None

    if "Document" == msg_type:
        # Check file extension to determine how to handle the document
        if file.endswith(('.mp4', '.mkv', '.avi', '.mov', '.flv', '.webm')):
            # Handle video files sent as documents
            try:
                # Try to get thumbnail if available
                ph_path = None
                if msg.document.thumbs:
                    try:
                        ph_path = await acc.download_media(msg.document.thumbs[0].file_id)
                    except:
                        pass
                
                # Get video attributes if available
                duration = None
                width = None
                height = None
                
                for attr in msg.document.attributes:
                    if hasattr(attr, 'duration'):
                        duration = attr.duration
                    if hasattr(attr, 'width'):
                        width = attr.width
                    if hasattr(attr, 'height'):
                        height = attr.height
                
                # Send as video
                await client.send_video(
                    chat, file, duration=duration, width=width, height=height,
                    thumb=ph_path, caption=first_caption, reply_to_message_id=message.id, progress=progress,
                    progress_args=[message, "up"]
                )
                if second_caption:
                    await client.send_message(chat, second_caption, reply_to_message_id=message.id)
                
                if ph_path and os.path.exists(ph_path):
                    os.remove(ph_path)
                    
            except Exception as e:
                # If sending as video fails, send as document
                await client.send_document(
                    chat, file, caption=first_caption, reply_to_message_id=message.id,
                    progress=progress, progress_args=[message, "up"]
                )
                if second_caption:
                    await client.send_message(chat, second_caption, reply_to_message_id=message.id)
        
        elif file.endswith('.ogg'):
            # Handle ogg files as voice messages
            try:
                await client.send_voice(
                    chat, file, caption=first_caption, caption_entities=msg.caption_entities,
                    reply_to_message_id=message.id, progress=progress, progress_args=[message, "up"]
                )
                if second_caption:
                    await client.send_message(chat, second_caption, reply_to_message_id=message.id)
            except Exception as e:
                # If sending as voice fails, send as document
                await client.send_document(
                    chat, file, caption=first_caption, reply_to_message_id=message.id,
                    progress=progress, progress_args=[message, "up"]
                )
                if second_caption:
                    await client.send_message(chat, second_caption, reply_to_message_id=message.id)
        
        else:
            # Send other document types as they are
            try:
                await client.send_document(
                    chat, file, caption=first_caption, reply_to_message_id=message.id,
                    progress=progress, progress_args=[message, "up"]
                )
                if second_caption:
                    await client.send_message(chat, second_caption, reply_to_message_id=message.id)
            except Exception as e:
                await client.send_message(message.chat.id, f"Error uploading document: {e}", reply_to_message_id=message.id)

    elif "Video" == msg_type:
        try:
            ph_path = await acc.download_media(msg.video.thumbs[0].file_id) if msg.video.thumbs else None
        except:
            ph_path = None

        try:
            # Send video as stream
            await client.send_video(
                chat, file, duration=msg.video.duration, width=msg.video.width, height=msg.video.height,
                thumb=ph_path, caption=first_caption, reply_to_message_id=message.id, progress=progress,
                progress_args=[message, "up"]
            )
            if second_caption:
                await client.send_message(chat, second_caption, reply_to_message_id=message.id)
        except Exception as e:
            await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)
        if ph_path and os.path.exists(ph_path):
            os.remove(ph_path)

    elif "VideoNote" == msg_type:
        try:
            await client.send_video_note(
                chat, file, length=msg.video_note.length, duration=msg.video_note.duration,
                reply_to_message_id=message.id, progress=progress, progress_args=[message, "up"]
            )
        except Exception as e:
            await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)

    elif "Voice" == msg_type:
        try:
            await client.send_voice(
                chat, file, caption=first_caption, caption_entities=msg.caption_entities,
                reply_to_message_id=message.id, progress=progress, progress_args=[message, "up"]
            )
            if second_caption:
                await client.send_message(chat, second_caption, reply_to_message_id=message.id)
        except Exception as e:
            await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)

    elif "Audio" == msg_type:
        # Check if it's an OGG file to send as voice
        if file.endswith('.ogg'):
            try:
                await client.send_voice(
                    chat, file, caption=first_caption, caption_entities=msg.caption_entities,
                    reply_to_message_id=message.id, progress=progress, progress_args=[message, "up"]
                )
                if second_caption:
                    await client.send_message(chat, second_caption, reply_to_message_id=message.id)
            except Exception as e:
                # If sending as voice fails, try sending as audio
                try:
                    ph_path = await acc.download_media(msg.audio.thumbs[0].file_id) if msg.audio.thumbs else None
                except:
                    ph_path = None

                try:
                    await client.send_audio(
                        chat, file, thumb=ph_path, caption=first_caption, reply_to_message_id=message.id,
                        progress=progress, progress_args=[message, "up"]
                    )
                    if second_caption:
                        await client.send_message(chat, second_caption, reply_to_message_id=message.id)
                except Exception as e:
                    await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)
                if ph_path and os.path.exists(ph_path):
                    os.remove(ph_path)
        else:
            # Handle regular audio files
            try:
                ph_path = await acc.download_media(msg.audio.thumbs[0].file_id) if msg.audio.thumbs else None
            except:
                ph_path = None

            try:
                await client.send_audio(
                    chat, file, thumb=ph_path, caption=first_caption, reply_to_message_id=message.id,
                    progress=progress, progress_args=[message, "up"]
                )
                if second_caption:
                    await client.send_message(chat, second_caption, reply_to_message_id=message.id)
            except Exception as e:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)
            if ph_path and os.path.exists(ph_path):
                os.remove(ph_path)

    elif "Photo" == msg_type:
        try:
            await client.send_photo(chat, file, caption=first_caption, reply_to_message_id=message.id)
            if second_caption:
                await client.send_message(chat, second_caption, reply_to_message_id=message.id)
        except Exception as e:
            await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)
    
    elif "Animation" == msg_type:
        try:
            await client.send_animation(
                chat, file, caption=first_caption, reply_to_message_id=message.id,
                progress=progress, progress_args=[message, "up"]
            )
            if second_caption:
                await client.send_message(chat, second_caption, reply_to_message_id=message.id)
        except Exception as e:
            await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)
    
    elif "Sticker" == msg_type:
        try:
            await client.send_sticker(chat, file, reply_to_message_id=message.id)
        except Exception as e:
            await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)
    
    else:
        # Unknown type - send as document
        try:
            await client.send_document(
                chat, file, caption=first_caption, reply_to_message_id=message.id,
                progress=progress, progress_args=[message, "up"]
            )
            if second_caption:
                await client.send_message(chat, second_caption, reply_to_message_id=message.id)
        except Exception as e:
            await client.send_message(message.chat.id, f"Error uploading unknown file type: {e}", reply_to_message_id=message.id)

    if os.path.exists(f'{message.id}upstatus.txt'):
        os.remove(f'{message.id}upstatus.txt')
    if os.path.exists(file):
        os.remove(file)
    await client.delete_messages(message.chat.id, [smsg.id])

# get the type of message
def get_message_type(msg: pyrogram.types.messages_and_media.message.Message):
    try:
        msg.video_note.file_id
        return "VideoNote"
    except:
        pass
    try:
        msg.document.file_id
        return "Document"
    except:
        pass

    try:
        msg.video.file_id
        return "Video"
    except:
        pass

    try:
        msg.animation.file_id
        return "Animation"
    except:
        pass

    try:
        msg.sticker.file_id
        return "Sticker"
    except:
        pass

    try:
        msg.voice.file_id
        return "Voice"
    except:
        pass

    try:
        msg.audio.file_id
        return "Audio"
    except:
        pass

    try:
        msg.photo.file_id
        return "Photo"
    except:
        pass

    try:
        msg.text
        return "Text"
    except:
        pass
        
