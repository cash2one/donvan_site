# -*- coding: utf-8 -*-

def dataParse():

    def dumpData(database):
        import subprocess
        CMD = 'mysqldump -u%s -p%s %s'%(database['USER'], database['PASSWORD'], database['NAME'])
        db = subprocess.Popen(CMD, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        db_stdout, db_stderr = db.communicate()
        if db_stderr:
            raise db_stderr
        else:
            return db_stdout

    def zipStr(root_dir=None, data=None):
        import os
        import zipfile
        from StringIO import StringIO
        buf = StringIO()
        with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
            if root_dir:
                for dirpath, dirname, filenames in os.walk(root_dir):
                    for filename in filenames:
                        zf.write(os.path.join(dirpath, filename))
            if data:
                zf.writestr('database.sql', data)
        return buf.getvalue()

    database = {
        'USER': 'donvan',
        'PASSWORD': 'qweqwe',
        'NAME': 'donvan_site'
    }
    media_dir = 'others'
    sql_data = dumpData(database)

    return zipStr(media_dir, sql_data)


def sendEmail(attach_str):

    from email.MIMEText import MIMEText
    from email.MIMEMultipart import MIMEMultipart
    import smtplib
    import datetime

    mail_host = 'localhost'
    mail_user = 'donvan@donvan.info'
    # mail_pwd = 'xx'
    mail_to = 'donvanf@hotmail.com'

    msg = MIMEMultipart()

    att = MIMEText(attach_str,'base64','utf8')
    att["Content-Type"] = 'application/octet-stream'
    att["Content-Disposition"] = 'attachment;filename="backup_%s.zip"'%datetime.datetime.now().strftime('%Y-%m-%d')
    msg.attach(att)

    message = 'to be add statistic.'
    body = MIMEText(message)
    msg.attach(body)
    msg['To'] = mail_to
    msg['from'] = mail_user
    msg['subject'] = '[backup][%s]'%datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    try:
        s = smtplib.SMTP()
        s.connect(mail_host)
        # s.login(mail_user,mail_pwd)
        s.sendmail(mail_user,mail_to,msg.as_string())
        s.close()

        print 'success'
    except Exception,e:
        print e

if __name__ == '__main__':
    sendEmail(dataParse())