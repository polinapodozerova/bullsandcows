from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from telegram import Update, ParseMode
from collections import Counter
from random import choice
import pandas as pd


data = pd.read_csv('nounlist.csv')
five_word_list = []
for i in data['ATM']:
    if len(i) == 5:
        five_word_list.append(i)
data1 = pd.read_csv('WordnetNouns.csv')
dictionary = []
for i in data1['Word'][1:]:
    if isinstance(i, str) and len(i) == 5:
        dictionary.append(i)
        
previous_tries = []
secret_word = None

def start(update: Update, context):
    global secret_word
    secret_word = choice(five_word_list)
    context.bot.send_message(chat_id=update.effective_chat.id, text=f"Hello! Let's play a game. \nPlease enter a {len(secret_word)}-letter word.\nIf you'll need some help, just type \hint.")
start_handler = CommandHandler('start', start)


def help_me(update: Update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=f"OK, I'll give you a hint. Your word is ||{secret_word}||", parse_mode='Markdown')
help_me_handler = CommandHandler('hint', help_me)


def list_tries(update: Update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text='\n'.join(previous_tries))
list_tries_handler= CommandHandler('tries', list_tries)


def guess(update: Update, context: CallbackContext):
    global previous_tries
    global secret_word
    if secret_word is None:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Please start the game using /start.")
        return

    user_guess = update.message.text.lower()

    if not isinstance(user_guess, str) or len(user_guess) != 5:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Please enter a 5-letter word.")
        return
    
    if user_guess not in (dictionary + five_word_list):
        context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I don't know this word :(")
        return

    bulls, cows = calculate_bulls_and_cows(user_guess)
    if bulls == 5:
        context.bot.send_message(chat_id=update.effective_chat.id, text="*Congratulations! You guessed the word correctly.*", parse_mode = 'Markdown')
        context.bot.send_sticker(chat_id=update.effective_chat.id, sticker='CAACAgIAAxkBAAEJ7exkzm_KNfLVtLxrbS0ZE-oy4Br87AAC4BoAAtlAuEq6iP63Pi2bIC8E')
        secret_word = None
        previous_tries = []
    else:
        response = f"Your guess: *{user_guess}* --- Bulls: {bulls}, Cows: {cows}"
        previous_tries.append(response)
        context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode='Markdown')
guess_handler = MessageHandler(Filters.text & ~Filters.command, guess)


def calculate_bulls_and_cows(guess_word):
    global secret_word
    dic = Counter(secret_word)-Counter(guess_word)
    bulls, cows = 0, 0
    for i in range(len(secret_word)):
        if guess_word[i] == secret_word[i]:
            bulls += 1
    cows = len(secret_word) - sum(dic.values()) - bulls
    return bulls, cows


def main():
    updater = Updater(token=TOKEN)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(help_me_handler)
    dispatcher.add_handler(guess_handler)
    dispatcher.add_handler(list_tries_handler)


    updater.start_polling()
    print("Bot started!")

    updater.idle()

if __name__ == "__main__":
    main()
