from zuul.driver.gerrit import GerritDriver
from zuul.driver.gerrit.gerritconnection import GerritWatcher, GerritEventConnector, GerritConnection
from zuul.driver.gerrit.gerritmodel import GerritChange, GerritTriggerEvent

from zuul.merger import merger

import git

import queue
import logging
import time
import urllib
import threading
import os

###############################################################################
# comment-added ( reply with code review -1)
# {
#     'approvals': [
#         {
#             'description': 'Code-Review',
#             'type': 'Code-Review',
#             'value': '-1'
#         }
#     ],
#     'author': {
#         'email': 'alexey.morlang@gmail.com',
#         'name': 'alexey-mr',
#         'username': 'alexey-mr'
#     },
#     'change': {
#         'branch': 'master',
#         'commitMessage': 'Test dont merge\n'
#                          '\n'
#                          'Change-Id: '
#                          'Idb20a5e92bc8e6d003df1e8c2793edbd625d426c\n'
#                          'partial-jira-bug: CTINFRA-36\n',
#         'id': 'Idb20a5e92bc8e6d003df1e8c2793edbd625d426c',
#         'number': '51398',
#         'owner': {
#             'email': 'alexey.morlang@gmail.com',
#             'name': 'alexey-mr',
#             'username': 'alexey-mr'
#         },
#         'project': 'Juniper/contrail-container-builder',
#         'status': 'NEW',
#         'subject': 'Test dont merge',
#         'url': 'https://review.opencontrail.org/51398'
#     },
#     'comment': 'Patch Set 5: Code-Review-1',
#     'eventCreatedOn': 1559058915,
#     'patchSet': {
#         'author': {
#             'email': 'alexey.morlang@gmail.com',
#             'name': 'alexey-mr',
#             'username': 'alexey-mr'
#         },
#         'createdOn': 1559057380,
#         'isDraft': False,
#         'kind': 'REWORK',
#         'number': '5',
#         'parents': ['fe25d28b9699db1f56b5bb26781d3de20b9e79d0'],
#         'ref': 'refs/changes/98/51398/5',
#         'revision': 'f7427867ab80f8219839cdfcac839f1ce78af9c4',
#         'sizeDeletions': 0,
#         'sizeInsertions': 1,
#         'uploader': {
#             'email': 'alexey.morlang@gmail.com',
#             'name': 'alexey-mr',
#             'username': 'alexey-mr'
#         }
#     },
#     'type': 'comment-added'
# }
#
###############################################################################
# comment-added ( reply with code review 0  (revert of -1))
# {
#     'author': {
#         'email': 'alexey.morlang@gmail.com',
#         'name': 'alexey-mr',
#         'username': 'alexey-mr'
#     },
#     'change': {
#         'branch': 'master',
#         'commitMessage': 'Test dont merge\n'
#                          '\n'
#                          'Change-Id: '
#                          'Idb20a5e92bc8e6d003df1e8c2793edbd625d426c\n'
#                          'partial-jira-bug: CTINFRA-36\n',
#         'id': 'Idb20a5e92bc8e6d003df1e8c2793edbd625d426c',
#         'number': '51398',
#         'owner': {
#             'email': 'alexey.morlang@gmail.com',
#             'name': 'alexey-mr',
#             'username': 'alexey-mr'
#         },
#         'project': 'Juniper/contrail-container-builder',
#         'status': 'NEW',
#         'subject': 'Test dont merge',
#         'url': 'https://review.opencontrail.org/51398'
#     },
#     'comment': 'Patch Set 5: -Code-Review',
#     'eventCreatedOn': 1559058947,
#     'patchSet': {
#         'author': {
#             'email': 'alexey.morlang@gmail.com',
#             'name': 'alexey-mr',
#             'username': 'alexey-mr'
#         },
#         'createdOn': 1559057380,
#         'isDraft': False,
#         'kind': 'REWORK',
#         'number': '5',
#         'parents': ['fe25d28b9699db1f56b5bb26781d3de20b9e79d0'],
#         'ref': 'refs/changes/98/51398/5',
#         'revision': 'f7427867ab80f8219839cdfcac839f1ce78af9c4',
#         'sizeDeletions': 0,
#         'sizeInsertions': 1,
#         'uploader': {
#             'email': 'alexey.morlang@gmail.com',
#             'name': 'alexey-mr',
#             'username': 'alexey-mr'
#         }
#     },
#     'type': 'comment-added'
# }
#
###############################################################################
# Change abandoned
# {
#     'abandoner': {
#         'email': 'alexey.morlang@gmail.com',
#         'name': 'alexey-mr',
#         'username': 'alexey-mr'
#     },
#     'change': {
#         'branch': 'master',
#         'commitMessage': 'Test dont merge\n\nChange-Id: Idb20a5e92bc8e6d003df1e8c2793edbd625d426c\npartial-jira-bug: CTINFRA-36\n',
#         'id': 'Idb20a5e92bc8e6d003df1e8c2793edbd625d426c',
#         'number': '51398',
#         'owner': {
#             'email': 'alexey.morlang@gmail.com',
#             'name': 'alexey-mr',
#             'username': 'alexey-mr'
#         },
#         'project': 'Juniper/contrail-container-builder',
#         'status': 'ABANDONED',
#         'subject': 'Test dont merge',
#         'url': 'https://review.opencontrail.org/51398'},
#     'eventCreatedOn': 1559050350,
#     'patchSet': {
#         'author': {
#             'email': 'alexey.morlang@gmail.com',
#             'name': 'alexey-mr',
#             'username': 'alexey-mr'
#         },
#         'createdOn': 1558440824,
#         'isDraft': False,
#         'kind': 'NO_CODE_CHANGE',
#         'number': '2',
#         'parents': ['fe25d28b9699db1f56b5bb26781d3de20b9e79d0'],
#         'ref': 'refs/changes/98/51398/2',
#         'revision': 'b43aa31777ed90126cac8150bb108fa0dd40a874',
#         'sizeDeletions': 0,
#         'sizeInsertions': 0,
#         'uploader': {
#             'email': 'alexey.morlang@gmail.com',
#             'name': 'alexey-mr',
#             'username': 'alexey-mr'
#         }
#     },
#     'type': 'change-abandoned'
# }
#
###############################################################################
# Change-Restored:
# {
#   "restorer": {
#     "email": "alexey.morlang@gmail.com",
#     "username": "alexey-mr",
#     "name": "alexey-mr"
#   },
#   "patchSet": {
#     "isDraft": false,
#     "parents": [
#       "fe25d28b9699db1f56b5bb26781d3de20b9e79d0"
#     ],
#     "number": "2",
#     "sizeDeletions": 0,
#     "uploader": {
#       "email": "alexey.morlang@gmail.com",
#       "username": "alexey-mr",
#       "name": "alexey-mr"
#     },
#     "revision": "b43aa31777ed90126cac8150bb108fa0dd40a874",
#     "author": {
#       "email": "alexey.morlang@gmail.com",
#       "username": "alexey-mr",
#       "name": "alexey-mr"
#     },
#     "ref": "refs/changes/98/51398/2",
#     "sizeInsertions": 0,
#     "kind": "NO_CODE_CHANGE",
#     "createdOn": 1558440824
#   },
#   "type": "change-restored",
#   "eventCreatedOn": 1558967749,
#   "change": {
#     "commitMessage": "Test dont merge\n\nChange-Id: Idb20a5e92bc8e6d003df1e8c2793edbd625d426c\npartial-jira-bug: CTINFRA-36\n",
#     "project": "Juniper/contrail-container-builder",
#     "id": "Idb20a5e92bc8e6d003df1e8c2793edbd625d426c",
#     "owner": {
#       "email": "alexey.morlang@gmail.com",
#       "username": "alexey-mr",
#       "name": "alexey-mr"
#     },
#     "url": "https://review.opencontrail.org/51398",
#     "branch": "master",
#     "subject": "Test dont merge",
#     "number": "51398",
#     "status": "NEW"
#   }
# }
####

