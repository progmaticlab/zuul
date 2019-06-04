from zuul.driver.gerrit import GerritDriver
from zuul.driver.gerrit.gerritconnection import GerritWatcher, GerritEventConnector, GerritConnection
from zuul.driver.gerrit.gerritmodel import GerritChange, GerritTriggerEvent

from zuul.merger import merger

import logging
import time
import urllib
import threading
import os
import re
import sys
import paramiko

import argparse


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

REPLICATE_BRANCHES = [
    'master',
    'stable/queens'
]

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
#     'change': {'branch': 'master',
#                 'commitMessage': 'accept cc-ip-address:cc-port as well, keep 443 '
#                                 'as default\n'
#                                 '\n'
#                                 'closes-jira-bug: CEM-5823\n'
#                                 '\n'
#                                 'PATCH-1:\n'
#                                 '1. addressing review comments\n'
#                                 'Change-Id: '
#                                 'Icdcc77c7548cd5ac0346138becf96090fca7ea9d\n',
#                 'id': 'Icdcc77c7548cd5ac0346138becf96090fca7ea9d',
#                 'number': '51529',
#                 'owner': {'email': 'dgautam@juniper.net',
#                         'name': 'Dheeraj Gautam',
#                         'username': 'dgautam'},
#                 'project': 'Juniper/contrail-controller',
#                 'status': 'MERGED',
#                 'subject': 'accept cc-ip-address:cc-port as well, keep 443 as '
#                         'default',
#                 'topic': 'cem-5824',
#                 'url': 'https://review.opencontrail.org/51529'
#     },
#     'eventCreatedOn': 1559239187,
#     'newRev': 'c04546e7ebb572ac48942c958691fa370c465b02',
#     'patchSet': {'author': {'email': 'dgautam@juniper.net',
#                             'name': 'Dheeraj Gautam',
#                             'username': 'dgautam'},
#                 'createdOn': 1559158074,
#                 'isDraft': False,
#                 'kind': 'REWORK',
#                 'number': '3',
#                 'parents': ['5b9271dd08b80ee95cea60a1f302f427d9873df9'],
#                 'ref': 'refs/changes/29/51529/3',
#                 'revision': '6b6746e69213b864705d7beb1a8ee4e2dbdafd95',
#                 'sizeDeletions': -2,
#                 'sizeInsertions': 5,
#                 'uploader': {'email': 'dgautam@juniper.net',
#                             'name': 'Dheeraj Gautam',
#                             'username': 'dgautam'}},
#     'submitter': {'email': 'zuulv3@zuul.opencontrail.org',
#                 'name': 'Zuul v3 CI',
#                 'username': 'zuulv3'},
#     'type': 'change-merged'
# }


COMMENT_PATTERN = 'recheck(( zuulv3)|( no bug))?(\s+clean)?\s*$'
COMMENT_RE = re.compile(COMMENT_PATTERN, re.MULTILINE)

REVIEW_ID_PATTERN = 'Change-Id:[ ]*[a-z0-9A-Z]+'
REVIEW_ID_RE = re.compile(REVIEW_ID_PATTERN)


def _get_value(data, field):
    if not data:
        return None
    if not isinstance(field, list):
        return data.get(field)
    v = data.get(field[0])
    return _get_value(v, field[1:]) if len(field) > 1 else v


class GerritConnectionReplicationBase(GerritConnection):
    def _findReviewInGerrit(self, project, review_id): 
        self.log.debug("DBG: _findReviewInGerrit: project: %s, %s" % (project, review_id))
        query = "change:%s" % review_id
        data = self.simpleQuery(query)
        self.log.debug("DBG: _findReviewInGerrit: data: %s" % data)
        for record in data:
            rid = _get_value(record, 'id')
            if rid == review_id:
                status = _get_value(record, 'status')
                if status is None:
                    status = _get_value(record, ['change', 'status'])
                if status == 'ABANDONED':
                    self.log.debug("DBG: _findReviewInGerrit: skip abandoned")
                    continue
                self.log.debug("DBG: _findReviewInGerrit: found: %s" % record)
                return record
        return None


