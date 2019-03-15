# <WARNING>
# Everything within sections like <TAG> is generated and can
# be automatically replaced on deployment. You can disable
# this functionality by simply removing the wrapping tags.
# </WARNING>

# <DOCKER_FROM>
FROM aldryn/base-project:py3-3.25.1
# </DOCKER_FROM>

# <NPM>
# </NPM>

# <BOWER>
# </BOWER>

# we want to keep project-specific sources in the "src" folder
ENV PYTHONPATH=/app/src:$PYTHONPATH

# <PYTHON>
ENV PIP_INDEX_URL=${PIP_INDEX_URL:-https://wheels.aldryn.net/v1/aldryn-extras+pypi/${WHEELS_PLATFORM:-aldryn-baseproject-py3}/+simple/} \
    WHEELSPROXY_URL=${WHEELSPROXY_URL:-https://wheels.aldryn.net/v1/aldryn-extras+pypi/${WHEELS_PLATFORM:-aldryn-baseproject-py3}/}
COPY requirements.* /app/
COPY addons-dev /app/addons-dev/
RUN pip-reqs compile && \
    pip-reqs resolve && \
    pip install \
        --no-index --no-deps \
        --requirement requirements.urls
# </PYTHON>

# This app is automatically installed by the aldryn-django-cms package.
# There are legacy reasons for this but in this case we cna just remove it.
# Can't leave it in because both this and django-recaptcha have a captcha package :/
RUN pip uninstall --yes django-simple-captcha && pip install django-recaptcha==2.0.2

# <SOURCE>
COPY . /app
# </SOURCE>

# <GULP>
# </GULP>

RUN rm -rf /static/*

# <STATIC>
RUN DJANGO_MODE=build python manage.py collectstatic --noinput
# </STATIC>
