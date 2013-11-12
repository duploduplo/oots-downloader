#!/usr/bin/env python
# encoding: utf-8

import os
import sys

import urllib2
import re

import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s:%(levelname)s -> %(message)s',
)
log = logging.getLogger('oots-downloader')

# Regex for image url (suddenly they decided to use an hash of the filename
# instead of the name with the progressive id).
_img_url_regex = re.compile(r'<IMG src="(/comics/images/.*\.gif)">')

# Latest comic downloaded regexp.
_img_filename = re.compile(r'oots(\d{4})\.gif')

def open_page(url):
    """
    Simpy download a content and return it as a string.
    """
    log.debug('Richiesta pagina "%s"', url)
    page = urllib2.urlopen(url).read()
    log.debug('Download di "%s" terminato', url)
    return page

def get_range(homepage='http://www.giantitp.com/Comics.html', directory='.'):
    """
    Return the latest downloaded comic and the latest available.
    """
    def _latest(homepage):
        log.debug('Ricerco l\'indice dell\'ultima vignetta in %s', homepage)
        p = open_page(homepage)
        # Prende il link all'ultima vignetta, dalla homepage per calcolare
        # l'indice.
        try:
            _l = int(re.search(r'<A href="/comics/oots(\d+)\.html" class="SideBar">', p).group(1))
            log.info('Indice dell\'ultima vignetta trovata: %d', _l)
            return _l
        except:
            log.error('Si è verificato un errore durante la ricerca della url dell\'ultima vignetta')
            raise

    def _last_downloaded(directory):
        log.debug('Ricerco l\'indice dell\'ultima vignetta scaricata')
        try:
            _downloaded = filter(lambda x: _img_filename.match(x), os.listdir(directory))[-1]
            _downloaded = int(_img_filename.match(_downloaded).group(1))
            log.info('L\'ultima vignetta scaricata è la numero %d', _downloaded)
        except IndexError:
            _downloaded = 0
            log.info('Nessuna immagine scaricata precedentemente: parto dalla prima.')
        return _downloaded

    return _last_downloaded(directory), _latest(homepage)

def get_image(n):
    """
    Downlaod the comic identified by the id n.
    """
    def _get_comic_page(n):
        return open_page('http://www.giantitp.com/comics/oots%04d.html' %n)

    def _get_img_url(page):
        return 'http://www.giantitp.com' + _img_url_regex.search(page).group(1)

    img_url = _get_img_url(_get_comic_page(n))
    log.info('Inizio il download di "%s"', img_url)
    img = open_page(img_url)
    log.info('Download terminato con successo')
    return img

def save_image(img, filename):
    """
    Save the image into file "filename".
    """
    log.info('Inizio la scrittura di %s', filename)
    open(filename, 'w').write(img)
    log.info('Scrittura di %s terminata con successo', filename)


def main():
    last_downloaded, last = get_range()
    for i in range(last_downloaded + 1, last + 1):
        save_image(get_image(i), 'oots%04d.gif' %i)

if __name__ == '__main__':
    main()
