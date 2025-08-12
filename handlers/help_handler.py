from aiogram import F
from aiogram.types import Message
from aiogram.filters import Command
from utils.templates import load_template
from utils.pictures import get_picture, picture_exists

def register_help_handlers(dp):
    
    @dp.message(Command("start"))
    async def start_command(message: Message):
        
        welcome_text = load_template('start_template.txt')
        
        start_picture = get_picture('start.jpg')  
        if start_picture and picture_exists('start.jpg'):
            await message.reply_photo(
                photo=start_picture,
                caption=welcome_text,
                parse_mode='Markdown'
            )
        elif get_picture('start.png') and picture_exists('start.png'):
            start_picture = get_picture('start.png')
            await message.reply_photo(
                photo=start_picture,
                caption=welcome_text,
                parse_mode='Markdown'
            )
        else:
            await message.reply(welcome_text, parse_mode='Markdown')
    
    @dp.message(F.text.in_(["помощь", "help", "команды"]))
    async def help_command(message: Message):
        help_text = load_template('help_template.txt')
        
        help_picture = get_picture('help.jpg')
        
        if help_picture and picture_exists('help.jpg'):
            await message.reply_photo(
                photo=help_picture,
                caption=help_text,
                parse_mode='Markdown'
            )
        elif get_picture('help.png') and picture_exists('help.png'):
            help_picture = get_picture('help.png')
            await message.reply_photo(
                photo=help_picture,
                caption=help_text,
                parse_mode='Markdown'
            )
        else:
            await message.reply(help_text, parse_mode='Markdown')