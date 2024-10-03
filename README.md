# ZoomScheduler 🚀

**ZoomScheduler** is an innovative, Python Flask-powered application that simplifies meeting scheduling by seamlessly integrating Google Calendar and Zoom. This tool streamlines the process of managing meetings by allowing users to select available time slots from multiple calendars and automatically generating Zoom meeting links—saving time and reducing the complexity of scheduling across multiple platforms.

## 🌟 Why ZoomScheduler?

Scheduling meetings can be a tedious task, especially when dealing with multiple calendars and coordinating time zones. **ZoomScheduler** was designed to solve that problem by offering an intuitive, automated solution that links calendars and Zoom accounts effortlessly. It's perfect for professionals, teams, and organizations who want a streamlined way to handle their virtual meetings without jumping between different platforms.

## 🔥 Key Features

- **Multiple Calendar Support**: Easily connect and manage two Google Calendars.
- **Zoom Integration**: Automatically create Zoom meeting links while scheduling events.
- **OAuth Authentication**: Securely authenticate with Google Calendar and Zoom using OAuth 2.0.
- **User-Friendly Interface**: Intuitive UI that allows for fast and efficient meeting setup.
- **Customizable Scheduler**: Choose from two different calendar views and customize meeting times to fit your needs.

## 🛠️ Built With

- **Python** (Flask)
- **Zoom API**
- **Google Calendar API**
- **OAuth 2.0**
- **HTML/CSS** (for UI)
- **JavaScript** (for interactivity)

## 🚀 How It Works

1. **Select a Scheduler**: Choose between Scheduler 1 or Scheduler 2 on the home page.
2. **Select Date and Time**: Pick a time from the available slots in your Google Calendar.
3. **Confirm Details**: Enter participant information and confirm the meeting.
4. **Zoom Integration**: After confirmation, a Zoom link is automatically created and added to your event, which is also synced to your Google Calendar.

## 💡 Installation

Get started with ZoomScheduler by following these simple steps:

1. **Clone the repository**:
    ```bash
    git clone https://github.com/vinibarbieri/ZoomScheduler.git
    cd ZoomScheduler
    ```

2. **Set up a virtual environment** (optional but recommended):
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Linux/Mac
    venv\Scripts\activate  # On Windows
    ```

3. **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4. **Configure your API keys**:
   - Add your Google Calendar API credentials (`credentials1.json` and `credentials2.json`).
   - Configure your Zoom API credentials in `zoom_config.json`.

5. **Run the application**:
    ```bash
    python app.py
    ```

6. **Access the app**:
   Open your browser and go to [http://localhost:5000](http://localhost:5000) to start scheduling meetings.

## 📊 Impact

The **ZoomScheduler** has improved efficiency by cutting down the time spent managing multiple calendars and generating meeting links. It’s particularly useful in:

- Professional settings where scheduling across teams is crucial.
- Remote work environments.
- Educational platforms where multiple class schedules need coordination.

## 💼 Professional Value

**ZoomScheduler** demonstrates expertise in:
- **API Integration**: Mastery in integrating third-party APIs such as Google Calendar and Zoom.
- **OAuth Authentication**: Secure and scalable OAuth 2.0 integration.
- **Flask Framework**: Proficiency in Python Flask for building lightweight, scalable web applications.
- **Full-Stack Development**: Handling both front-end (UI/UX) and back-end (API handling) development.

### 💻 Technologies Used

- **Backend**: Python (Flask), RESTful APIs (Zoom, Google Calendar)
- **Frontend**: HTML, CSS, JavaScript
- **Database**: None (session-based)
- **Security**: OAuth 2.0 for secure authentication

## 🌱 Future Enhancements

1. **Support for More Calendars**: Expand to support more than two Google Calendars.
2. **Time Zone Auto-Detection**: Add automatic time zone detection for cross-region meetings.
3. **Notification System**: Implement email or SMS notifications before the meeting start time.
4. **Integration with Other Meeting Platforms**: Add support for Microsoft Teams or WebEx.

## 👏 Contributions

Contributions are welcome! If you're interested in improving this project or adding new features, feel free to submit a pull request or open an issue.

---

**ZoomScheduler** was created as a demonstration of expertise in API integration, web development, and seamless user experience design. It's a practical tool with a real-world application, showcasing my skills in developing automated solutions that add value to businesses and teams.

## 📫 Let's Connect!

- **Email**: [vinicius190702@hotmail.com](mailto:vinicius190702@hotmail.com)
- **LinkedIn**: [Vinicius Barbieri](https://www.linkedin.com/in/vinibarbieri/)
- **GitHub**: [Vinicius Barbieri](https://github.com/vinibarbieri)

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
