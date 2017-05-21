Image source: https://github.com/mailhog/MailHog/blob/master/Dockerfile.


## Usage with docker-compose:

    $ docker build . -f docker/mailhog/Dockerfile -t mailhog/mailhog:latest
    $ docker run -d -p 1025:1025 -p 8025:8025 mailhog/mailhog
    $ navigate with your browser to localhost:8025
