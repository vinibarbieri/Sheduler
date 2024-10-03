# ZoomScheduler

ZoomScheduler is a Python Flask application that allows users to schedule meetings in Google Calendar and automatically create Zoom meeting links. The application supports multiple calendars and Zoom accounts, providing a practical solution for managing meetings.

## Features

- **Meeting Scheduling:** Users can select available dates and times from linked calendars to schedule meetings.
- **Zoom Integration:** Automatically creates Zoom meeting links when scheduling an event.
- **Support for Multiple Calendars and Zoom Accounts:** The application allows the use of two different calendars and corresponding Zoom accounts.
- **OAuth Authentication:** Supports authentication with Google Calendar and Zoom using OAuth.

## Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/YourUsername/ZoomScheduler.git
    cd ZoomScheduler
    ```

2. **Create and activate a virtual environment (optional but recommended):**

    ```bash
    python -m venv venv
    source venv/bin/activate  # For Linux/Mac
    venv\Scripts\activate  # For Windows
    ```

3. **Install the dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4. **Set Up Credentials:**

    - **Google Calendar:** Place your `credentials1.json` and `credentials2.json` files in the project's root directory.
    - **Zoom:** Update `zoom_config.json` with your Zoom API credentials.

5. **Run the application:**

    ```bash
    python app.py
    ```

6. **Access in your browser:**

    - Go to [http://localhost:5000](http://localhost:5000) to choose between the two schedulers.

## Usage

1. **Select a Scheduler:** Choose between Scheduler 1 or Scheduler 2 on the home page.
2. **Select a Date and Time:** Browse the calendar and select an available time slot.
3. **Enter Details:** Fill in your name, email, and additional details.
4. **Confirm the Meeting:** After confirmation, an event will be created in Google Calendar, and a Zoom meeting link will be sent via email.

## Contributing

Contributions are welcome! If you'd like to contribute to the project, feel free to fork the repository and submit a pull request.

## License

This project is licensed under the MIT License.
