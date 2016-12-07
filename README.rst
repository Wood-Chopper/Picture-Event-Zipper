Picture Event
==========

For run this app need to install Django framework and the requirements.
Execute the follow command::

    $ sudo pip install -r requirements.txt

And later followed by::

    $ python manage.py migrate

After which you can run::

    $ python manage.py runserver

And open the following URL in your web browser:

 - http://127.0.0.1:8000/

$ Créer les 3 Buckets S3

$ Mettre les ressources dans le S3 static

$ Créer le SQS

$ Créer un role pour le Lambda

$ Créer la lambda avec son trigger

$ Modifier les 2 roles IAM pour EB

$ Modifier policies S3 images et archives

$ Modifier les variables globales du Django