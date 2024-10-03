document.addEventListener('DOMContentLoaded', function() {
    const urlParams = new URLSearchParams(window.location.search);
    const date = urlParams.get('date');
    const time = urlParams.get('time');
    const timezone = urlParams.get('timezone');
    const duration = urlParams.get('duration');
    const format = urlParams.get('format') || '24h'; // Use '24h' como padrão se format for null

    // Se os parâmetros estão corretos, prossiga com a formatação e exibição
    if (date && time && timezone && duration) {
        const duration_in_minutes = duration * 60;
        const dateTimeString = `${time}:00`;

        const startDateTime = moment.tz(dateTimeString, timezone);
        const endDateTime = startDateTime.clone().add(duration_in_minutes, 'minutes');

        const timeFormat = format === '24h' ? 'HH:mm' : 'h:mm A';

        const formattedStartTime = startDateTime.format(timeFormat);
        const formattedEndTime = endDateTime.format(timeFormat);
        // Formata a data para exibir o dia da semana, dia, mês e ano
        const formattedDate = startDateTime.format('dddd, MMM, DD, YYYY');

        const formattedTimezone = timezone.replace('_', ' ').split('/').pop() + ' Time';

        document.getElementById('confirmation-date').textContent = `${formattedDate}`;
        document.getElementById('confirmation-time').textContent = `${formattedStartTime} - ${formattedEndTime}`;
        document.getElementById('confirmation-timezone').textContent = `${formattedTimezone}`;
    } else {
        console.error('Parâmetros faltando ou incorretos na URL.');
    }
});
