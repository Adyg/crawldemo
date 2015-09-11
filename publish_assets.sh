cd crawldemo && \
env SECRET_KEY=`heroku config:get SECRET_KEY --app=crawldemo` \
    AWS_SECRET_ACCESS_KEY=`heroku config:get AWS_SECRET_ACCESS_KEY --app=crawldemo` \
    AWS_ACCESS_KEY_ID=`heroku config:get AWS_ACCESS_KEY_ID --app=crawldemo` \
    AWS_STORAGE_BUCKET_NAME=`heroku config:get AWS_STORAGE_BUCKET_NAME --app=crawldemo` \
    STATIC_ROOT='/vagrant/crawldemo/assets' \
    /usr/bin/python manage.py collectstatic --settings=crawldemo.settings.heroku
cd ..