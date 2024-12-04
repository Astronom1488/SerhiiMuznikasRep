import functions as fuc
import time
import telebot
from cred import TelegramBotID, ChatID
import random

leverage = 25
balance_percent = 5
running = True
bot = telebot.TeleBot(TelegramBotID)
pointer = str(random.randint(1000, 9999))
PnLInPlus = 0


@bot.message_handler(commands=['start'], func=lambda message: message.chat.id == int(ChatID))
def send_welcome(message):
    fuc.SendMessageOnTelegram(bot, pointer, message, "Bot on.")

@bot.message_handler(commands=['run'], func=lambda message: message.chat.id == int(ChatID))
def run(message):
    global running
    fuc.SendMessageOnTelegram(bot, pointer, message, "Bot working. If you need< you can stop it by: /stop")
    running = True
    main(message)

@bot.message_handler(commands=['stop'], func=lambda message: message.chat.id == int(ChatID))
def stop_bot(message):
    global running
    running = False
    fuc.SendMessageOnTelegram(bot, pointer, message, "Bot is stop /run")

def main(message):
    while running:
        try:
            global PnLInPlus
            global balance_percent
            position = fuc.get_opened_positions(symbol)
            open_sl = position[0]
            money = fuc.get_balance_on_account()
            if open_sl == "":
                timer15min = '/html/body/div[3]/div[4]/div[2]/div[2]/div/section/div/div[2]/div[1]/div/div/button[3]/span[1]'
                timer60min = '/html/body/div[4]/div[4]/div[2]/div[2]/div/section/div/div[2]/div[1]/div/div/button[5]/span[1]/span'
                meaning15min = fuc.get_trading_signal(symbol, timer15min)
                meaning60min = fuc.get_trading_signal(symbol, timer60min)
                if meaning60min == "Активно покупать" and meaning15min == "Активно покупать":
                    signal = "long"
                elif meaning60min == "Активно покупать" and meaning15min == "Покупать":
                    signal = "long"
                elif meaning60min == "Покупать" and meaning15min == "Активно покупать":
                    signal = "long"
                elif meaning60min == "Покупать" and meaning15min == "Покупать":
                    signal = "long"

                elif meaning60min == "Активно продавать" and meaning15min == "Активно продавать":
                    signal = "short"
                elif meaning60min == "Активно продавать" and meaning15min == "Продавать":
                    signal = "short"
                elif meaning60min == "Продавать" and meaning15min == "Активно продавать":
                    signal = "short"
                elif meaning60min == "Продавать" and meaning15min == "Продавать":
                    signal = "short"
                else:
                    signal = "neutral"

                # signal == 'long' or
                if signal == 'longMAX':
                    fuc.open_position(symbol, 'long', balance_percent, leverage)
                    fuc.SendMessageOnTelegram(bot, pointer, message, f"Bot open long {money}$")
                    time.sleep(10)
                # signal == 'short' or
                elif signal == 'shortMAX':
                    fuc.open_position(symbol, 'short', balance_percent, leverage)
                    fuc.SendMessageOnTelegram(bot, pointer, message, f"Bot open short {money}$")
                    time.sleep(10)
                else:
                    time.sleep(10)
                    # time.sleep(60*5)
            else:
                quantity = position[1]
                timer15min = '/html/body/div[3]/div[4]/div[2]/div[2]/div/section/div/div[2]/div[1]/div/div/button[3]/span[1]'
                timer60min = '/html/body/div[4]/div[4]/div[2]/div[2]/div/section/div/div[2]/div[1]/div/div/button[5]/span[1]'
                meaning60min = fuc.get_trading_signal(symbol, timer60min)
                meaning15min = fuc.get_trading_signal(symbol, timer15min)
                if meaning60min == "Активно покупать" and meaning15min == "Активно покупать":
                    NEWsignal = "long"
                elif meaning60min == "Активно покупать" and meaning15min == "Покупать":
                    NEWsignal = "long"
                elif meaning60min == "Покупать" and meaning15min == "Активно покупать":
                    NEWsignal = "long"
                elif meaning60min == "Покупать" and meaning15min == "Покупать":
                    NEWsignal = "long"

                elif meaning60min == "Активно продавать" and meaning15min == "Активно продавать":
                    NEWsignal = "short"
                elif meaning60min == "Активно продавать" and meaning15min == "Продавать":
                    NEWsignal = "short"
                elif meaning60min == "Продавать" and meaning15min == "Активно продавать":
                    NEWsignal = "short"
                elif meaning60min == "Продавать" and meaning15min == "Продавать":
                    NEWsignal = "short"
                else:
                    NEWsignal = "neutral"
                if NEWsignal == "short":
                    NEWsignal = "neutral"
                if NEWsignal == "long":
                    NEWsignal = "neutral"
                PnL = position[6]


                if open_sl == 'long':
                    if NEWsignal == "short" or NEWsignal == "shortMAX" or NEWsignal == "neutral" or NEWsignal == "long":
                        fuc.close_position(symbol, 'long', abs(quantity), leverage)

                        fuc.SendMessageOnTelegram(bot, pointer, message, f"The bot closed the order due to a change in position {money}$")
                        balance_percent = 8
                    elif PnL <= -100:
                        fuc.close_position(symbol, 'long', abs(quantity), leverage)
                        fuc.SendMessageOnTelegram(bot, pointer, message, f"The bot closed the order at minus 100% {money}$")
                        balance_percent = 8
                        time.sleep(120)
                    elif PnL >= 10:
                        fuc.close_position(symbol, 'long', abs(quantity), leverage)
                        fuc.SendMessageOnTelegram(bot, pointer, message, f"The bot closed the order in plus {money}$")
                        balance_percent = 8


                elif open_sl == 'short':
                    PnL = PnL * -1
                    if NEWsignal == "long" or NEWsignal == "longMAX" or NEWsignal == "neutral" or NEWsignal == "short":
                        fuc.close_position(symbol, 'short', abs(quantity), leverage)
                        fuc.SendMessageOnTelegram(bot, pointer, message, f"Bot closed order due to position change {money}$")
                        balance_percent = 8
                    elif PnL <= -100:
                        fuc.close_position(symbol, 'short', abs(quantity), leverage)
                        fuc.SendMessageOnTelegram(bot, pointer, message, f"The bot closed the order at minus 100% {money}$")
                        balance_percent = 8
                        time.sleep(120)
                    elif PnL >= 10:
                        fuc.close_position(symbol, 'short', abs(quantity), leverage)
                        fuc.SendMessageOnTelegram(bot, pointer, message, f"The bot closed the order in plus {money}$")
                        balance_percent = 8
                else:
                    time.sleep(30)
        except Exception as ex:
            fuc.SendMessageOnTelegram(bot, pointer, message, f"The bot did not turn on for some reason! {ex}")
            time.sleep(60)

@bot.message_handler(content_types=['text'], func=lambda message: message.chat.id == int(ChatID))
def get_name(message):
    global symbol
    symbol = message.text + "USDT"
    fuc.SendMessageOnTelegram(bot, pointer, message, f"Enter nam of toksen: {symbol} /run")

bot.polling()