class GerritEventConnectorSlave(GerritEventConnector):
    log = logging.getLogger("zuul.GerritEventConnectorSlave")

    def __init__(self, connection):
        super(GerritEventConnectorSlave, self).__init__(connection)

    def _handleEvent(self):
        ts, event = self.connection.getEvent()
        # pause see details in base class
        self._pauseForGerrit(ts = ts)
        if self._stopped:
            return
        self.connection.doReplicateEvent(event)

    def _addEvent(self, event):
        pass

    def _getChange(self, event):
        pass

    def _pauseForGerrit(self, ts = None):
        if ts is not None:
            now = time.time()
            time.sleep(max((ts + self.delay) - now, 0.0))
        else:
            time.sleep(self.delay)

class GerritConnectionSlave(GerritConnectionReplicationBase):
    log = logging.getLogger("zuul.GerritConnectionSlave")
    iolog = logging.getLogger("zuul.GerritConnectionSlave.io")

    def __init__(self, driver, connection_name, connection_config):
        super(GerritConnectionSlave, self).__init__(
            driver, connection_name, connection_config)
        self.merger = None
        self.master = None
        self.ssh_gerrit_client = None

    def setMaster(self, master):
        self.master = master

    def setMerger(self, merger):
        self.merger = merger

    def doReplicateEvent(self, event):
        if self._filterEvent(event):
            return

        change_type = _get_value(event, 'type')
        if change_type is None:
            change_type = _get_value(event, ['change', 'type'])

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
        if branch not in REPLICATE_BRANCHES:
            self.log.debug("DBG: skip branch: %s" % branch)
            return True
        if project not in REPLICATE_PROJECTS:
            self.log.debug("DBG: skip project: %s" % project)
            return True
        return False

    def _getRemote(self, project, url):
        r = urllib.parse.urlparse(url)
        remote = urllib.parse.urlunparse(r._replace(path="/{}".format(project), fragment='', query=''))
        return remote

    def _checkoutFromRemote(self, repo, remote, project, ref):
        repo.fetchFrom(remote, ref)
        git_repo = repo.createRepoObject()
        git_repo.git.checkout("FETCH_HEAD")
        return git_repo.head.commit

    def _amendCommitMessage(self, repo, message=None, commit_id=None):
        git_repo = repo.createRepoObject()
        if commit_id is not None:
            git_repo.git.checkout(commit_id)
        if message is not None:
            git_repo.git.commit('--amend', '--reset-author', '--no-edit', '--message', message)
        else:
            git_repo.git.commit('--amend', '--reset-author', '--no-edit')
        return git_repo.head.commit

    def _processPatchSetEvent(self, event):
        commit = None
        project = _get_value(event, ['change', 'project'])
        branch = _get_value(event, ['change', 'branch'])
        self.log.debug("DBG: _processPatchSetEvent: project=%s, branch=%s" % (project, branch))
        url = _get_value(event, ['change', 'url'])
        ref = _get_value(event, ['patchSet', 'ref'])
        if not url:
            self.log.debug("DBG: _processPatchSetEvent: skip event, epmty url for change")
            return
        remote = self._getRemote(project, url)
        repo = self.merger.getRepo(self.connection_name, project)
        commit = self._checkoutFromRemote(repo, remote, project, ref)
        self.log.debug("DBG: _processPatchSetEvent: commit=%s" % commit)
        # reset author to default (zuul)
        new_message =  'Initial Review: %s\n\n%s' % (url, _get_value(event, ['change', 'commitMessage']))
        commit = self._amendCommitMessage(repo, message=new_message)
        self.log.debug("DBG: _processPatchSetEvent: amended commit=%s" % commit)
        # public changes to gerrit
        repo.push('HEAD', 'refs/publish/%s' % branch)
        self._pauseForGerrit()
        changeid = self._getCurrentChangeId(event)
        if changeid is None:
            # try push parent (TODO: for one only first parent)
            try_again = False
            for p in _get_value(event, ['patchSet', 'parents']):
                parent_review_id, parent_event = self._findCommitInGerritMaster(project, p)
                if parent_event is not None:
                    #patch parent event if it has no change inside )it is for merged changes)
                    parent_event = self._currentPatchSet2ChangeEvent(parent_event)
                    # pranet found on master
                    parent_changeid = self._getCurrentChangeId(parent_event)
                    if parent_changeid is not None:
                        # parent already commited
                        self.log.debug("DBG: _processPatchSetEvent: parent:  %s: already commited" % parent_review_id)
                        continue
                    # replicate parent
                    self.log.debug("DBG: _processPatchSetEvent: parent:  %s: try to replicate" % parent_review_id)
                    parent_changeid = self._processPatchSetEvent(parent_event)
                    try_again = parent_changeid is not None
            if try_again:
                # try to push commit again
                self.log.debug("DBG: _processPatchSetEvent: retry to push")
                git_repo = repo.createRepoObject()
                git_repo.git.checkout(commit)
                repo.push('HEAD', 'refs/publish/%s' % branch)
                self._pauseForGerrit()
                changeid = self._getCurrentChangeId(event)
        return changeid

    def _processChangeRestoredEvent(self, event):
        action = {'restore': True}
        changeid = self._getCurrentChangeId(event)
        if changeid is None:
            # push as new
            self._processPatchSetEvent(event)
        else:
            self._processChangeRestoredOrAbandonedEvent(event, action, changeid)

    def _processChangeAbandonedEvent(self, event):
        action = {'abandon': True}
        changeid = self._getCurrentChangeId(event)
        if changeid is None:
            self.log.debug("DBG: _processChangeAbandonedEvent: review is not replicated - skipped")
            return
        self._processChangeRestoredOrAbandonedEvent(event, action, changeid)

    def _formatCurrentChangeId(self, event):
        change_number = _get_value(event, ['number'])
        patch_number = _get_value(event, ['currentPatchSet', 'number'])
        changeid = '%s,%s' % (change_number, patch_number)
        return changeid

    def _getCurrentChangeId(self, event):
        review_id = _get_value(event, ['change', 'id'])
        query = "change:%s" % review_id
        data = self.simpleQuery(query)
        changeid = None
        for record in data:
            if _get_value(record, 'id') == review_id:
                changeid = self._formatCurrentChangeId(record)
                if changeid is not None:
                    break
        return changeid

    def _findCommitInGerritMaster(self, project, commit_id):
        if self.master is not None:
            return self.master._findCommitInGerrit(project, commit_id)
        return (None, None)

    def _processChangeRestoredOrAbandonedEvent(self, event, action, changeid):
        project = _get_value(event, ['change', 'project'])
        review_id = _get_value(event, ['change', 'id'])
        self.log.debug("DBG: _processChangeRestoredOrAbandonedEvent: %s: %s: %s" % (project, review_id, action))
        err = self.review(project, changeid, None, action)
        self.log.debug("DBG: _processChangeRestoredOrAbandonedEvent: gerrit review result: %s" % err)

    def _processChangeMergedEvent(self, event):
        project = _get_value(event, ['change', 'project'])
        review_id = _get_value(event, ['change', 'id'])
        self.log.debug("DBG: _processChangeMergedEvent: project %s: review_id: %s" % (project, review_id))
        data = self._findReviewInGerrit(project, review_id)
        if data is None:
            self.log.debug("DBG: _processChangeMergedEvent: cannot find review")
        else:
            status = _get_value(data, 'status')
            if status is None:
                status = _get_value(data, ['change', 'status'])
            if status == 'MERGED':
                self.log.debug("DBG: _processChangeMergedEvent: merged in replica: nothing todo")
                return
            self.log.debug("DBG: _processChangeMergedEvent: not merged in replica: abandon and reclone from master")
            changeid = self._getCurrentChangeId(event)
            if changeid is None:
                self.log.debug("DBG: _processChangeMergedEvent: review is not replicated")
            else:
                action = {'abandon': True}
                self._processChangeRestoredOrAbandonedEvent(event, action, changeid)
        self._fullCloneFromMaster(event)

    def _processCommentAddedEvent(self, event):
        project = _get_value(event, ['change', 'project'])
        review_id = _get_value(event, ['change', 'id'])
        self.log.debug("DBG: _processCommentAddedEvent: %s: %s" % (project, review_id))
        actions = {}
        message = None
        approvals = _get_value(event, 'approvals')
        if approvals is not None:
            for a in approvals:
                t = _get_value(a, 'type')
                v = _get_value(a, 'value')
                if t == 'Code-Review':
                    actions['code-review'] = v
