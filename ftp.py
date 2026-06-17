import os
import tarfile
import ssl
from ftplib import FTP, FTP_TLS
from datetime import datetime


# KONFIGURACJA

FILES_TO_BACKUP = [
    r"C:\Users\Iza\Desktop\semestr2\programowanieskryptowe\plik1.txt",
]

BACKUP_DIR = r"C:\Users\Iza\Desktop\semestr2\programowanieskryptowe\Backup"

FTP_HOST = "127.0.0.1"
FTP_PORT = 21
FTP_USER = "iza"
FTP_PASSWORD = "haslo123"
FTP_REMOTE_DIR = "/"

# KLASA FTPS Z TLS SESSION REUSE

class ReusableSessionFTP_TLS(FTP_TLS):
    def ntransfercmd(self, cmd, rest=None):
        conn, size = FTP.ntransfercmd(self, cmd, rest)

        if self._prot_p:
            conn = self.context.wrap_socket(
                conn,
                server_hostname=self.host,
                session=self.sock.session
            )

        return conn, size

# TWORZENIE ARCHIWUM
def create_archive(files, backup_dir):
    os.makedirs(backup_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_name = f"backup_{timestamp}.tar.gz"
    archive_path = os.path.join(backup_dir, archive_name)

    with tarfile.open(archive_path, "w:gz") as archive:
        for file in files:
            if os.path.exists(file):
                archive.add(file, arcname=os.path.basename(file))
                print(f"Dodano: {file}")
            else:
                print(f"Nie znaleziono pliku: {file}")

    return archive_path


# WYSYŁANIE NA SERWER FTPS
def upload_to_ftps(file_path):
    context = ssl._create_unverified_context()

    ftps = ReusableSessionFTP_TLS(context=context)

    try:
        ftps.connect(FTP_HOST, FTP_PORT)

        # Włączenie TLS przed logowaniem
        ftps.auth()

        # Logowanie
        ftps.login(FTP_USER, FTP_PASSWORD)

        # Szyfrowany kanał danych
        ftps.prot_p()

        print("Połączono z serwerem FTPS.")

        ftps.cwd(FTP_REMOTE_DIR)

        filename = os.path.basename(file_path)

        with open(file_path, "rb") as file:
            ftps.storbinary(f"STOR {filename}", file)

        print(f"Plik {filename} został wysłany na serwer FTPS.")

    finally:
        try:
            ftps.quit()
        except:
            ftps.close()


# PROGRAM GŁÓWNY
def main():
    try:
        archive = create_archive(FILES_TO_BACKUP, BACKUP_DIR)
        print(f"Utworzono archiwum: {archive}")

        upload_to_ftps(archive)

        print("Backup zakończony pomyślnie.")

    except Exception as e:
        print(f"Błąd: {e}")

if __name__ == "__main__":
    main()