def _get_value(data, field):
    if not data:
        return None
    if not isinstance(field, list):
        return data.get(field)
    v = data.get(field[0])
    return _get_value(v, field[1:]) if len(field) > 1 else v


class GerritEventConnectorSlave(GerritEventConnector):
    def __init__(self, connection):
        super(GerritEventConnectorSlave, self).__init__(connection)

    def _addEvent(self, event):
        pass

    def _getChange(self, event):
        pass


class GerritReplicateEventThread(threading.Thread):
    log = logging.getLogger("zuul.GerritReplicateEventThread")
    delay = 10.0

    def __init__(self, connection):
        super(GerritReplicateEventThread, self).__init__()
        self.daemon = True
        self.connection = connection
        self._stopped = False

    def stop(self):
        self._stopped = True
        self.connection.replicateEvent(None)

    def _handleEvent(self):
        ts, event = self.connection.getReplicateEvent()
        if self._stopped:
            return
        self.connection.doReplicateEvent(event)

    def run(self):
        while True:
            if self._stopped:
                return
            try:
                self._handleEvent()
            except Exception as e:
                self.log.exception("Exception Replicate Gerrit event: %s" %e)
            finally:
                self.connection.replicateEventDone()


class GerritConnectionSlave(GerritConnection):
    WORKING_DIR = '/home/zuul/git-slave'

    def __init__(self, driver, connection_name, connection_config):
        super(GerritConnectionSlave, self).__init__(
            driver, connection_name, connection_config)
        self.merger = None
        self.replicate_thread = None
        self.replicate_event_queue = queue.Queue()

    def setMerger(self, merger):
        self.merger = merger

    def replicateEvent(self, event):
        return self.replicate_event_queue.put((time.time(), event))

    def getReplicateEvent(self):
        return self.replicate_event_queue.get()

    def replicateEventDone(self):
        self.log.debug("DBG: replicateEventDone")
        self.replicate_event_queue.task_done()

    def doReplicateEvent(self, event):
        if self._filterEvent(event):
            return

        change_type = _get_value(event, 'type')

        if change_type  in ['change-created', 'patchset-created']:
            return self._processPatchSetEvent(event)

        if change_type  == 'change-restored':
            return self._processChangeRestoredEvent(event)

        if change_type  == 'change-abandoned':
            return self._processChangeAbandonedEvent(event)

        if change_type  == 'change-merged':
            return self._processChangeRestoredEvent(event)

        self.log.debug("DBG: skip change type: %s" % change_type)

    def _filterEvent(self, event):
        project = _get_value(event, ['change', 'project'])
        branch = _get_value(event, ['change', 'branch'])
        if branch != 'master':
            self.log.debug("DBG: skip branch: %s" % branch)
            return True
        if project != 'Juniper/contrail-container-builder':
            self.log.debug("DBG: skip project: %s" % project)
            return True
        return False

    def _processPatchSetEvent(self, event):
        project = _get_value(event, ['change', 'project'])
        try:
            url = _get_value(event, ['change', 'url'])
            ref = _get_value(event, ['patchSet', 'ref'])
            if not url:
                self.log.debug("DBG: _processReplicatedEvent: skip event, epmty url for change")
                return
            r = urllib.parse.urlparse(url)
            remote = urllib.parse.urlunparse(r._replace(path="/{}".format(project), fragment='', query=''))
            repo = self.merger.getRepo(self.connection_name, project)
            repo.fetchFrom(remote, ref)
            commit = repo.checkout('FETCH_HEAD')
            self.log.debug("DBG: _processReplicatedEvent: checkout=%s" % commit)
            # reset author to default (zuul)
            git_repo = repo.createRepoObject()
            git_repo.git.commit('--amend', '--reset-author', '--no-edit')
            commit = git_repo.head.commit
            self.log.debug("DBG: _processReplicatedEvent: checkout=%s" % commit)
            # public changes to gerrit
            repo.push('HEAD', 'refs/publish/master')
        except Exception as e:
            self.log.exception("DBG: %s" % e)

    def _processChangeRestoredEvent(self, event):
        action = {'restore': True}
        self._processChangeRestoredOrAbandonedEvent(event, action)

    def _processChangeAbandonedEvent(self, event):
        action = {'abandon': True}
        self._processChangeRestoredOrAbandonedEvent(event, action)

    def _processChangeRestoredOrAbandonedEvent(self, event, action):
        project = _get_value(event, ['change', 'project'])
        change_id = _get_value(event, ['change', 'id'])
        self.log.debug("DBG: _processChangeRestoredOrAbandonedEvent: %s: %s: %s" % (project, change_id, action))
        query = "change:%s" % change_id
        data = self.simpleQuery(query)
        changeid = None
        for record in data:
            if _get_value(record, 'id') == change_id:
                change_number = _get_value(record, ['number'])
                patch_number = _get_value(record, ['currentPatchSet', 'number'])
                changeid = '%s,%s' % (change_number, patch_number)
        err = self.review(project, changeid, None, action)
        self.log.debug("DBG: _processChangeRestoredOrAbandonedEvent: gerrit review result: %s" % err)


    def _processChangeMergedEvent(self, event):
        self.log.debug("DBG: _processChangeMergedEvent: TODO impl")

    def _start_watcher_thread(self):
        pass

    def _start_event_connector(self):
        self.gerrit_event_connector = GerritEventConnectorSlave(self)
        self.gerrit_event_connector.start()
        self.replicate_thread = GerritReplicateEventThread(self)
        self.replicate_thread.start()

    def _stop_event_connector(self):
        if self.replicate_thread:
            self.replicate_thread.stop()
            self.replicate_thread.join()
        super(GerritConnectionSlave, self)._stop_event_connector()        


