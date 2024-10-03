from flask import Flask, render_template, request, jsonify, send_from_directory, session, redirect, url_for
from auth import GoogleCalendarAuth
from calendar_service import GoogleCalendarService
from zoom_service import create_zoom_meeting, get_zoom_authorization_url, get_zoom_tokens, save_tokens, get_access_token, load_tokens

import datetime
import pytz
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Gera uma chave secreta aleatória

# Autenticação do Google Calendar
auth1 = GoogleCalendarAuth(credentials_file='credentials1.json')
creds1 = auth1.authenticate(token_file='token1.json')

auth2 = GoogleCalendarAuth(credentials_file='credentials2.json')
creds2 = auth2.authenticate(token_file='token2.json')

creds_list = [creds1, creds2]  # Lista de credenciais

# Definindo os IDs dos calendários diretamente
calendar_ids = {'calendar_1': 0, 'calendar_2': 1}  # Substitua pelos IDs dos calendários

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/scheduler_1')
def scheduler_1():
    if not load_tokens('scheduler_1'):
        return redirect(url_for('login_scheduler', scheduler_type='scheduler_1'))
    return render_template('index.html', scheduler_type='scheduler_1')

@app.route('/scheduler_2')
def scheduler_2():
    if not load_tokens('scheduler_2'):
        return redirect(url_for('login_scheduler', scheduler_type='scheduler_2'))
    return render_template('index.html', scheduler_type='scheduler_2')

@app.route('/login/<scheduler_type>')
def login_scheduler(scheduler_type):
    session['scheduler_type'] = scheduler_type
    
    if scheduler_type == 'scheduler_1':
        client_id = '' # Substituir por .env
        redirect_uri = 'http://localhost:5000/callback_1'
    elif scheduler_type == 'scheduler_2':
        client_id = '' # Substituir por .env
        redirect_uri = 'http://localhost:5000/callback_2'
    else:
        return "Invalid scheduler type", 400
    
    return redirect(get_zoom_authorization_url(scheduler_type, client_id, redirect_uri))


@app.route('/callback_1')
def callback_1():
    return handle_zoom_callback('scheduler_1')

@app.route('/callback_2')
def callback_2():
    return handle_zoom_callback('scheduler_2')

def handle_zoom_callback(scheduler_type):
    code = request.args.get('code')

    if not code:
        return "Error: No code provided in the callback URL."

    try:
        client_id, client_secret, redirect_uri = get_zoom_credentials(scheduler_type)
        tokens = get_zoom_tokens(code, client_id, client_secret, redirect_uri, scheduler_type)
        save_tokens(tokens, scheduler_type)
        return redirect(url_for(f'scheduler_{scheduler_type.split("_")[-1]}'))
    except Exception as e:
        return str(e)

def get_zoom_credentials(scheduler_type):
    if scheduler_type == 'scheduler_1':
        return ('api', 'key', 'http://localhost:5000/callback_1')
    elif scheduler_type == 'scheduler_2':
        return ('api', 'key', 'http://localhost:5000/callback_2')
    else:
        raise ValueError("Invalid scheduler type")


@app.route('/api/available_dates')
def api_available_dates():
    timezone = request.args.get('timezone', 'UTC')
    meeting_time = float(request.args.get('meeting_time', 1))
    calendar_service = GoogleCalendarService(creds_list, timezone=timezone, slot_time=0.25, meeting_time=meeting_time, buffer=0.25, days=30, initial_buffer=3)
    free_times = calendar_service.get_free_times()
    dates = set([time['start'][:10] for time in free_times])
    return jsonify(sorted(dates))


@app.route('/api/free_times_1/<date>')
def api_free_times_1(date):
    timezone = request.args.get('timezone', 'UTC')
    meeting_time = float(request.args.get('meeting_time', 1))
    calendar_service = GoogleCalendarService(creds_list, timezone=timezone, slot_time=0.25, meeting_time=meeting_time, buffer=0.25, days=30, initial_buffer=3)
    free_times = calendar_service.get_free_times()
    times = [time for time in free_times if time['start'].startswith(date)]
    return jsonify(times)

@app.route('/api/free_times_2/<date>')
def api_free_times_2(date):
    timezone = request.args.get('timezone', 'UTC')
    meeting_time = float(request.args.get('meeting_time', 1))
    calendar_service = GoogleCalendarService(creds_list, timezone=timezone, slot_time=0.25, meeting_time=meeting_time, buffer=0.25, days=30, initial_buffer=3)
    free_times = calendar_service.get_free_times()
    times = [time for time in free_times if time['start'].startswith(date)]
    return jsonify(times)



@app.route('/api/create_event_1', methods=['POST'])
def api_create_event_1():
    return create_event_handler(calendar_ids['calendar_1'])

@app.route('/api/create_event_2', methods=['POST'])
def api_create_event_2():
    return create_event_handler(calendar_ids['calendar_2'])


def create_event_handler(calendar_id):
    try:
        if calendar_id == 0:
            scheduler_type = 'scheduler_1'
        else:
            scheduler_type = 'scheduler_2'

        if not get_access_token(scheduler_type):
            return redirect(get_zoom_authorization_url(scheduler_type))

        data = request.get_json()
        print(f"Data received: {data}")

        start_time_str = data.get('time')
        timezone = data.get('timezone', 'UTC')
        duration = float(data.get('duration'))
        
        email = data.get('email')
        guests_emails = data.get('guests_emails', [])
        name = data.get('name', 'Anonymous')
        notes = data.get('notes', '')



        # Cria uma reunião no Zoom
        zoom_link = create_zoom_meeting(scheduler_type, topic=f"Chat Giulia / {name}")
        if not zoom_link:
            return jsonify({'status': 'error', 'message': 'Erro ao criar a reunião no Zoom.'}), 500

        # Adiciona o link do Zoom na descrição do evento
        description = f"{notes}\n\nZoom Meeting Link: {zoom_link}"

        attendees = [{'email': email}]
        if guests_emails:
            for emails_str in guests_emails:
                additional_attendees = [{'email': e.strip()} for e in emails_str.split(',')]
                attendees.extend(additional_attendees)
        
        calendar_service = GoogleCalendarService(creds_list, timezone=timezone, slot_time=0.25, meeting_time=duration, buffer=0.25, days=30, initial_buffer=3)

        # Converte o horário para o fuso do Brasil
        start_time_str = calendar_service.convert_to_brazil_timezone(start_time_str, timezone)
        start_time_dt = datetime.datetime.fromisoformat(start_time_str)
        end_time_dt = start_time_dt + datetime.timedelta(hours=duration)
        end_time_str = end_time_dt.isoformat()

        event = calendar_service.create_event(
            start_time_str=start_time_str,
            end_time_str=end_time_str,
            calendar_id=calendar_id,
            summary=f'Chat Giulia / {name}',
            description=description,
            location='Zoom',
            attendees=attendees
        )

        if event:
            return jsonify({'status': 'success', 'event_link': event.get('htmlLink')})
        else:
            return jsonify({'status': 'error'}), 500
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500



@app.route('/form.html')
def form():
    return send_from_directory('templates', 'form.html')

    
@app.route('/confirmation.html')
def confirmation():
    event_date = session.get('event_date')
    event_time = session.get('event_time')
    event_timezone = session.get('event_timezone')
    
    return render_template('confirmation.html', date=event_date, time=event_time, timezone=event_timezone)

if __name__ == '__main__':
    app.run(debug=True)
