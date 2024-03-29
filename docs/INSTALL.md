# Installation

Dependencies:

- Python
- Git
- Node.JS

All of these are _extremely standard_, so if you search "install X windows",
"install X mac", you should get usable results. I actually think Python is
pre-installed on Mac's these days. (If you're on Linux, then you should be able
to figure it out yourself.)

## Setting up Django

On a standard Linux system, suppose you want to build the MOSP server inside the
folder `~/Documents/MOSP/`. Then you should do the following steps to first get
Django to work:

```shell
cd ~/Documents/MOSP/
git clone https://github.com/vEnhance/mosp-web/
cd mosp-web
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py check
python manage.py migrate
python manage.py runserver
```

If this works the shell will hang, meaning the server is running!
Point your web browser to [http://127.0.0.1:8000](http://127.0.0.1:8000)
and you should see a version of the MOSP website.

It's missing something though --- all the static files are not there yet,
meaning no JavaScript and no CSS. You need to fix this by installing the
relevant machinery.
MOSP-WEB uses [Typescript](https://duckduckgo.com/?q=typescript)
and [Tailwind CSS](https://duckduckgo.com/?q=tailwindcss) for these.

## Compiling Typescript

To get Typescript working, do the following:

```shell
cd ~/Documents/MOSP/mosp-web/
sudo npm install -g typescript
cd ~/Documents/MOSP/mosp-web/typescripts/
tsc
cd ~/Documents/MOSP/mosp-web/data2021/
tsc
```

## Compiling Tailwind

Stop the previously running `python manage.py runserver` command.
Then do the following.

```shell
cd ~/Documents/MOSP/mosp-web/
npm install -D tailwindcss@latest postcss@latest autoprefixer@latest
source venv/bin/activate
python manage.py collectstatic
python manage.py tailwind install
python manage.py tailwind build
python manage.py tailwind start
```

Restart `python manage.py runserver` command from before.
Then in an ideal world, Tailwind will work.

## What if I'm not using Linux?

You'll have to google stuff, sorry. Things that should "just work" often don't
function correctly outside Linux, doubly so if you're on Windows.
