import locale
from configparser import ConfigParser
from pathlib import Path

import yfinance as yf
from telegram import ReplyKeyboardRemove, Update
from telegram.ext import (ApplicationBuilder, CommandHandler, ContextTypes,
                          MessageHandler, filters)

locale.setlocale(locale.LC_MONETARY, 'pt_BR.UTF-8')

file_path = Path(__file__).parent.resolve()

credentials = ConfigParser()
credentials.read(f'{file_path}/config.ini')

TOKEN_API = credentials.get('DEFAULT', 'Key')


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await context.bot.send_message(chat_id=update.effective_chat.id, text='Olá, o que deseja fazer no momento?\n\n' +
                                   '• Informações sobre renda variável: Digite o código do FII ou AÇÃO.')


async def stocks_information(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await context.bot.send_message(chat_id=update.effective_chat.id, text=f'Certo, buscarei sobre a ação "{update.message.text.upper()}".\n\nAguarde um momento enquanto os dados estão sendo processados.')

    stock = yf.Ticker(update.message.text+".SA")

    if stock.info["regularMarketPrice"] is None:

        text = f'O código {update.message.text.upper()} não foi encontrado, verifique a escrita e tente novamente.'

    else:

        stock_variation = (
            stock.info["regularMarketPrice"] / stock.info['previousClose'] - 1) * 100

        text = f'A ação {update.message.text.upper()} está cotada no valor de {locale.currency(stock.info["regularMarketPrice"])}.\n\nHouve uma variação de {stock_variation:.2f}% em relação a precificação do último dia útil ({locale.currency(stock.info["previousClose"])}).'

        if stock.info['volume'] != 0:

            text += f'\nTiveram cerca de {stock.info["volume"]} transações hoje.'

    await update.message.reply_text(text,
                                    reply_markup=ReplyKeyboardRemove(),
                                    )


async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Não fui programado para reconhecer este comando.")


def main():

    application = ApplicationBuilder().token(TOKEN_API).build()

    application.add_handler(CommandHandler("start", start))

    application.add_handler(MessageHandler(
        filters.Regex('^[a-zA-Z][a-zA-Z][a-zA-Z][a-zA-Z]4$|[a-zA-Z][a-zA-Z][a-zA-Z][a-zA-Z]11$'), stocks_information))
    application.add_handler(MessageHandler(
        filters.COMMAND, unknown_command))

    application.run_polling()


if __name__ == "__main__":
    main()
