from io import BytesIO
from datetime import datetime
from fabric import task, Connection
import warnings
from cryptography.utils import CryptographyDeprecationWarning
warnings.filterwarnings("ignore", category=CryptographyDeprecationWarning)


@task
def deploy(context):
    connection = Connection('200.130.45.80', user='webapp', port=8090)
    with connection.cd('/var/webapp/timeline/timeline'):
        connection.run('git pull')
        connection.run('../bin/python manage.py migrate')
        connection.run('../bin/python manage.py collectstatic --noinput')
        connection.run('supervisorctl restart timeline')
        print('Atualização efetuada')


@task
def deploy_test(context):
    connection = Connection('200.130.45.80', user='webapp', port=8090)
    with connection.cd('/var/webapp/timeline2/timeline/media/uploads/themes/home2'):
        connection.run('git pull')

    with connection.cd('/var/webapp/timeline2/timeline'):
        connection.run('git pull')
        connection.run('../bin/python manage.py migrate')
        connection.run('../bin/python manage.py collectstatic --noinput')
        connection.run('supervisorctl restart timeline-teste')
        print('Atualização efetuada')


@task
def connect(context):
    server = Connection('200.130.45.80', user='webapp', port=8090)
    with server.cd('/var/webapp/'):
        result = server.run('ls', hide=True)
    msg = "Ran {0.command!r} on {0.connection.host}, got stdout:\n{0.stdout}"
    print(msg.format(result))


def read_var(connection, file_path, encoding='utf-8'):
    io_obj = BytesIO()
    connection.get(file_path, io_obj)
    return io_obj.getvalue().decode(encoding)


def backup(connection, base):
    path = '/var/webapp/timeline/'
    with connection.cd(path):
        senha = read_var(connection, path+'mysql.pwd').strip()
        filename = path + 'backup%s.gz' % datetime.strftime(datetime.now(),'%Y%m%d')
        connection.run('mysqldump -u timeline -p"%s" %s --no-tablespaces | gzip > %s' % (senha, base, filename))
        print(filename)
        connection.get(filename)
        # connection.run('rm %s' % path+filename)


@task
def backup_producao(context):
    backup(Connection('200.130.45.80', user='webapp', port=8090), base='timeline')

@task
def backup_teste(context):
    backup(Connection('200.130.45.80', user='webapp', port=8090), base='timeline_teste')
