import os
import logging
from datetime import datetime, timedelta
from typing import Any
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ConversationHandler, filters
from db_handler import DBHandler
from graph_generator import GraphGenerator

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.WARNING)
logger = logging.getLogger(__name__)

# States for conversation handler
CHOOSING_ACTION, ADDING_PRICE, ADDING_LITERS, ADDING_KM, ADDING_TIMESTAMP, CHOOSING_GRAPH, CHOOSING_PERIOD = range(7)

# Initialize database handler
db = DBHandler()
graph_gen = GraphGenerator()

async def start(update: Update, context: Any):
    """Send welcome message when the command /start is issued."""
    assert update.message is not None
    welcome_text = (
        "👋 Welcome to FuelGraph Bot!\n\n"
        "I can help you track your fuel consumption and generate useful graphs.\n\n"
        "Use /help to see available commands."
    )
    keyboard = [
        ['📝 Add Refill Data'],
        ['📊 Generate Graphs'],
        ['❓ Help']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)
    return CHOOSING_ACTION

async def help_command(update: Update, context: Any):
    """Send help message."""
    assert update.message is not None
    help_text = (
        "🚗 *FuelGraph Bot Help*\n\n"
        "*Commands:*\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n\n"
        "*Features:*\n"
        "📝 Add Refill Data - Record new fuel refill\n"
        "📊 Generate Graphs - Create visualizations\n\n"
        "*Available Graphs:*\n"
        "- Price per liter over time\n"
        "- Kilometers travelled\n"
        "- Fuel consumption"
    )
    await update.message.reply_text(help_text, parse_mode='Markdown')
    return CHOOSING_ACTION

async def add_refill(update: Update, context: Any):
    """Start the refill data addition process."""
    assert update.message is not None
    await update.message.reply_text("Please enter the price paid:")
    return ADDING_PRICE

async def price_received(update: Update, context: Any):
    """Handle received price."""
    assert update.message is not None
    try:
        assert update.message.text is not None
        price = float(update.message.text)
        context.user_data['price'] = price
        await update.message.reply_text("Great! Now enter the number of liters:")
        return ADDING_LITERS
    except ValueError:
        await update.message.reply_text("Invalid number for the price. Operation cancelled.")
        return CHOOSING_ACTION

async def liters_received(update: Update, context: Any):
    """Handle received liters."""
    assert update.message is not None
    try:
        assert update.message.text is not None
        liters = float(update.message.text)
        context.user_data['liters'] = liters
        await update.message.reply_text("Excellent! Now enter the kilometers travelled:")
        return ADDING_KM
    except ValueError:
        await update.message.reply_text("Invalid number for liters. Operation cancelled.")
        return CHOOSING_ACTION

async def km_received(update: Update, context: Any):
    """Handle received kilometers and save all data."""
    assert update.message is not None
    try:
        assert update.message.text is not None
        km = float(update.message.text)
        context.user_data['km'] = km
        await update.message.reply_text("Perfect! Finally, enter the timestamp, if needed:")
        return ADDING_TIMESTAMP
    except ValueError:
        await update.message.reply_text("Invalid number for kilometers. Operation cancelled.")
        return CHOOSING_ACTION

async def timestamp_received(update: Update, context: Any):
    """Handle received timestamp and save all data."""
    assert update.message is not None
    assert update.effective_user is not None
    try:
        assert update.message.text is not None
        if len(update.message.text) == 13:
            text = int(update.message.text[:10])
        elif len(update.message.text) == 10:
            text = int(update.message.text)
        else:
            raise ValueError
        timestamp = datetime.fromtimestamp(text)
        data = {
            'user_id': update.effective_user.id,
            'price': context.user_data['price'],
            'liters': context.user_data['liters'],
            'km': context.user_data['km'],
            'timestamp': timestamp
        }
        db.add_refill(data)
        await update.message.reply_text("✅ Data saved successfully!")
        return CHOOSING_ACTION
    except:
        data: dict[str, Any] = {
            'user_id': update.effective_user.id,
            'price': context.user_data['price'],
            'liters': context.user_data['liters'],
            'km': context.user_data['km'],
            'timestamp': datetime.now()
        }
        db.add_refill(data)
        await update.message.reply_text("Timestamp invalid or not provided. ✅ Adding data as current.")
        return CHOOSING_ACTION

