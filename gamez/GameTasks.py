from gamez.Logger import *
from gamez import common
from gamez.classes import Game, Download, History
from plugins import Indexer
import datetime
import os
import json
from gamez.jsonHelper import MyEncoder


def runSearcher():
    log("running searcher")
    for game in Game.select():
        if game.status == common.FAILED and common.SYSTEM.c.again_on_fail:
            game.status = common.WANTED
        elif game.status != common.WANTED:
            continue
        elif game.release_date and game.release_date > datetime.datetime.now(): # is the release date in the future
            continue
        log("Looking for %s" % game)
        searchGame(game)


def notify(game):
    for notifier in common.PM.N:
        createGenericEvent(game, 'Notifier', 'Sending notification with %s on status %s' % (notifier, game.status))
        if notifier.c.on_snatch and game.status == common.SNATCHED:
            notifier.sendMessage("%s has been snatched" % game, game)
        if notifier.c.on_complete and game.status in (common.COMPLETED, common.DOWNLOADED, common.PP_FAIL):
            notifier.sendMessage("%s is now %s" % (game, game.status), game)


def createGenericEvent(game, event_type, event_msg):
    h = History()
    h.game = game
    h.event = event_type
    h.obj_id = 0
    h.obj_class = 'Generic'
    h.old_obj = json.dumps(game, cls=MyEncoder)
    h.new_obj = json.dumps({'_data': {'msg': event_msg}})
    h.save()


def commentOnDownload(download):
    for indexer in common.PM.I:
        if indexer.type != download.indexer or indexer.instance != download.indexer_instance:
            continue
        if indexer.c.comment_on_download and download.status == common.FAILED:
            indexer.commentOnDownload('Gamez snatched this but it failed to download (automtic notice)', download)
        if indexer.c.comment_on_download and download.status in (common.COMPLETED, common.DOWNLOADED, common.PP_FAIL):
            indexer.commentOnDownload('Gamez snatched this and it downloaded successfully (automtic notice)', download)


def searchGame(game):
    blacklist = common.SYSTEM.getBlacklistForPlatform(game.platform)
    whitelist = common.SYSTEM.getWhitelistForPlatform(game.platform)
    for indexer in common.PM.I:
        createGenericEvent(game, 'Search', 'Searching %s on %s' % (game, indexer))
        downloads = indexer.searchForGame(game) #intensiv
        downloads = _filterBadDownloads(blacklist, whitelist, downloads)
        return snatchOne(game, downloads)
    return game.status


# in a way we dont need game here since each download holds a ref to each game ... but it is easier to read
def snatchOne(game, downloads):
    for downloader in common.PM.getDownloaders(types=Indexer.types):
        for download in downloads:
            createGenericEvent(game, 'Snatch', 'Trying to snatch %s' % download.name)
            if downloader.addDownload(game, download):
                game.status = common.SNATCHED # games save status automatically
                download.status = common.SNATCHED # downloads don't
                download.save()
                notify(game)
                return game.status #exit on first success
    return game.status


def _filterBadDownloads(blacklist, whitelist, downloads, min_size=0):
    clean = []
    for download in downloads:
        nope = False
        for white_word in whitelist:
            log("Checking white word: '%s' in '%s'" % (white_word, download.name))
            if not white_word.lower() in download.name.lower():
                log.info("Did not find required word '%s' in title: '%s'. Skipping..." % (white_word, download.name))
                nope = True
            else:
                log.info("Found suitable download: '%s'" % download.name)
                nope = False
                break
        for black_word in blacklist:
            log("Checking Word: '%s' in '%s'" % (black_word, download.name))
            if black_word.lower() in download.name.lower():
                log.info("Found '%s' in Title: '%s'. Skipping..." % (black_word, download.name))
                nope = True
                break
        if nope:
            continue
        old_download = None
        try:
            old_download = Download.get(Download.url == download.url)
        except Download.DoesNotExist:
            #no download with that url found
            pass

        if not old_download:
            log("Saving the new download we found %s" % download)
            download.status = common.UNKNOWN
            download.save()
        else:
            if old_download.status in (common.FAILED, common.DOWNLOADED):
                log.info("Found a Download(%s) with the same url and it failed or we downloaded it already. Skipping..." % download)
                continue
            if old_download.status == common.SNATCHED:
                if common.SYSTEM.c.resnatch_same:
                    continue
                log.info("Found a Download(%s) with the same url and we snatched it already. I'l get it again..." % download)
            download = old_download
        if not min_size or min_size < download.size:
            clean.append(download)
    return clean


def runChecker():
    games = Game.select().execute()
    for checker in common.PM.D:
        for game in games:
            if not game.status == common.SNATCHED:
                continue
            log("Checking game status for %s" % game)
            status, download, path = checker.getGameStaus(game)
            log("%s gave back status %s for game %s on download %s" % (checker, status, game, download))
            if status == common.DOWNLOADED:
                game.status = common.DOWNLOADED
                if download.id:
                    download.status = common.DOWNLOADED
                    download.save()
                ppGame(game, download, path)
                notify(game)
                if download.id:
                    commentOnDownload(download)
            elif status == common.SNATCHED:
                game.status = common.SNATCHED #status setting on Game saves automatically
                download.status = common.SNATCHED
                download.save()
            elif status == common.FAILED:
                download.status = common.FAILED
                download.save()
                if common.SYSTEM.c.again_on_fail:
                    game.status = common.WANTED
                    searchGame(game)
                else:
                    game.status = common.FAILED


def ppGame(game, download, path):
    pp_try = False
    for pp in common.PM.PP:
        createGenericEvent(game, 'PostProcess', 'Starting PP with %s' % pp)
        if pp.ppPath(game, path):
            game.status = common.COMPLETED # downloaded and pp success
            download.status = common.COMPLETED
            download.save()
            return True
        pp_try = True
    if pp_try:
        game.status = common.PP_FAIL # tried to pp but fail
        download.status = common.PP_FAIL
        download.save()
    return False


#TDOD: make this play nice with multiple providers !!
def updateGames():
    log("running game updater")
    for game in Game.select():
        if game.status == common.DELETED:
            continue
        updateGame(game)


def updateGame(game):
    for p in common.PM.P:
        new_game = p.getGame(game.tgdb_id)
        createGenericEvent(game, 'Update', 'Serching for update on %s' % p)
        if new_game and new_game != game:
            log.info("Found new version of %s" % game)
            new_game.id = game.id
            new_game.status = game.status # this will save the new game stuff
        if new_game.boxart_url != game.boxart_url or not os.path.exists(game.boxArtPath()):
            createGenericEvent(game, 'Update', 'Getting new cover image' % p)
            new_game.cacheImg()