# SKIP APPROVED TO AVOID MERGES
                # elif t == 'Approved':
                #     actions['approved'] = v
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
        changeid = self._getCurrentChangeId(event)
        if changeid is None:
            # review is not replicated yet, push new
            changeid = self._processPatchSetEvent(event)
            return
        err = self.review(project, changeid, message, actions)
        self.log.debug("DBG: _processChangeMergedEvent: gerrit review result: %s" % err)

    def _fullCloneFromMaster(self, event):
        project = _get_value(event, ['change', 'project'])
        url = _get_value(event, ['change', 'url'])
        if not url:
            self.log.debug("DBG: _fullCloneFromMaster: skip full clone, epmty url for change")
            return
        project_path = '/var/gerrit/git/%s.git' % project
        cmd = "docker exec -t gerrit_gerrit_1 rm -rf %s " % project_path
        out, err = self._ssh_gerrit_host(cmd)
        self.log.debug("DBG: _fullCloneFromMaster: rm cur folder: out: %s: err: %s" % (out, err))
        remote = '%s.git' % self._getRemote(project, url)
        cmd = "docker exec -t gerrit_gerrit_1 git clone --mirror %s %s" % (remote, project_path)
        out, err = self._ssh_gerrit_host(cmd)
        self.log.debug("DBG: _fullCloneFromMaster: git clone: %s: %s" % (out, err))

    def _open_ssh_gerrit_host(self):
        if self.ssh_gerrit_client:
            # Paramiko needs explicit closes, its possible we will open even
            # with an unclosed client so explicitly close here.
            self.ssh_gerrit_client.close()
        try:
            client = paramiko.SSHClient()
            client.load_system_host_keys()
            client.set_missing_host_key_policy(paramiko.WarningPolicy())
            client.connect(self.server,
                           username=self.user,
                           port=22,
                           key_filename=self.keyfile)
            transport = client.get_transport()
            transport.set_keepalive(self.keepalive)
            self.ssh_gerrit_client = client
        except Exception:
            client.close()
            self.ssh_gerrit_client = None
            raise

    def _ssh_gerrit_host(self, command, stdin_data=None):
        if not self.ssh_gerrit_client:
            self._open_ssh_gerrit_host()

        try:
            self.log.debug("SSH command:\n%s" % command)
            stdin, stdout, stderr = self.ssh_gerrit_client.exec_command(command)
        except Exception:
            self._open_ssh_gerrit_host()
            stdin, stdout, stderr = self.ssh_gerrit_client.exec_command(command)

        if stdin_data:
            stdin.write(stdin_data)

        out = stdout.read().decode('utf-8')
        self.iolog.debug("SSH received stdout:\n%s" % out)

        ret = stdout.channel.recv_exit_status()
        self.log.debug("SSH exit status: %s" % ret)

        err = stderr.read().decode('utf-8')
        if err.strip():
            self.log.debug("SSH received stderr:\n%s" % err)

        if ret:
            self.log.debug("SSH received stdout:\n%s" % out)
            raise Exception("Gerrit error executing %s" % command)
        return (out, err)

    def abandonAll(self):
        self.log.debug("DBG: abandonAll")
        query = "owner:%s status:open" % self.user
        data = self.simpleQuery(query)
        action = {'abandon': True}
        for record in data:
            changeid = self._formatCurrentChangeId(record)
            if changeid is None:
                self.log.debug("DBG: abandonAll: cannot get changeid - skipped")
                continue
            self._processChangeRestoredOrAbandonedEvent(event, action, changeid)

    def _currentPatchSet2ChangeEvent(self, data):
        change = _get_value(data, 'change')
        if change is None:
            change = {}
            change['id'] = _get_value(data, 'id')
            change['project'] = _get_value(data, 'project')
            change['branch'] = _get_value(data, 'branch')
            change['number'] = _get_value(data, 'number')
            change['url'] = _get_value(data, 'url')
            change['commitMessage'] = _get_value(data, 'commitMessage')
            data['change'] = change
        patchSet = _get_value(data, 'patchSet')
        if patchSet is None:
            patchSet = {}
            patchSet['number'] = _get_value(data, ['currentPatchSet', 'number'])
            patchSet['ref'] = _get_value(data, ['currentPatchSet', 'ref'])
            patchSet['parents'] = _get_value(data, ['currentPatchSet', 'parents'])
            data['patchSet'] = patchSet
        return data

    def pushAllOpenedReviews(self):
        self.log.debug("DBG: pushAllOpenedReviews")
        for p in REPLICATE_PROJECTS:
            data = self.master._getAllOpenedReviews(p)
            for record in data:
                event = self._currentPatchSet2ChangeEvent(record)
                if self._filterEvent(event):
                    continue
                self._fullCloneFromMaster(event)
                self._processPatchSetEvent(event)

    def _pauseForGerrit(self):
        self.gerrit_event_connector._pauseForGerrit()

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