async def generate_graphs(update: Update, context: Any):
    """Show graph options."""
    assert update.message is not None
    keyboard = [
        [InlineKeyboardButton("Price per liter", callback_data='graph_price')],
        [InlineKeyboardButton("Kilometers travelled", callback_data='graph_km')],
        [InlineKeyboardButton("Fuel consumption", callback_data='graph_consumption')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Choose the type of graph:", reply_markup=reply_markup)
    return CHOOSING_GRAPH

async def handle_graph_choice(update: Update, context: Any):
    """Handle graph type selection."""
    assert update.callback_query is not None
    query = update.callback_query
    await query.answer()
    context.user_data['graph_type'] = query.data
    
    keyboard = [
        [InlineKeyboardButton("Last month", callback_data='period_1m')],
        [InlineKeyboardButton("Last 3 months", callback_data='period_3m')],
        [InlineKeyboardButton("Last 6 months", callback_data='period_6m')],
        [InlineKeyboardButton("Last year", callback_data='period_1y')],
        [InlineKeyboardButton("All", callback_data='period_all')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("Choose the time period:", reply_markup=reply_markup)
    return CHOOSING_PERIOD

async def handle_period_choice(update: Update, context: Any):
    """Generate and send the requested graph."""
    assert update.callback_query is not None
    query = update.callback_query
    await query.answer()
    assert query.data is not None
    
    # Calculate date range
    period = query.data.split('_')[1]
    end_date = datetime.now()
    if period == '1m':
        start_date = end_date - timedelta(days=30)
    elif period == '3m':
        start_date = end_date - timedelta(days=90)
    elif period == '6m':
        start_date = end_date - timedelta(days=180)
    elif period == '1y':
        start_date = end_date - timedelta(days=365)
    else:
        start_date = datetime(1970, 1, 1)
    
    # Get data and generate graph
    assert update.effective_user is not None
    user_id = update.effective_user.id
    data = db.get_refills(user_id, start_date, end_date)
    
    if not data:
        await query.edit_message_text("No data available for the selected period.")
        return CHOOSING_ACTION
    
    graph_type = context.user_data['graph_type'].split('_')[1]
    graph_path = graph_gen.generate_graph(user_id, data, graph_type, start_date, end_date)
    
    # Send graph
    assert update.effective_chat is not None
    with open(graph_path, 'rb') as photo:
        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo)
    os.remove(graph_path)  # Clean up
    
    return CHOOSING_ACTION

def main():
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(os.environ['TELEGRAM_TOKEN']).build()

    # Add conversation handler
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('start', start),
            MessageHandler(filters.Regex('^📝 Add Refill Data$'), add_refill),
            MessageHandler(filters.Regex('^📊 Generate Graphs$'), generate_graphs),
            MessageHandler(filters.Regex('^❓ Help$'), help_command)
        ],
        states={
            CHOOSING_ACTION: [
                MessageHandler(filters.Regex('^📝 Add Refill Data$'), add_refill),
                MessageHandler(filters.Regex('^📊 Generate Graphs$'), generate_graphs),
                MessageHandler(filters.Regex('^❓ Help$'), help_command)
            ],
            ADDING_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, price_received)],
            ADDING_LITERS: [MessageHandler(filters.TEXT & ~filters.COMMAND, liters_received)],
            ADDING_KM: [MessageHandler(filters.TEXT & ~filters.COMMAND, km_received)],
            ADDING_TIMESTAMP: [MessageHandler(filters.TEXT & ~filters.COMMAND, timestamp_received)],
            CHOOSING_GRAPH: [CallbackQueryHandler(handle_graph_choice)],
            CHOOSING_PERIOD: [CallbackQueryHandler(handle_period_choice)]
        },
        fallbacks=[CommandHandler('start', start)]
    )

    application.add_handler(conv_handler)

    # Start the Bot
    application.run_polling()

if __name__ == '__main__':
    main()


