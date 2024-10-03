import datetime
import pytz
from dateutil import parser
from googleapiclient.discovery import build


class GoogleCalendarService:
    def __init__(self, creds_list, timezone, slot_time, meeting_time, buffer, days, initial_buffer):
        # Inicializa o serviço do Google Calendar com as credenciais fornecidas
        self.creds_list = creds_list
        self.timezone = timezone  # Fuso horário para converter os horários
        self.slot_time = slot_time # Duração do intervalo de tempo livre (em horas)
        self.meeting_time = meeting_time  # Duração da reunião (em horas)
        self.buffer = buffer  # Duração do buffer (em horas)
        self.days = days  # Número de dias para verificar os horários livres
        self.initial_buffer = initial_buffer  # Duração do buffer inicial (em horas)

    def get_service(self, creds):
        return build('calendar', 'v3', credentials=creds)
    
    def get_now_and_end_time(self):
        # Obtém o tempo atual em UTC e calcula o tempo final (daqui a 'days' dias)
        now_utc = (datetime.datetime.utcnow() + datetime.timedelta(hours=self.initial_buffer)).replace(microsecond=0)
        end_time_utc = now_utc + datetime.timedelta(days=self.days)

        # Converte os tempos para o formato ISO 8601 com 'Z' indicando UTC
        now = now_utc.isoformat() + 'Z'
        end_time = end_time_utc.isoformat() + 'Z'
        return now, end_time
    
    def get_calendar(self, service):
        now, end_time = self.get_now_and_end_time()

        # Ele procura os eventos ocupados, se não tiver nenhum evento, ele retorna vazio
        # Adicionar um parametro de data para pegar os horários livres de um dia específico
        # Corpo da solicitação para a API de freebusy do Google Calendar
        body = {
            "timeMin": now,
            "timeMax": end_time,
            "timeZone": 'UTC',
            "items": [{"id": 'primary'}]
        }

        try:
            # Executa a solicitação para obter os horários ocupados
            events_result = service.freebusy().query(body=body).execute()
            event_times = events_result['calendars']['primary']['busy']
            return event_times
        except Exception as e:
            print(f"Error fetching event times: {e}")
            return []

    def get_free_times(self):
        now, end_time = self.get_now_and_end_time()
        
        service1 = self.get_service(self.creds_list[0])
        service2 = self.get_service(self.creds_list[1])

        events1 = self.get_calendar(service1)
        events2 = self.get_calendar(service2)

        events = events1 + events2

        # Ordena os eventos por horário de início
        events.sort(key=lambda x: x['start'])

        # Calcula os horários livres com base nos horários ocupados
        free_times = self.calculate_free_times(now, end_time, events)
        timezone_selected = pytz.timezone(self.timezone)
        # Divide os horários livres em intervalos horários
        hourly_free_times = self.split_into_hourly_slots(free_times, timezone_selected)

        return hourly_free_times

    def calculate_free_times(self, now, end_time, event_times):
        print("\n=========================================================\n")

        free_times = []
        current_time = now
        current_time_dt = datetime.datetime.strptime(current_time, '%Y-%m-%dT%H:%M:%SZ')
        end_time_dt = datetime.datetime.strptime(end_time, '%Y-%m-%dT%H:%M:%SZ')

        meeting_time_delta = datetime.timedelta(hours=self.meeting_time)
        buffer_delta = datetime.timedelta(hours=self.buffer)

        for i in range(len(event_times)):
            event_start = datetime.datetime.strptime(event_times[i]['start'], '%Y-%m-%dT%H:%M:%SZ')
            event_end = datetime.datetime.strptime(event_times[i]['end'], '%Y-%m-%dT%H:%M:%SZ')
            
            # Antes do primeiro evento ocupado
            # Se o horário de início do evento for maior que o horário atual + o buffer
            if i == 0 and event_start > current_time_dt + buffer_delta:
                # Available start é o horário atual
                available_start = current_time_dt
                # Available end é o horário de início do prox evento - o buffer
                available_end = event_start - buffer_delta
                # Se a diferença entre o horário de início e fim for maior ou igual a duração da reunião
                if available_end - available_start >= meeting_time_delta:
                    # Adiciona o horário inicio: horário atual e fim: horário de início do evento - buffer
                    free_times.append({"start": available_start.isoformat() + 'Z', "end": available_end.isoformat() + 'Z'})

            # Entre eventos ocupados
            if i > 0:
                last_event_end = datetime.datetime.strptime(
                    event_times[i-1]['end'], '%Y-%m-%dT%H:%M:%SZ')
                # Available start é o horário de fim do último evento + buffer
                available_start = last_event_end + buffer_delta
                # Available end é o horário de início do evento - buffer
                available_end = event_start - buffer_delta
                if available_end - available_start >= meeting_time_delta:
                    # Adiciona o horário inicio: horário de fim do último evento + buffer e fim: horário de início do evento - buffer
                    free_times.append({"start": available_start.isoformat() + 'Z', "end": available_end.isoformat() + 'Z'})

            # Após o último evento ocupado
            if i == len(event_times) - 1 and event_end + buffer_delta < end_time_dt:
                available_start = event_end + buffer_delta
                available_end = end_time_dt
                if available_end - available_start >= meeting_time_delta:
                    free_times.append({"start": available_start.isoformat() + 'Z', "end": available_end.isoformat() + 'Z'})

        return free_times

    def split_into_hourly_slots(self, free_times, timezone):
        # Divide os horários livres em intervalos horários
        hourly_slots = []
        meeting_time_delta = datetime.timedelta(hours=self.meeting_time)
        buffer_delta = datetime.timedelta(hours=self.buffer)

        for time in free_times:
            start_utc = datetime.datetime.fromisoformat(time['start'].replace('Z', '+00:00'))
            end_utc = datetime.datetime.fromisoformat(time['end'].replace('Z', '+00:00'))

            # Converte os horários de UTC para o fuso horário especificado
            start_timezone = start_utc.astimezone(timezone)
            end_timezone = end_utc.astimezone(timezone)

            # Ajusta o início para o próximo intervalo de 15 minutos
            start_timezone = self.round_to_next_slot(start_timezone)

            current = start_timezone
            # Divide o intervalo livre em slots horários
            # explicando o while: enquanto o horário atual (current) + a duração do slot (slot_time) for menor que o horário final (end_timezone) - a duração da reunião (meeting_time_delta) - o buffer (buffer_delta)
            while current + datetime.timedelta(hours=self.slot_time) <= end_timezone - meeting_time_delta + buffer_delta:
                # end_slot = horário atual + duração do slot
                end_slot = current + datetime.timedelta(hours=self.slot_time)
                # Adiciona o slot à lista de horários
                hourly_slots.append({"start": current.strftime('%Y-%m-%d %H:%M'),
                                     "end": end_slot.strftime('%Y-%m-%d %H:%M')})
                # Atualiza o horário atual para o final do slot
                current = end_slot

        return hourly_slots

    def round_to_next_slot(self, dt):
        # Arredonda o horário para o próximo intervalo de 15 minutos
        if dt.minute > 0 and dt.minute < 15:
            dt = dt.replace(minute=15, second=0, microsecond=0)
        elif dt.minute > 15 and dt.minute < 30:
            dt = dt.replace(minute=30, second=0, microsecond=0)
        elif dt.minute > 30 and dt.minute < 45:
            dt = dt.replace(minute=45, second=0, microsecond=0)
        elif dt.minute > 45:
            dt = dt.replace(minute=0, second=0, microsecond=0) + \
                datetime.timedelta(hours=1)
        return dt

    def convert_to_brazil_timezone(self, datetime_str, user_timezone_str):
        horario_sem_tz = datetime.datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")

        fuso_horario_user = pytz.timezone(user_timezone_str)
        horario_user = fuso_horario_user.localize(horario_sem_tz)

        fuso_horario_brasil = pytz.timezone("America/Sao_Paulo")
        horario_brasil = horario_user.astimezone(fuso_horario_brasil)

        # Retorna a data e hora no formato ISO 8601
        return horario_brasil.isoformat()


    def create_event(self, start_time_str, end_time_str, calendar_id, summary='New Event', description='', location='', attendees=None):
        # Cria um evento no Google Calendar com os detalhes fornecidos
        event = {
            'summary': summary,
            'location': location,
            'description': description,
            'start': {
                'dateTime': start_time_str,
                'timeZone': self.timezone,
            },
            'end': {
                'dateTime': end_time_str,
                'timeZone': self.timezone,
            },
            'attendees': attendees if attendees else [],
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},
                    {'method': 'popup', 'minutes': 10},
                ],
            },
        }

        try:
            # Executa a solicitação para criar o evento
            service = self.get_service(self.creds_list[calendar_id])
            event = service.events().insert(calendarId='primary', body=event).execute()
            print(f'Event created: {event.get("htmlLink")}')
            return event
        except Exception as e:
            print(f'An error occurred: {e}')
            return None
