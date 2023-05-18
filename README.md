# Gerenciador de Timelines

O Timeline Larhud/IBICT é uma plataforma que se propõe a construir e hospedar linhas do tempo (timelines) sobre qualquer temática, pessoa ou instituição, permitindo assim a visualização de fatos históricos que se tornam recuperáveis a partir de notícias da mídia ou
de outras fontes verificadas, coletadas e armazenadas/arquivadas no sistema da Timeline pelo pesquisador responsável. 

O sistema foi desenvolvido em Python 3 e Django 2 e utiliza uma base MySQL/MariaDb

# Instalação

1. Criar virtualenv
> virtualenv timeline

Outra opção é utilizar: mkvirtualenv timeline -p python3

2. Ativar virtualenv
```
cd timeline
source bin/activate
mkdir logs
```

3. Clonar o repositório
> git clone git@github.com:larhud/timeline.git

4. Entrar no repositório
> cd timeline

5. Instalar as libs
> pip install -r requirements.txt

6. Copie o local.py de configs/defaults/local.py para a pasta onde se encontra o settings.py e faça os ajustes necessários para configurar o seu ambiente. Para executar o sistema em um servidor diferente da sua máquina, recomendamos que utilize o servidor NGINX e o Supervisor como gerenciador. Na mesma pasta configs/defaults existem exemplos de arquivos de configuração para ambos os serviços.

7. Preparar o Banco de Dados. A base default está em sqlite e é mais que suficiente para que você possa testar a ferramenta.
> python manage.py migrate

8. Cria o superuser
> python manage.py createsuperuser

9. Rode o servidor de testes
> python manage.py runserver

10. Acesse primeiramente o ambiente do admin para importar o tema com o layout do site utilizando o menu Tema ou acessando diretamente a URL:
> http://127.0.0.1:8000/admin/cms/theme/

Você pode encontrar o tema padrão aqui: 
> https://github.com/larhud/timeline-tema-covid/archive/refs/heads/main.zip