class GerritWatcherMaster(GerritWatcher):
    def __init__(self, gerrit_connection, username, hostname,
                 port=29418, keyfile=None, keepalive=60):
        super(GerritWatcherMaster, self).__init__(
            gerrit_connection, username, hostname, port=port,
            keyfile=keyfile, keepalive=keepalive)


class GerritEventConnectorMaster(GerritEventConnector):
    def __init__(self, connection):
        super(GerritEventConnectorMaster, self).__init__(connection)

    def _addEvent(self, event):
        self.log.debug("DBG: GerritEventConnectorMaster: _addEvent: %s" % event)
        self.connection.addEvent(event)

    def _getChange(self, event):
        self.log.debug("DBG: GerritEventConnectorMaster: _getChange: %s" % event)
        self.connection._getChange(event.change_number,
                                    event.patch_number,
                                    refresh=True)


class GerritConnectionMaster(GerritConnection):
    def __init__(self, driver, connection_name, connection_config):
        super(GerritConnectionMaster, self).__init__(
            driver, connection_name, connection_config)
        self.slave = None

    def setSlave(self, slave):
        self.slave = slave

    def addEvent(self, event):
        if not self.slave:
            return
        return self.slave.replicateEvent(event)

    def _start_watcher_thread(self):
        self.log.debug("DBG: gcm start gwm")
        self.watcher_thread = GerritWatcherMaster(
            self,
            self.user,
            self.server,
            self.port,
            keyfile=self.keyfile,
            keepalive=self.keepalive)
        self.watcher_thread.start()
        self.log.debug("DBG: gcm start gwm done")

    def _start_event_connector(self):
        self.log.debug("DBG: gcm start gecm")
        self.gerrit_event_connector = GerritEventConnectorMaster(self)
        self.gerrit_event_connector.start()
        self.log.debug("DBG: gcm start gecm done")


