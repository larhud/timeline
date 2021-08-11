# Precisa digitar a chave privada do git em producao #
# coding: utf-8
from fabric import task, Connection
from io import BytesIO
from datetime import datetime


@task
def deploy(context):
    connection = Connection('200.130.45.79', user='webapp', port=8090)
    with connection.cd('/var/webapp/vepeinfo/vepeinfo'):
        connection.run('git pull')
        connection.run('../bin/python manage.py migrate')
        connection.run('../bin/python manage.py collectstatic --noinput')
        connection.run('supervisorctl restart vepeinfo')
        print('Atualização efetuada')


@task
def connect(context):
    server = Connection('200.130.45.79', user='webapp', port=8090)
    with server.cd('/var/webapp/'):
        result = server.run('ls', hide=True)
    msg = "Ran {0.command!r} on {0.connection.host}, got stdout:\n{0.stdout}"
    print(msg.format(result))


def read_var(connection, file_path, encoding='utf-8'):
    io_obj = BytesIO()
    connection.get(file_path, io_obj)
    return io_obj.getvalue().decode(encoding)


def backup(connection):
    path = '/var/webapp/vepeinfo/'
    with connection.cd(path):
        senha = read_var(connection, path+'mysql.pwd').strip()
        filename = path + 'backup%s.gz' % datetime.strftime(datetime.now(),'%Y%m%d')
        connection.run('mysqldump -u vepeinfo -p"%s" vepeinfo --no-tablespaces | gzip > %s' % (senha, filename))
        print(filename)
        connection.get(filename)
        # connection.run('rm %s' % path+filename)


@task
def backup_producao(context):
    backup(Connection('200.130.45.79', user='webapp', port=8090))
