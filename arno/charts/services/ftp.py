from ftplib import FTP
from typing import List

from ..models import FtpCredential


def load_rows_from_ftp(filename: str, ftp_name: str) -> (List[List[str]], FtpCredential):
    if ftp_name is not None:
        ftp_credential = FtpCredential.objects.get(name=ftp_name)
    else:
        ftp_credential = FtpCredential.objects.all()[0]
    ftp = FTP(ftp_credential.host)
    ftp.login(ftp_credential.user, ftp_credential.pwd)
    try:
        lines = []
        ftp.retrlines('RETR ' + filename + '.CSV', lines.append)
        return [line.split(';') for line in lines], ftp_credential
    finally:
        ftp.quit()
