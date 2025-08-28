import os
import re
import logging
from re import sub as re_sub
from aioshutil import move
from asyncio import create_subprocess_exec
from asyncio.subprocess import PIPE
from bot import LOGGER, bot_cache
from bot.helper.ext_utils.fs_utils import clean_target

LOGGER = logging.getLogger(__name__)

########-------- Metadata -------------#########
async def edit_metadata(listener, base_dir: str, media_file: str, outfile: str, metadata: str = ''):
    file_name = os.path.basename(media_file)  # Get the filename without path
    file_namex = re_sub(r'www\S+', '', file_name)
    title_metadata = f'{metadata}{file_namex}'

    cmd = [
        bot_cache['pkgs'][2], '-i', media_file,
        '-map', '0',
        '-metadata', f'title={title_metadata}',
        '-metadata:s:v', f'title={metadata}',
        '-metadata:s:a', f'title={metadata}',
        '-metadata:s:s', f'title={metadata}', 
        '-c', 'copy',
        outfile
    ]
  
    listener.suproc = await create_subprocess_exec(*cmd, stderr=PIPE)
    code = await listener.suproc.wait()
    
    if code == 0:
        await clean_target(media_file)
        listener.seed = False
        await move(outfile, base_dir)
    else:
        await clean_target(outfile)
        LOGGER.error('%s. Changing metadata failed, Path %s', await listener.suproc.stderr.read().decode(), media_file)


########-------- Attachment -------------#########
async def edit_attachment(listener, base_dir: str, media_file: str, outfile: str, attachment: str = ''):
    #Attachment
    omg = "photo"  
    attachment_ext = attachment.split(".")[-1].lower()   
    mime_type = "application/octet-stream"
    if attachment_ext in ["jpg", "jpeg"]:
        mime_type = "image/jpeg"
    elif attachment_ext == "png":
        mime_type = "image/png"
        
    cmd = [
        bot_cache['pkgs'][2], '-hide_banner', '-loglevel', 'error', '-progress', 'pipe:1',
        '-i', media_file,
        '-attach', attachment,
        '-metadata:s:t', f'mimetype={mime_type}',
        '-metadata:s:t', f'filename={omg}.{attachment_ext}',
        '-disposition:t', 'default',
        '-c', 'copy', 
        '-map', '0', 
        '-map', '0:t?', 
        outfile
    ]  
    listener.suproc = await create_subprocess_exec(*cmd, stderr=PIPE)
    code = await listener.suproc.wait()
    if code == 0:
        await clean_target(media_file)
        listener.seed = False
        await move(outfile, base_dir)
    else:
        await clean_target(outfile)
        LOGGER.error('%s. Changing failed, Path %s', await listener.suproc.stderr.read().decode(), media_file)