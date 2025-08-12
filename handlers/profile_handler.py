from aiogram import F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from utils.database import save_user_profile, get_user_profile, delete_user_profile
from utils.templates import load_template
from datetime import datetime

def register_profile_handlers(dp, osu_api):
    
    @dp.message(F.text.startswith("привязать "))
    async def link_profile(message: Message):
        try:
            username = message.text[10:].strip()
            
            if not username:
                await message.reply("❌ Укажите никнейм после команды!\nПример: привязать cookiezi")
                return
            
            user_data = await osu_api.get_user(username)
            
            if not user_data:
                await message.reply("❌ Пользователь не найден! Проверьте правильность никнейма.")
                return
            
            save_user_profile(message.from_user.id, user_data['username'], user_data['id'])
            
            await message.reply(f"✅ Профиль успешно привязан!\n👤 osu! профиль: {user_data['username']}")
            
        except Exception as e:
            print(f"[!] error during binding profile")
            await message.reply("❌ Произошла ошибка при привязке профиля.")
    
    @dp.message(F.text.in_(["профиль", "профайл", "проф", "стата", "статистика"]))
    async def show_profile(message: Message):
        try:
            user_profile = get_user_profile(message.from_user.id)
            
            if not user_profile:
                await message.reply("❌ У вас нет привязанного профиля!\nИспользуйте: привязать <никнейм>")
                return
            
            username = user_profile[0]
            
            user_data = await osu_api.get_user(username)
            
            if not user_data:
                await message.reply("❌ Не удалось получить данные профиля. Попробуйте позже.")
                return
            
            stats = user_data['statistics']
            
            play_time_hours = stats['play_time'] // 3600
            play_time_minutes = (stats['play_time'] % 3600) // 60
            
            rank_text = f"Rank: 🥈SS: {stats['grade_counts']['ssh']} | 🥇SS: {stats['grade_counts']['ss']} | 🪙 SH: {stats['grade_counts']['sh']} | 🏆 S: {stats['grade_counts']['s']} | 🧱 A: {stats['grade_counts']['a']}"
            
            profile_text = load_template('profile_template.txt', {
                'username': user_data['username'],
                'pp': f"{stats['pp']:,.0f}",
                'country_rank': f"{stats['country_rank']:,}",
                'global_rank': f"{stats['global_rank']:,}",
                'accuracy': f"{stats['hit_accuracy']:.2f}",
                'play_count': f"{stats['play_count']:,}",
                'play_time_hours': play_time_hours,
                'play_time_minutes': play_time_minutes,
                'rank_text': rank_text
            })
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🎵 Последний плей", callback_data=f"recent_{user_data['id']}")]
            ])
            
            await message.reply(profile_text, reply_markup=keyboard)
            
        except Exception as e:
            print(f"Ошибка при показе профиля: {e}")
            await message.reply("[!] error 47")
    
    @dp.callback_query(F.data.startswith("recent_"))
    async def show_recent_play(callback: CallbackQuery):
        try:
            user_id = callback.data.split("_")[1]
            
            # Пробуем разные возможные названия методов для получения последних игр
            recent_plays = None
            
            # Вариант 1: get_user_recent
            if hasattr(osu_api, 'get_user_recent'):
                recent_plays = await osu_api.get_user_recent(user_id, limit=1)
            # Вариант 2: get_recent_scores  
            elif hasattr(osu_api, 'get_recent_scores'):
                recent_plays = await osu_api.get_recent_scores(user_id, limit=1)
            # Вариант 3: get_user_scores_recent
            elif hasattr(osu_api, 'get_user_scores_recent'):
                recent_plays = await osu_api.get_user_scores_recent(user_id, limit=1)
            # Вариант 4: user_recent
            elif hasattr(osu_api, 'user_recent'):
                recent_plays = await osu_api.user_recent(user_id, limit=1)
            else:
                await callback.answer("❌ Метод получения последних игр не найден", show_alert=True)
                return
            
            if not recent_plays or len(recent_plays) == 0:
                await callback.answer("❌ Последние игры не найдены", show_alert=True)
                return
            
            play = recent_plays[0]
            beatmap = play.get('beatmap', {})
            beatmapset = play.get('beatmapset', {})
            
            # Форматируем время
            created_at = datetime.fromisoformat(play['created_at'].replace('Z', '+00:00'))
            time_ago = format_time_ago(created_at)
            
            # Определяем мод строку
            mods = play.get('mods', [])
            mods_str = "+".join(mods) if mods else "No mods"
            
            # Определяем grade эмодзи
            grade_emojis = {
                'XH': '🥈',
                'X': '🥇', 
                'SH': '🪙',
                'S': '🏆',
                'A': '🥉',
                'B': '🟢',
                'C': '🟡',
                'D': '🔴',
                'F': '💀'
            }
            grade_emoji = grade_emojis.get(play.get('rank', 'F'), '❓')
            
            # Рассчитываем точность
            statistics = play.get('statistics', {})
            total_hits = (statistics.get('count_300', 0) + 
                         statistics.get('count_100', 0) + 
                         statistics.get('count_50', 0) + 
                         statistics.get('count_miss', 0))
            
            if total_hits > 0:
                accuracy = ((statistics.get('count_300', 0) * 300 + 
                           statistics.get('count_100', 0) * 100 + 
                           statistics.get('count_50', 0) * 50) / (total_hits * 300)) * 100
            else:
                accuracy = 0
            
            # Используем шаблон для recent play
            recent_text = load_template('recent_template.txt', {
                'title': beatmapset.get('title', 'Unknown'),
                'version': beatmap.get('version', 'Unknown'),
                'creator': beatmapset.get('creator', 'Unknown'),
                'grade_emoji': grade_emoji,
                'rank': play.get('rank', 'F'),
                'difficulty_rating': f"{beatmap.get('difficulty_rating', 0):.2f}",
                'accuracy': f"{accuracy:.2f}",
                'max_combo': f"{play.get('max_combo', 0)}",
                'pp': f"{play.get('pp', 0):.0f}",
                'count_300': statistics.get('count_300', 0),
                'count_100': statistics.get('count_100', 0),
                'count_50': statistics.get('count_50', 0),
                'count_miss': statistics.get('count_miss', 0),
                'mods': mods_str,
                'time_ago': time_ago
            })
            
            # Кнопка возврата к профилю
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="← Назад к профилю", callback_data="back_to_profile")]
            ])
            
            await callback.message.edit_text(recent_text, reply_markup=keyboard, parse_mode='Markdown')
            await callback.answer()
            
        except Exception as e:
            print(f"Ошибка при показе последнего плея: {e}")
            await callback.answer("❌ Ошибка при загрузке последнего плея", show_alert=True)
    
    @dp.callback_query(F.data == "back_to_profile")
    async def back_to_profile(callback: CallbackQuery):
        try:
            # Получаем профиль пользователя заново
            user_profile = get_user_profile(callback.from_user.id)
            
            if not user_profile:
                await callback.answer("❌ Профиль не найден", show_alert=True)
                return
            
            username = user_profile[0]
            user_data = await osu_api.get_user(username)
            
            if not user_data:
                await callback.answer("❌ Не удалось загрузить профиль", show_alert=True)
                return
            
            stats = user_data['statistics']
            
            play_time_hours = stats['play_time'] // 3600
            play_time_minutes = (stats['play_time'] % 3600) // 60
            
            rank_text = f"Ранг: 🥈SS: {stats['grade_counts']['ssh']} | 🥇SS: {stats['grade_counts']['ss']} | 🪙 SH: {stats['grade_counts']['sh']} | 🏆 S: {stats['grade_counts']['s']} | 🧱 A: {stats['grade_counts']['a']}"
            
            profile_text = load_template('profile_template.txt', {
                'username': user_data['username'],
                'pp': f"{stats['pp']:,.0f}",
                'country_rank': f"{stats['country_rank']:,}",
                'global_rank': f"{stats['global_rank']:,}",
                'accuracy': f"{stats['hit_accuracy']:.2f}",
                'play_count': f"{stats['play_count']:,}",
                'play_time_hours': play_time_hours,
                'play_time_minutes': play_time_minutes,
                'rank_text': rank_text
            })
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🎵 Последний плей", callback_data=f"recent_{user_data['id']}")]
            ])
            
            await callback.message.edit_text(profile_text, reply_markup=keyboard)
            await callback.answer()
            
        except Exception as e:
            print(f"Ошибка при возврате к профилю: {e}")
            await callback.answer("❌ Ошибка при загрузке профиля", show_alert=True)

def format_time_ago(created_at):
    """Форматирует время 'назад'"""
    now = datetime.now(created_at.tzinfo)
    diff = now - created_at
    
    if diff.days > 0:
        return f"{diff.days} дн. назад"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} ч. назад"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} мин. назад"
    else:
        return "Только что"