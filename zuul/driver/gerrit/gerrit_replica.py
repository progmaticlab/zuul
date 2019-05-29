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
import re

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
#
###############################################################################
# change-merged:
# {
#     'change': {
#         'branch': 'master',
#         'commitMessage': 'For dpdk cluster enable agent restart testcases\n'
#                         'Added agent-dpdk to list of services\n'
#                         'Restart dpdk agent before starting agent '
#                         'container\n'
#                         '\n'
#                         'Change-Id: Ie5def7a66f8415147e78e4869943266df2a81b3a\n'
#                         'Closes-jira-bug: CEM-5445\n',
#         'id': 'Ie5def7a66f8415147e78e4869943266df2a81b3a',
#         'number': '51367',
#         'owner': {'email': 'aswanikr@juniper.net',
#                     'name': 'aswani kumar',
#                     'username': 'aswanikumar'},
#         'project': 'Juniper/contrail-test',
#         'status': 'MERGED',
#         'subject': 'For dpdk cluster enable agent restart testcases Added '
#                     'agent-dpdk to list of services Restart dpdk agent '
#                     'before starting agent container',
#         'topic': 'R5.1_dpdk',
#         'url': 'https://review.opencontrail.org/51367'},
#         'eventCreatedOn': 1559063795,
#         'newRev': '6a9eebe460d6eaaec1be5f0e1c3a0084be3b68ac',
#         'patchSet': {
#             'author': {'email': 'aswanikr@juniper.net',
#                         'name': 'aswani kumar',
#                         'username': 'aswanikumar'},
#             'createdOn': 1558332874,
#             'isDraft': False,
#             'kind': 'REWORK',
#             'number': '1',
#             'parents': ['21e4274883604fb956e33ad78fbd09c90f9ec2ea'],
#             'ref': 'refs/changes/67/51367/1',
#             'revision': '2ca687f3781752324eeb1e77f1045a4b900c8211',
#             'sizeDeletions': -5,
#             'sizeInsertions': 33,
#             'uploader': {'email': 'aswanikr@juniper.net',
#                         'name': 'aswani kumar',
#                         'username': 'aswanikumar'}},
#             'submitter': {'email': 'zuulv3@zuul.opencontrail.org',
#                             'name': 'Zuul v3 CI',
#                             'username': 'zuulv3'},
#     'type': 'change-merged'
# }

REPLICATE_PROJECTS = [
    'Juniper/contrail-analytics',
    'Juniper/contrail-ansible-deployer',
    'Juniper/contrail-api-client',
    'Juniper/contrail-build',
    'Juniper/contrail-common',
    'Juniper/contrail-community-docs',
    'Juniper/contrail-container-builder',
    'Juniper/contrail-controller',
    'Juniper/contrail-deployers-containers',
    'Juniper/contrail-dev-env',
    'Juniper/contrail-docker',
    'Juniper/contrail-docs',
    'Juniper/contrail-dpdk',
    'Juniper/contrail-heat',
    'Juniper/contrail-helm-deployer',
    'Juniper/contrail-horizon',
    'Juniper/contrail-infra',
    'Juniper/contrail-infra-doc',
    'Juniper/contrail-java-api',
    'Juniper/contrail-kolla-ansible',
    'Juniper/contrail-neutron-plugin',
    'Juniper/contrail-nova-vif-driver',
    'Juniper/contrail-packages',
    'Juniper/contrail-packaging',
    'Juniper/contrail-provisioning',
    'Juniper/contrail-puppet',
    'Juniper/contrail-sandesh',
    'Juniper/contrail-specs',
    'Juniper/contrail-test',
    'Juniper/contrail-test-ci',
    'Juniper/contrail-third-party',
    'Juniper/contrail-third-party-cache',
    'Juniper/contrail-third-party-packages',
    'Juniper/contrail-tripleo-heat-templates',
    'Juniper/contrail-tripleo-puppet',
    'Juniper/contrail-vro-plugin',
    'Juniper/contrail-vrouter'
]