class GerritConnectionMaster(GerritConnectionReplicationBase):
    log = logging.getLogger("zuul.GerritConnectionMaster")
    iolog = logging.getLogger("zuul.GerritConnectionMaster.io")

    def __init__(self, driver, connection_name, connection_config):
        super(GerritConnectionMaster, self).__init__(
            driver, connection_name, connection_config)
        self.slave = None
        self.merger = None

    def setMerger(self, merger):
        self.merger = merger

    def setSlave(self, slave):
        self.slave = slave

    def addEvent(self, event):
        if not self.slave:
            return
        return self.slave.addEvent(event)

    def _getReviewIdByCommit(self, project, commit_id):
        repo = self.merger.getRepo(self.connection_name, project)
        git_repo = repo.createRepoObject()
        git_repo.git.checkout(commit_id)
        res = REVIEW_ID_RE.search(git_repo.head.commit.message)
        self.log.debug("DBG: _getReviewIdByCommit: project: %s, commit: %s, message: %s" % (project, commit_id, git_repo.head.commit.message))
        if res is None:
            return None
        return res.group(0).split()[1]

    def _getAllOpenedReviews(self, project):
        query = "project:%s status:open" % project
        data = self.simpleQuery(query)
        return data

    def _findCommitInGerrit(self, project, commit_id): 
        review_id = self._getReviewIdByCommit(project, commit_id)
        if review_id is None:
            self.log.debug("DBG: _findCommitInGerrit: review not found")
            return (None, None)
        return (review_id, self._findReviewInGerrit(project, review_id))

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

    parser = argparse.ArgumentParser()
    parser.add_argument('cmd', default='sync')
    args = parser.parse_args()

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

    merge_email = 'zuul@gerrit'
    merge_name = 'zuul'
    speed_limit = '1000'
    speed_time = '30'
    
    merger_slave = merger.Merger(
        '/home/zuul/replica/slave/merger-git',
        registry, merge_email, merge_name,
        speed_limit, speed_time)

    merger_master = merger.Merger(
        '/home/zuul/replica/master/merger-git',
        registry, merge_email, merge_name,
        speed_limit, speed_time)

    connection_slave.setMaster(connection_master)
    connection_slave.setMerger(merger_slave)
    connection_master.setMerger(merger_master)
    connection_master.setSlave(connection_slave)
    if args.cmd == 'sync':
        connection_slave.onLoad()
        connection_master.onLoad()

        try:
            while(True):
                time.sleep(1)
        except KeyboardInterrupt as e:
            print("DBG: KeyboardInterrupt: %s" % e)

    elif args.cmd == 'abandon_synced_reviews':
        connection_slave.abandonAll()
    elif args.cmd == 'push_opened_reviews':
        connection_slave.pushAllOpenedReviews()

    connection_slave.onStop()
    connection_master.onStop()
    connection_master.setSlave(None)
    connection_slave.setMaster(None)
    print("DBG: exit")
    sys.exit(0)