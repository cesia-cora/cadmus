## CADMUS | PERSONAL DIARY PROJECT
Cadmus is a web app made to post and see your entries, as an personal diary/journal.

### Features:
- User creation
- Post, view, edit and delete entries
- Filter entries through years and months
- Rich text formatting
- Cute 3D images from [Ouch!][def3]

### Why "Cadmus"?
Cadmus is the greek god literature and writing.

### Installation and usage:
`pip install -r requirements.txt`

`py manage.py migrate`

`py manage.py runserver`

### Create admin user:
`py manage.py createsuperuser`

If you use Linux or Mac you should type <em>python</em> instead of <em>py</em>

### Components:
- Built with Python framework [Django][def]
- CSS framework [Bulma][def4] for design
- Default database SQLite3
- Rich text editor with [CKEditor][def2]

[def]: https://www.djangoproject.
[def2]: https://ckeditor.com
[def3]: https://iconos8.es/illustrations
[def4]: https://bulma.io