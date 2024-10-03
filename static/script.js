document.addEventListener('DOMContentLoaded', function() {
    function showLoading() {
        document.getElementById('loading').style.display = 'flex';
    }

    function hideLoading() {
        document.getElementById('loading').style.display = 'none';
    }

    function updateSelectedTimezoneDisplay(timezone) {
        if (!timezone) {
            console.error("Timezone is undefined or null");
            return;
        }
        const friendlyName = timezone.split('/').pop().replace('_', ' ');
        const currentTime = moment().tz(timezone).format('HH:mm');
        document.getElementById('selected-timezone').textContent = `${friendlyName} (Current Time: ${currentTime})`;
        selectedTimezoneElement.dataset.timezone = timezone; // Armazena a timezone completa para uso posterior
    }

    let selectedTime = null;
    let selectedDate = null;
    let selectedTimezone = moment.tz.guess();
    
    // const selectedTimezone = moment.tz.guess();  
    const today = new Date().toISOString().split('T')[0];

    const timezones = {
        "Africa": ["Africa/Cairo", "Africa/Johannesburg"],
        "America": ["America/New_York", "America/Los_Angeles", "America/Sao_Paulo"],
        "Asia": ["Asia/Tokyo", "Asia/Shanghai"],
        "Europe": ["Europe/London", "Europe/Berlin", "Europe/Paris"],
        "Oceania": ["Australia/Sydney", "Pacific/Auckland"]
    };

    const timezoneSelectContainer = document.getElementById('timezone-select-container');
    const timezoneSelectHeader = timezoneSelectContainer.querySelector('.custom-select-header');
    const timezoneDropdown = timezoneSelectContainer.querySelector('.custom-select-dropdown');
    const selectedTimezoneElement = document.getElementById('selected-timezone');
    const timezoneSearchInput = document.getElementById('timezone-search');
    const timezoneOptionsContainer = document.getElementById('timezone-options');

    const timeFormatToggle = document.querySelector('input[name="time-format"]:checked');
    let is24HourFormat = timeFormatToggle.value === '24h';

    function populateTimezones(filter = '') {
        timezoneOptionsContainer.innerHTML = '';
        let timezoneSelected = false;
        const is24Hour = is24HourFormat;

        for (let continent in timezones) {
            if (timezones.hasOwnProperty(continent)) {
                const filteredTimezones = timezones[continent].filter(tz => tz.toLowerCase().includes(filter.toLowerCase()));
                if (filteredTimezones.length > 0) {
                    const continentElement = document.createElement('div');
                    continentElement.className = 'continent';
                    continentElement.textContent = continent.toUpperCase();
                    timezoneOptionsContainer.appendChild(continentElement);

                    filteredTimezones.forEach(tz => {
                        const optionElement = document.createElement('div');
                        optionElement.className = 'timezone';
                        const friendlyName = tz.split('/').pop().replace('_', ' ');
                        const timeFormat = is24Hour ? 'HH:mm' : 'hh:mm A';
                        const currentTime = moment().tz(tz).format(timeFormat);

                        optionElement.innerHTML = `<span>${friendlyName}</span><span style="float:right;">${currentTime}</span>`;
                        optionElement.dataset.timezone = tz; // Salva o nome completo da timezone

                        if (!filter && tz === selectedTimezone) {
                            updateSelectedTimezoneDisplay(tz);
                            timezoneSelected = true;
                            optionElement.classList.add('selected'); // Marca como selecionado
                        }

                        optionElement.addEventListener('click', function() {
                            // Remova a classe 'selected' de todas as opções
                            document.querySelectorAll('.timezone').forEach(el => el.classList.remove('selected'));
                            // Adiciona a classe 'selected' à opção clicada
                            optionElement.classList.add('selected');
                            selectedTimezone = tz;
                            updateSelectedTimezoneDisplay(tz);
                            timezoneDropdown.classList.remove('open');
                            
                            // Atualiza os horários imediatamente ao selecionar uma nova timezone
                            if (selectedDate) {
                                updateAvailableTimes(selectedDate, tz, getSelectedDuration());
                            }
                        });
                        timezoneOptionsContainer.appendChild(optionElement);
                    });
                }
            }
        }

        if (!timezoneSelected && filter === '') {
            const firstTimezone = timezoneOptionsContainer.querySelector('.timezone');
            if (firstTimezone) {
                firstTimezone.classList.add('selected');
                selectedTimezone = firstTimezone.dataset.timezone;
                updateSelectedTimezoneDisplay(firstTimezone.dataset.timezone);
            }
        }
    }

    timezoneSelectHeader.addEventListener('click', function() {
        timezoneDropdown.classList.toggle('open');
    });

    timezoneSearchInput.addEventListener('input', function() {
        populateTimezones(this.value);
    });

    document.querySelectorAll('input[name="time-format"]').forEach((input) => {
        input.addEventListener('change', function() {
            is24HourFormat = this.value === '24h';
            // const currentTimezone = getSelectedTimezone();
            populateTimezones();
            updateSelectedTimezoneDisplay(currentTimezone);

            if (selectedDate) {
                updateAvailableTimes(selectedDate, currentTimezone, getSelectedDuration());
            }
        });
    });

    document.addEventListener('click', function(event) {
        if (!timezoneSelectContainer.contains(event.target)) {
            timezoneDropdown.classList.remove('open');
        }
    });

    populateTimezones();
    updateSelectedTimezoneDisplay(selectedTimezone); // Corrigir para selectedTimezone no carregamento

    function getSelectedTimezone() {
        return selectedTimezone;
    }

    function getSelectedDuration() {
        return parseFloat(document.getElementById('duration').value);
    }

    function getApiRoute() {
        // Detecta a página atual
        const currentPath = window.location.pathname;
        
        if (currentPath.includes('scheduler_1')) {
            return '/api/free_times_1';
        } else if (currentPath.includes('scheduler_2')) {
            return '/api/free_times_2';
        } else {
            console.error('Unknown scheduler page');
            return null;
        }
    }

    function updateAvailableTimes(dateStr, timezone, meetingTime) {
        showLoading();

        const apiRoute = getApiRoute(); // Obtenha a rota de API com base na página

        if (!apiRoute) {
            console.error('API route is not defined');
            return;
        }

        const year = dateStr.split('-')[0];
        const month = dateStr.split('-')[1];

        const startDate = `${year}-${month}-01`;
        const endDate = `${year}-${month}-${new Date(year, month, 0).getDate()}`;

        fetch(`${apiRoute}/${dateStr}?timezone=${encodeURIComponent(timezone)}&meeting_time=${encodeURIComponent(meetingTime)}&start_date=${startDate}&end_date=${endDate}`)
            .then(response => response.json())
            .then(times => {
                const timesContainer = document.getElementById("time-slots");
                timesContainer.innerHTML = "";

                const messageContainer = document.getElementById("message");
                messageContainer.style.display = "none";

                if (times.length === 0) {
                    messageContainer.textContent = 'There are no available times for the selected day.';
                    messageContainer.className = 'error';
                    messageContainer.style.display = 'block';
                    return;
                }

                const timeFormat = is24HourFormat ? 'HH:mm' : 'hh:mm A';

                times.forEach(time => {
                    const timeSlot = document.createElement("div");
                    timeSlot.className = "time-slot";
                    timeSlot.textContent = moment.tz(time.start, timezone).format(timeFormat);
                    
                    timeSlot.addEventListener("click", function() {
                        document.querySelectorAll(".time-slot").forEach(slot => {
                            slot.classList.remove("selected");
                        });
                        timeSlot.classList.add("selected");
                        selectedTime = time.start;


                        const schedulerType = window.location.pathname.includes('scheduler_1') ? '1' : '2';
                        const timeFormatParam = is24HourFormat ? '24h' : 'ampm';
                        window.location.href = `/form.html?scheduler=${schedulerType}&date=${dateStr}&time=${selectedTime}&timezone=${encodeURIComponent(timezone)}&duration=${getSelectedDuration()}&format=${timeFormatParam}`;
                    });
                    timesContainer.appendChild(timeSlot);
                });
            })
            .catch(error => {
                const messageContainer = document.getElementById('message');
                messageContainer.textContent = 'Error fetching available times. Please try again.';
                messageContainer.className = 'error';
                messageContainer.style.display = 'block';
            })
            .finally(() => {
                hideLoading();
            });
    }

    showLoading();
    fetch(`/api/available_dates?timezone=${encodeURIComponent(getSelectedTimezone())}&meeting_time=${encodeURIComponent(getSelectedDuration())}`)
        .then(response => response.json())
        .then(availableDates => {
            const calendar = flatpickr("#calendar", {
                inline: true,
                dateFormat: "Y-m-d",
                disable: [
                    function(date) {
                        const dateStr = date.toISOString().split('T')[0];
                        return !availableDates.includes(dateStr);
                    }
                ],
                onDayCreate: function(dObj, dStr, fp, dayElem) {
                    if (dayElem.dateObj.toISOString().split('T')[0] === today) {
                        dayElem.classList.add('today');
                    }
                },
                onChange: function(selectedDates, dateStr, instance) {
                    selectedDate = dateStr;
                    updateAvailableTimes(dateStr, getSelectedTimezone(), getSelectedDuration());
                }
            });
        })
        .catch(error => {
            const messageContainer = document.getElementById('message');
            messageContainer.textContent = 'Error fetching available dates. Please try again.';
            messageContainer.className = 'error';
            messageContainer.style.display = 'block';
        })
        .finally(() => {
            hideLoading();
        });

    timezoneSelectContainer.addEventListener('change', function() {
        if (selectedDate) {
            updateAvailableTimes(selectedDate, getSelectedTimezone(), getSelectedDuration());
        }
    });

    document.getElementById('duration').addEventListener('change', function() {
        if (selectedDate) {
            updateAvailableTimes(selectedDate, getSelectedTimezone(), getSelectedDuration());
        }
    });
});
