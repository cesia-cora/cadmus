![Static Badge](https://img.shields.io/badge/Django-6.0.1-%23?labelColor=black&style=for-the-badge&logo=django&color=%233C7782)
![Static Badge](https://img.shields.io/badge/CKEditor%205-0.2.19-%23?labelColor=black&style=for-the-badge&color=%23c55e73)
![Static Badge](https://img.shields.io/badge/reportlab-4.4.7-%23?labelColor=black&style=for-the-badge&color=%234e6041)
![Static Badge](https://img.shields.io/badge/cryptography-45.0.6-%23?labelColor=black&style=for-the-badge&color=%23756154)

## CADMUS | PERSONAL DIARY PROJECT
Cadmus is a web application made to publish and view your entries, like a personal diary/journal.

This is a Django project using the Model-Template-View architectural pattern.
<br>The Model handles the business logic and interaction with the database.
<br>The Template handles the presentation layer.
<br>The View handles the logic of what data to display.

### Features:
- User authentication system
- Post, view, edit and delete entries
- Encrypted entries (end-to-end)
- Calendar integration
- Filter entries by date
- Rich text formatting
- Search bar
- Convert to and download entries as PDF
- Cute 3D images from [Ouch!][def3]

### Requirements:
- Python 3.x
- pip
- Dependencies installation

### Why "Cadmus"?
Cadmus is the greek god of literature and writing.

### Quickstart
#### Win 10

1. Clone repository

2. Create and activate a virtual environment in the main folder (diary-env)

Type this command in the terminal

<pre>py -m pip install virtualenv</pre>

3. Activate your environment

<pre>venv\Scripts\activate</pre>

4. Install required packages

<pre>py -m pip install -r requirements.txt</pre>

4. Apply database models

<pre>py -m manage makemigrations</pre>

<pre>py -m manage migrate</pre>

5. Generate a random key on the terminal

<pre>python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"</pre>

6. Create an .env file in the main folder with the following

<pre>SECRET_KEY='paste your random secret key here'</pre>

7. Generate an encryption key on the terminal

<pre>python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"</pre>

8. On the .env file type

<pre>ENCRYPTION_KEY='your encryption key'</pre>

9. Create superuser (optional)
<pre>py -m manage createsuperuser</pre>

Choose an username and a password. 

10. Run the server

<pre>py -m manage runserver</pre>

11. Go to 127.0.0.1/admin to view your database interface.

### Run tests (optional):
<pre>py -m manage test cadmus</pre>

### Components:
- Built with Python framework [Django][def]
- CSS framework [Bulma][def4] for website design
- Default database SQLite3
- Rich text editor with [CKEditor][def2]

[def]: https://www.djangoproject.
[def2]: https://ckeditor.com
[def3]: https://iconos8.es/illustrations
[def4]: https://bulma.io

This project was built using the [Django official documentation][def5] and [Fernet methods for field encryption][def6].

[def5]: https://docs.djangoproject.com/en/6.0/
[def6]: https://cryptography.io/en/latest/fernet/