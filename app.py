import sys
from io import BytesIO

import telegram
from flask import Flask, request, send_file
from fsm import TocMachine


API_TOKEN = '336497236:AAFdVaWEpud36r-R56sLc1COimj2_0QCYQA'
WEBHOOK_URL = 'https://ebfb9f23.ngrok.io/hook'

app = Flask(__name__)
bot = telegram.Bot(token=API_TOKEN)
machine = TocMachine(
    states=[
        'user',
        'instruction1',
        'instruction2',
        'state1',
	    'news',
        'news_ori',
	    'ask_for_year_season',
        'check_year_season',
        'go_deeper_animainfo1',
        'go_deeper_animainfo2',
        'go_deeper_animback',
        'boyslove',
        'get_BLcomic',
        'teach_boyslove',
        'stillBL',
        'refuseBL',
        'news_commod',
        'news_realmod',
        'news_back',
        'state2'
    ],
    transitions=[
        {
            'trigger': 'advance',
            'source': 'user',
            'dest': 'instruction1'
        },
        {
            'trigger': 'advance',
            'source': 'instruction1',
            'dest': 'state1',
            'conditions': 'is_going_to_state1'
        },
        {
            'trigger': 'advance',
            'source': 'state1',
            'dest': 'ask_for_year_season',
            'conditions': 'is_going_to_ask_for_year_season'
        },
        {
            'trigger': 'advance',
            'source': 'state1',
            'dest': 'news',
            'conditions': 'is_going_to_news'
        },
        {
            'trigger': 'advance',
            'source': 'news',
            'dest': 'news_ori',
            'conditions': 'is_going_to_news_ori'
        },
        {
            'trigger': 'advance',
            'source': 'news',
            'dest': 'news_realmod',
            'conditions': 'is_going_to_news_realmod'
        },
        {
            'trigger': 'advance',
            'source': 'news',
            'dest': 'news_commod',
            'conditions': 'is_going_to_news_commod'
        },
        {
            'trigger': 'advance',
            'source': 'news',
            'dest': 'news_back',
            'conditions': 'is_going_to_news_back'
        },
        {
            'trigger': 'advance',
            'source': 'ask_for_year_season',
            'dest': 'check_year_season',
            'conditions': 'is_going_to_check_year_season'
        },
        {
            'trigger': 'advance',
            'source': 'ask_for_year_season',
            'dest': 'news_back',
            'conditions': 'is_going_to_news_back'
        },
        {
            'trigger': 'advance',
            'source': 'check_year_season',
            'dest': 'go_deeper_animainfo1',
            'conditions': 'is_going_to_go_deeper_animainfo1'
        },
        {
            'trigger': 'advance',
            'source': 'check_year_season',
            'dest': 'go_deeper_animback',
            'conditions': 'is_going_to_go_deeper_animback'
        },
        {
            'trigger': 'advance',
            'source': 'go_deeper_animainfo1',
            'dest': 'go_deeper_animainfo2',
            'conditions': 'is_going_to_go_deeper_animainfo2'
        },
        {
            'trigger': 'advance',
            'source': 'go_deeper_animainfo2',
            'dest': 'go_deeper_animback',
            'conditions': 'is_going_to_go_deeper_animback'
        },
        {
            'trigger': 'advance',
            'source': 'go_deeper_animainfo2',
            'dest': 'go_deeper_animainfo2',
            'conditions': 'is_going_to_go_deeper_animainfo2'
        },
        {
            'trigger': 'advance',
            'source': 'state1',
            'dest': 'boyslove',
            'conditions': 'is_going_to_boyslove'
        },
        {
            'trigger': 'advance',
            'source': 'boyslove',
            'dest': 'get_BLcomic',
            'conditions': 'is_going_to_get_BLcomic'
        },
        {
            'trigger': 'advance',
            'source': 'boyslove',
            'dest': 'teach_boyslove',
            'conditions': 'is_going_to_teach_boyslove'
        },
        {
            'trigger': 'advance',
            'source': 'teach_boyslove',
            'dest': 'stillBL',
            'conditions': 'is_going_to_stillBL'
        },
        {
            'trigger': 'advance',
            'source': 'teach_boyslove',
            'dest': 'refuseBL',
            'conditions': 'is_going_to_refuseBL'
        },
        {
            'trigger': 'advance',
            'source': 'get_BLcomic',
            'dest': 'boyslove',
            'conditions': 'is_going_to_boyslove'
        },
        {
            'trigger': 'go_back',
            'source': 'stillBL',
            'dest': 'get_BLcomic'
        },
        {
            'trigger': 'go_back',
            'source': 'refuseBL',
            'dest': 'state1'
        },
        {
            'trigger': 'go_back',
            'source': 'go_deeper_animainfo1',
            'dest': 'instruction1'
        },
        {
            'trigger': 'go_back',
            'source': 'go_deeper_animback',
            'dest': 'ask_for_year_season'
        },
        {
            'trigger': 'go_back',
            'source': 'news_ori',
            'dest': 'news'
        },
        {
            'trigger': 'go_back',
            'source': 'news_commod',
            'dest': 'news'
        },
        {
            'trigger': 'go_back',
            'source': 'news_realmod',
            'dest': 'news'
        },
        {
            'trigger': 'go_back',
            'source': 'news_back',
            'dest': 'state1'
        }
    ],
    initial='user',
    auto_transitions=False,
    show_conditions=True,
)


def _set_webhook():
    status = bot.set_webhook(WEBHOOK_URL)
    if not status:
        print('Webhook setup failed')
        sys.exit(1)
    else:
        print('Your webhook URL has been set to "{}"'.format(WEBHOOK_URL))

@app.route('/hook', methods=['POST'])
def webhook_handler():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    machine.advance(update)
    return 'ok'


@app.route('/show-fsm', methods=['GET'])
def show_fsm():
    byte_io = BytesIO()
    machine.graph.draw(byte_io, prog='dot', format='png')
    byte_io.seek(0)
    return send_file(byte_io, attachment_filename='fsm.png', mimetype='image/png')


if __name__ == "__main__":
    _set_webhook()
    app.run()
