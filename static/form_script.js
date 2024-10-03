document.addEventListener('DOMContentLoaded', function() {
    const urlParams = new URLSearchParams(window.location.search);
    const date = urlParams.get('date');
    const time = urlParams.get('time'); 
    const timezone = urlParams.get('timezone');
    const duration = urlParams.get('duration');
    const format = urlParams.get('format');
    const schedulerType = urlParams.get('scheduler');

    // Converte a duração para minutos
    duration_in_minutes = duration * 60; 

    const dateTimeString = `${time}:00`;

    // Atualiza os campos escondidos com os valores dos parâmetros
    if (date) document.getElementById('selected-date').value = date;
    if (time) document.getElementById('selected-time').value = time;
    if (timezone) document.getElementById('timezone').value = timezone;
    if (duration) document.getElementById('duration').value = duration;

    const eventTimezoneElement = document.getElementById('event-timezone');
    const meetingDurationElement = document.getElementById('meeting-duration');


    if (date && duration_in_minutes) {
        const startDateTime = moment.tz(dateTimeString, timezone);
        const endDateTime = startDateTime.clone().add(duration_in_minutes, 'minutes');

        const timeFormat = format === '24h' ? 'HH:mm' : 'h:mm A';

        const formattedStartTime = startDateTime.format(timeFormat);
        const formattedEndTime = endDateTime.format(timeFormat);
        const formattedDate = startDateTime.format('dddd, MMMM do YYYY');

        const hourElement = document.getElementById('hour');
        const dateElement = document.getElementById('date');

        hourElement.textContent = `${formattedStartTime} - ${formattedEndTime}`;
        dateElement.textContent = formattedDate;

        const timezoneElement = document.getElementById('event-timezone');
        if (timezoneElement) {
            timezoneElement.textContent = timezone;
        }

      
    } else {
        console.error('Error: Invalid date or time.');
    }

    if (eventTimezoneElement && timezone) {
        const formattedTimezone = timezone.replace('_', ' ').split('/').pop() + ' Time';
        eventTimezoneElement.textContent = formattedTimezone;
    }

    if (meetingDurationElement && duration_in_minutes) {
        meetingDurationElement.textContent = duration_in_minutes; // Atualiza o valor dentro do span para refletir a duração correta
    }

    // Função para adicionar novas caixas de texto de convidados
    document.getElementById('add-guest-button').addEventListener('click', function() {
        const container = document.getElementById('guests-emails-container');
        const instruction = document.querySelector('.instruction');

        // Cria a nova caixa de texto para adicionar emails
        const newInput = document.createElement('div');
        newInput.classList.add('form-group');
        newInput.innerHTML = `
            <label for="guests-emails">Guests emails*</label>
            <input type="text" name="guests_emails[]" placeholder="Ex: guest1@example.com, guest2@example.com">
        `;
        container.appendChild(newInput);

        // Exibe a instrução para separar os emails por virgua
        instruction.style.display = 'block';

        this.style.display = 'none'; // Esconde o botão de adicionar convidados
    });

    document.getElementById('booking-form').addEventListener('submit', function(event) {
        event.preventDefault();
    
        const formData = new FormData(this);
        const jsonData = {};
        formData.forEach((value, key) => {
            if (key === 'email') {
                jsonData[key] = value;
            } else if (key === 'guests_emails[]') {
                if (!jsonData['guests_emails']) {
                    jsonData['guests_emails'] = [];
                }
                jsonData['guests_emails'].push(value);
            } else {
                jsonData[key] = value;
            }
        });

        const createEventUrl = schedulerType === '1' ? '/api/create_event_1' : '/api/create_event_2';
        console.log('Create Event URL:', createEventUrl);
    
        fetch(createEventUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(jsonData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                const date = jsonData['date']; // Captura a data do form
                const time = jsonData['time']; // Captura a hora do form
                const timezone = jsonData['timezone']; // Captura a timezone do form
                const duration = jsonData['duration']; // Captura a duração do form
                const format = new URLSearchParams(window.location.search).get('format'); // Captura o formato da URL

                // Log para depuração
                console.log("Format:", format); // Adiciona este log para garantir que format está correto
    
                // Redireciona para confirmation.html com os parâmetros
                const confirmationUrl = `/confirmation.html?date=${encodeURIComponent(date)}&time=${encodeURIComponent(time)}&timezone=${encodeURIComponent(timezone)}&duration=${encodeURIComponent(duration)}&format=${encodeURIComponent(format)}`;
                window.location.href = confirmationUrl;

            } else {
                const message = document.getElementById('message');
                message.textContent = 'Error creating the event. Please try again.';
                message.className = 'error';
                message.style.display = 'block';
            }
        })
        .catch(error => {
            const message = document.getElementById('message');
            message.textContent = 'Error creating the event. Please try again.';
            message.className = 'error';
            message.style.display = 'block';
        });
    });
});
