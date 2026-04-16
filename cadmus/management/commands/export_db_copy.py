from datetime import datetime
from django.core.management.base import BaseCommand
from django.conf import settings
from pathlib import Path
import os
import sqlite3
import tempfile
import socket

def _dest_path(sync_dir):
    host = socket.gethostname().replace(" ", "_")
    ts = datetime.now().strftime("%Y%m%d%H%M%S")
    return os.path.join(sync_dir, f"db_copy-{host}-{ts}.sqlite3")

class Command(BaseCommand):
    help = "Export a consistent copy of the default sqlite DB into a Syncthing folder"

    def add_arguments(self, parser):
        parser.add_argument('--sync-dir', default=None, help='Folder that Syncthing syncs (default: <project>/diary_sync)')

    def handle(self, *args, **options):
        src = settings.DATABASES['default']['NAME']

        base_dir = getattr(settings, "BASE_DIR", None)
        if base_dir is None:
            base_dir = Path(__file__).resolve().parents[3]
        else:
            base_dir = Path(base_dir)

        if options['sync_dir']:
            sync_dir = Path(options['sync_dir'])
        else:
            sync_dir = base_dir / 'diary_sync'
            
        os.makedirs(sync_dir, exist_ok=True)
        dest = _dest_path(sync_dir)

        fd, tmp_path = tempfile.mkstemp(dir=sync_dir, prefix='.tmp_db_copy_')
        os.close(fd)
        try:
            src_conn = sqlite3.connect(src)
            dest_conn = sqlite3.connect(tmp_path)
            with dest_conn:
                src_conn.backup(dest_conn)
            dest_conn.close()
            src_conn.close()
            os.replace(tmp_path, dest)
            self.stdout.write(self.style.SUCCESS(f'Exported DB copy to {dest}'))
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)