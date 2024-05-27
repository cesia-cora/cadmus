![Static Badge](https://img.shields.io/badge/Django-5.0.4-%23?labelColor=black&style=for-the-badge&logo=django&color=%233C7782)
![Static Badge](https://img.shields.io/badge/djangockeditor-6.7.1-%23?labelColor=black&style=for-the-badge&color=%23c55e73)
![Static Badge](https://img.shields.io/badge/reportlab-4.1.0-%23?labelColor=black&style=for-the-badge&color=%234e6041)

## CADMUS | PERSONAL DIARY PROJECT
Cadmus is a web application made to publish and view your entries, like a personal diary/journal.

### Features:
- User creation
- Post, view, edit and delete entries
- Filter entries through years and months
- Rich text formatting
- Search bar
- Save entries as PDF
- Cute 3D images from [Ouch!][def3]

### Why "Cadmus"?
Cadmus is the greek god of literature and writing.

### Installation and usage:
`py -m pip install -r requirements.txt`

`py -m manage makemigrations`

`py -m manage migrate`

`py -m manage runserver`

### Create admin user:
`py -m manage createsuperuser`

### Run tests:
`py -m manage test cadmus`

### Components:
- Built with Python framework [Django][def]
- CSS framework [Bulma][def4] for website design
- Default database SQLite3
- Rich text editor with [CKEditor][def2]

[def]: https://www.djangoproject.
[def2]: https://ckeditor.com
[def3]: https://iconos8.es/illustrations
[def4]: https://bulma.io