COMMENT_PATTERN = 'recheck(( zuulv3)|( no bug))?(\s+clean)?\s*$'
COMMENT_RE = re.compile(COMMENT_PATTERN, re.MULTILINE)

def _get_value(data, field):
    if not data:
        return None
    if not isinstance(field, list):
        return data.get(field)
    v = data.get(field[0])
    return _get_value(v, field[1:]) if len(field) > 1 else v


class GerritEventConnectorSlave(GerritEventConnector):
    log = logging.getLogger("zuul.GerritEventConnectorSlave")

    def __init__(self, connection):
        super(GerritEventConnectorSlave, self).__init__(connection)

    def _handleEvent(self):
        ts, event = self.connection.getEvent()
        # pause see details in base class
        self._pauseForGerrit()
        if self._stopped:
            return
        self.connection.doReplicateEvent(event)

    def _addEvent(self, event):
        pass

    def _getChange(self, event):
        pass

    def _pauseForGerrit(self):
        now = time.time()
        time.sleep(max((ts + self.delay) - now, 0.0))


class GerritConnectionSlave(GerritConnection):
    log = logging.getLogger("zuul.GerritConnectionSlave")
    iolog = logging.getLogger("zuul.GerritConnectionSlave.io")

    WORKING_DIR = '/home/zuul/git-slave'

    def __init__(self, driver, connection_name, connection_config):
        super(GerritConnectionSlave, self).__init__(
            driver, connection_name, connection_config)
        self.merger = None

    def setMerger(self, merger):
        self.merger = merger

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
            return self._processChangeMergedEvent(event)

        if change_type  == 'comment-added':
            return self._processCommentAddedEvent(event)

        self.log.debug("DBG: skip change type: %s" % change_type)

    def _filterEvent(self, event):
        project = _get_value(event, ['change', 'project'])
        branch = _get_value(event, ['change', 'branch'])
        if branch != 'master':
            self.log.debug("DBG: skip branch: %s" % branch)
            return True
        if project not in REPLICATE_PROJECTS:
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
            new_message =  'Initial Review: %s\n\n%s' % (url, _get_value(event, ['change', 'commitMessage']))
            git_repo.git.commit('--amend', '--reset-author', '--no-edit', '--message', new_message)
            commit = git_repo.head.commit
            self.log.debug("DBG: _processReplicatedEvent: checkout=%s" % commit)
            # public changes to gerrit
            repo.push('HEAD', 'refs/publish/master')
        except Exception as e:
            self.log.exception("DBG: %s" % e)

    def _processChangeRestoredEvent(self, event):
        action = {'restore': True}
        changeid = self._getCurrentReviewId(event)
        if changeid is None:
            # push as new
            self._processPatchSetEvent(event)
        else:
            self._processChangeRestoredOrAbandonedEvent(event, action, changeid)

    def _processChangeAbandonedEvent(self, event):
        action = {'abandon': True}
        changeid = self._getCurrentReviewId(event)
        if changeid is None:
            self.log.debug("DBG: _processChangeAbandonedEvent: review is not replicated - skipped")
            return
        self._processChangeRestoredOrAbandonedEvent(event, action, changeid)

    def _getCurrentReviewId(self, event):
        change_id = _get_value(event, ['change', 'id'])
        query = "change:%s" % change_id
        data = self.simpleQuery(query)
        changeid = None
        for record in data:
            if _get_value(record, 'id') == change_id:
                change_number = _get_value(record, ['number'])
                patch_number = _get_value(record, ['currentPatchSet', 'number'])
                changeid = '%s,%s' % (change_number, patch_number)
        return changeid

    def _processChangeRestoredOrAbandonedEvent(self, event, action, changeid):
        project = _get_value(event, ['change', 'project'])
        change_id = _get_value(event, ['change', 'id'])
        self.log.debug("DBG: _processChangeRestoredOrAbandonedEvent: %s: %s: %s" % (project, change_id, action))
        err = self.review(project, changeid, None, action)
        self.log.debug("DBG: _processChangeRestoredOrAbandonedEvent: gerrit review result: %s" % err)

    def _processChangeMergedEvent(self, event):
        # project = _get_value(event, ['change', 'project'])
        change_id = _get_value(event, ['change', 'id'])
        query = "change:%s" % change_id
        data = self.simpleQuery(query)
        self.log.debug("DBG: _processChangeMergedEvent: gerrit review result: %s" % data)
        # TODO: force merge?
        # change_number = _get_value(event, ['change', 'number'])
        # patch_number = _get_value(event, ['patchSet', 'number'])
        # changeid = '%s,%s' % (change_number, patch_number)
        # self.log.debug("DBG: _processChangeMergedEvent: %s: %s" % (project, changeid))
        # action = {
        #     'verified': '+2',
        #     'code-review': '+2',
        #     'approved': '+1'
        # }
        # err = self.review(project, changeid, None, action)
        # self.log.debug("DBG: _processChangeMergedEvent: gerrit review result: %s" % err)

    def _processCommentAddedEvent(self, event):
        project = _get_value(event, ['change', 'project'])
        change_id = _get_value(event, ['change', 'id'])
        self.log.debug("DBG: _processCommentAddedEvent: %s: %s" % (project, change_id))
        changeid = self._getCurrentReviewId(event)
        if changeid is None:
            # review is not replicated yet, push new
            self._processPatchSetEvent(event)
            self.gerrit_event_connector._pauseForGerrit()
            changeid = self._getCurrentReviewId(event)
        if changeid is None:
            self.log.debug("DBG: _processCommentAddedEvent: review is not replicated and failed to replicate - skipped")
            return
        actions = {}
        message = None
        approvals = _get_value(event, 'approvals')
        if approvals is not None:
            for a in approvals:
                t = _get_value(a, 'type')
                v = _get_value(a, 'value')
                if t == 'Code-Review':
                    actions['code-review'] = v
                elif t == 'Approved':
                    actions['approved'] = v
                else:
                    self.log.debug("DBG: _processCommentAddedEvent: skip approval type: %s" % t)
                    return
        else:
            comment = _get_value(event, 'comment')
            # if comment.find(': -Code-Review'):
            #     actions['code-review'] = '0'
            if COMMENT_RE.search(comment) is not None:
                message = 'recheck'
            else:
                self.log.debug("DBG: _processCommentAddedEvent: skip comment: %s" % comment)
                return
        err = self.review(project, changeid, message, actions)
        self.log.debug("DBG: _processChangeMergedEvent: gerrit review result: %s" % err)


    def _start_watcher_thread(self):
        pass

    def _start_event_connector(self):
        self.gerrit_event_connector = GerritEventConnectorSlave(self)
        self.gerrit_event_connector.start()


class GerritWatcherMaster(GerritWatcher):
    log = logging.getLogger("gerrit.GerritWatcherMaster")

    def __init__(self, gerrit_connection, username, hostname,
                 port=29418, keyfile=None, keepalive=60):
        super(GerritWatcherMaster, self).__init__(
            gerrit_connection, username, hostname, port=port,
            keyfile=keyfile, keepalive=keepalive)


class GerritConnectionMaster(GerritConnection):
    log = logging.getLogger("zuul.GerritConnectionMaster")
    iolog = logging.getLogger("zuul.GerritConnectionMaster.io")

    def __init__(self, driver, connection_name, connection_config):
        super(GerritConnectionMaster, self).__init__(
            driver, connection_name, connection_config)
        self.slave = None

    def setSlave(self, slave):
        self.slave = slave

    def addEvent(self, event):
        if not self.slave:
            return
        return self.slave.addEvent(event)

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
        pass


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
