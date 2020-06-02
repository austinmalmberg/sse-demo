import os
import uuid
import json
from datetime import datetime, timedelta

from flask import Flask, render_template, Response, session, g, stream_with_context


def create_app():
    app = Flask(__name__)

    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev'),
    )

    @app.before_request
    def define_user():
        if session.get('uuid') is None:
            session['uuid'] = str(uuid.uuid4())

        g.uuid = session['uuid']

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/notifications')
    def notifications():
        def construct_message(payload='no message'):
            time = datetime.now()
            message_info = {
                'user': g.uuid,
                'time': f'{time.month}/{time.day}/{time.year} {time.hour:02}:{time.minute:02}:{time.second:02}',
                'payload': payload
            }
            return f'data: {json.dumps(message_info)}\n\n';

        def event_stream():
            now = None
            while True:
                later = datetime.now()
                if now is None or later > now + timedelta(seconds=5):
                    now = later
                    message = construct_message()
                    yield message

        return Response(stream_with_context(event_stream()), mimetype="text/event-stream")

    return app
