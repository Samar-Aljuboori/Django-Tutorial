
# Planify - Modern Task Management & Productivity Application

**Planify** is a sleek, feature-rich web application built with **Django** designed to help users organize daily priorities, track deadlines, manage custom task categories, and visualize schedules seamlessly.

---

##  Features & Highlights

- **Interactive Dashboard:** Summary metrics displaying total, completed, and pending tasks, along with quick-add forms and advanced filtering.
- **Task & Category Management:** Create, update, and categorize tasks with set priorities (Low, Medium, High) and custom categories.
- **Interactive Calendar View:** Full monthly calendar integration to schedule, view, and update tasks and appointments interactively.
- **Account & Customization Settings:** Profile management with custom avatar photo uploads, theme toggling (Dark & Light Mode), and custom theme colors.

##  Tech Stack

- **Backend:** Python, Django
- **Frontend:** HTML5, CSS3, JavaScript, FontAwesome Icons
- **Database:** SQLite
- **Image Processing:** Pillow (`PIL`)

##  Set up a virtual environment:


python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

##  Install dependencies:

pip install Django Pillow



## Apply database migrations:

python manage.py makemigrations
python manage.py migrate


##  Run the development server:

python manage.py runserver