class ConnectionRegistry(object):
    log = logging.getLogger("ConnectionRegistry")

    def __init__(self):
        self.connections = {}
        self.drivers = {}

    def getSource(self, connection_name):
        connection = self.connections[connection_name]
        return connection.driver.getSource(connection)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    config_master = {
        "name":             "gerrit_master",
        "driver":           "gerrit",
        "sshkey":           "/var/ssh/zuul_rsa",
        "server":           "review.opencontrail.org",
        "user":             "alexey-mr",
        "baseurl":          "https://review.opencontrail.org"
    }

    config_slave = {
        "name":             "gerrit_slave",
        "driver":           "gerrit",
        "sshkey":           "/var/ssh/zuul_rsa",
        "server":           "gerrit",
        "user":             "zuul",
        "baseurl":          "http://gerrit",
    }

    print(os.environ)
    home=os.environ['HOME']
    path=os.environ['PATH']
    os.environ.clear()
    os.environ.update(
        {
            'HOME': home,
            'PATH': path,
            'GIT_SSH_COMMAND': 'ssh -i /var/ssh/zuul_rsa'
        }
    )
    print(os.environ)

    driver = GerritDriver()

    connection_slave = GerritConnectionSlave(driver, 'gerrit_slave', config_slave)
    connection_master = GerritConnectionMaster(driver, 'gerrit_master', config_master)

    registry = ConnectionRegistry()    
    registry.connections['gerrit_slave'] = connection_slave
    registry.connections['gerrit_master'] = connection_master

    merge_root = '/home/zuul/replica/merger-git'
    merge_email = ''
    merge_name = ''
    speed_limit = '1000'
    speed_time = '30'
    merger = merger.Merger(
        merge_root, registry, merge_email, merge_name,
        speed_limit, speed_time)

    connection_slave.setMerger(merger)
    connection_slave.onLoad()

    connection_master.setSlave(connection_slave)
    connection_master.onLoad()

    while(True):
        time.sleep(1)
    connection_master.log.debug("DBG: stop")
    connection_master.onStop()

    print("DBG: exit")
