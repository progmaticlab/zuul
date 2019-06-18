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
    "Juniper/contrail-analytics",
    "Juniper/contrail-ansible",
    "Juniper/contrail-ansible-deployer",
    "Juniper/contrail-ansible-internal",
    "Juniper/contrail-api-client",
    "Juniper/contrail-build",
    "Juniper/contrail-common",
    "Juniper/contrail-community-docs",
    "Juniper/contrail-container-builder",
    "Juniper/contrail-controller",
    "Juniper/contrail-deployers-containers",
    "Juniper/contrail-dev-env",
    "Juniper/contrail-docker",
    "Juniper/contrail-docs",
    "Juniper/contrail-dpdk",
    "Juniper/contrail-fabric-utils",
    "Juniper/contrail-generateDS",
    "Juniper/contrail-go-api",
    "Juniper/contrail-heat",
    "Juniper/contrail-helm-deployer",
    "Juniper/contrail-horizon",
    "Juniper/contrail-infra",
    "Juniper/contrail-infra-doc",
    "Juniper/contrail-java-api",
    "Juniper/contrail-kolla-ansible",
    "Juniper/contrail-neutron-plugin",
    "Juniper/contrail-nova-vif-driver",
    "Juniper/contrail-packages",
    "Juniper/contrail-packaging",
    "Juniper/contrail-provisioning",
    "Juniper/contrail-publisher",
    "Juniper/contrail-puppet",
    "Juniper/contrail-sandesh",
    "Juniper/contrail-server-manager",
    "Juniper/contrail-specs",
    "Juniper/contrail-test",
    "Juniper/contrail-test-ci",
    "Juniper/contrail-third-party",
    "Juniper/contrail-third-party-cache",
    "Juniper/contrail-third-party-packages",
    "Juniper/contrail-tripleo-heat-templates",
    "Juniper/contrail-tripleo-puppet",
    "Juniper/contrail-vcenter-fabric-manager",
    "Juniper/contrail-vcenter-manager",
    "Juniper/contrail-vcenter-plugin",
    "Juniper/contrail-vnc",
    "Juniper/contrail-vro-plugin",
    "Juniper/contrail-vrouter",
    "Juniper/contrail-vrouter-java-api",
    "Juniper/contrail-web-controller",
    "Juniper/contrail-web-core",
    "Juniper/contrail-web-server-manager",
    "Juniper/contrail-web-storage",
    "Juniper/contrail-webui-third-party",
    "Juniper/contrail-windows",
    "Juniper/contrail-windows-docker-driver",
    "Juniper/contrail-windows-test",
    "Juniper/horizon",
    "Juniper/nova",
    "Juniper/openshift-ansible",
    "Juniper/openstack-helm",
    "Juniper/openstack-helm-infra",
    "Juniper/puppet-contrail",
    "Juniper/vijava",
]
# Dont track
#   "Juniper/contrail-project-config",
#   "Juniper/contrail-zuul-jobs",


REPLICATE_BRANCHES = [
    'master',
    'stable/queens',
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
    def __init__(self, driver, connection_name, connection_config):
        super(GerritConnectionReplicationBase, self).__init__(
            driver, connection_name, connection_config)
        self.merger = None

    def setMerger(self, merger):
        self.merger = merger

    def _findReviewInGerrit(self, review_id, branch = None, status = None): 
        self.log.debug("DBG: _findReviewInGerrit: review_id=%s branch=%s status=%s" % (review_id, branch, status))
        query = "change:%s" % review_id
        data = self.simpleQuery(query)
        self.log.debug("DBG: _findReviewInGerrit: data: %s" % data)
        res = None
        for record in data:
            if branch is not None and branch != _get_value(record, 'branch'):
                continue
            if status is not None and status != _get_value(record, 'status'):
                continue
            res = record
            break
        return res

    def _getReviewIdByCommit(self, project, commit_id):
        repo = self.merger.getRepo(self.connection_name, project)
        repo.update()
        git_repo = repo.createRepoObject()
        try:
            for c in git_repo.iter_commits(rev=commit_id):
                self.log.debug("DBG: _getReviewIdByCommit: commit: %s" % c)
                msg = c.message.strip()
                res = REVIEW_ID_RE.search(msg)
                if res is not None:
                    return res.group(0).split()[1]
                self.log.debug("DBG: _getReviewIdByCommit: skip commit with message: %s" % msg)

        except Exception:
            # commit not found
            pass

        return None

    def _findCommitInGerrit(self, project, branch, commit_id): 
        review_id = self._getReviewIdByCommit(project, commit_id)
        if review_id is None:
            self.log.debug("DBG: _findCommitInGerrit: review not found")
            return (None, None)
        return (review_id, self._findReviewInGerrit(review_id, branch=branch))

    def _getAllOpenedReviews(self, project):
        query = "project:%s status:open" % project
        for i in range(1, 3):
            try:
                data = self.simpleQuery(query)
                return data
            except Exception as e:
                if i == 3:
                    self.log.debug("DBG: _getAllOpenedReviews: Exception: %s" % e)
        return []

    def _countAllReviews(self, project):
        counter = 0
        query = "project:%s " % project
        for i in range(1, 3):
            try:
                data = self.simpleQuery(query)
                for i in data :
                    print("DBG: _countAllReviews: data: %s" % i)
                    d = _get_value(i , 'status')
                    counter+= 1
            except Exception as e:
                if i == 3:
                    self.log.debug("DBG: _countAllReviews: Exception: %s" % e)
        return counter

    def _countOpenedReviews(self, project):
        counter = 0
        query = "project:%s " % project
        for i in range(1, 3):
            try:
                data = self.simpleQuery(query)
                for i in data :
                    print("DBG: _countAllReviews: data: %s" % i)
                    d = _get_value(i , 'status')
                    if d != "ABANDONED":
                        counter+= 1
            except Exception as e:
                if i == 3:
                    self.log.debug("DBG: _countAllReviews: Exception: %s" % e)
        return counter

class GerritEventConnectorSlave(GerritEventConnector):
    log = logging.getLogger("zuul.GerritEventConnectorSlave")

    def __init__(self, connection):
        super(GerritEventConnectorSlave, self).__init__(connection)

    def _handleEvent(self):
        ts, event = self.connection.getEvent()
        # pause see details in base class
        self._pauseForGerrit(ts=ts)
        if self._stopped:
            return
        self.connection.doReplicateEvent(event)

    def _addEvent(self, event):
        pass

    def _getChange(self, event):
        pass

    def _pauseForGerrit(self, ts=None):
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
        self.master = None
        self.ssh_gerrit_client = None

    def setMaster(self, master):
        self.master = master

    def doReplicateEvent(self, event):
        if self._filterEvent(event):
            return

        change_type = _get_value(event, 'type')
        if change_type is None:
            change_type = _get_value(event, ['change', 'type'])

        if change_type in ['change-created', 'patchset-created']:
            return self._processPatchSetEvent(event)

        if change_type == 'change-restored':
            return self._processChangeRestoredEvent(event)

        if change_type == 'change-abandoned':
            return self._processChangeAbandonedEvent(event)

        if change_type == 'change-merged':
            return self._processChangeMergedEvent(event)

        if change_type == 'comment-added':
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

    def _checkoutFromRemote(self, repo, remote, ref):
        repo.fetchFrom(remote, ref)
        git_repo = repo.createRepoObject()
        git_repo.git.checkout("FETCH_HEAD")
        return git_repo.head.commit

    def _cherryPickFromRemote(self, repo, remote, ref):
        repo.checkout('master')
        repo.fetchFrom(remote, ref)
        git_repo = repo.createRepoObject()
        git_repo.git.cherry_pick("FETCH_HEAD")
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

    def _processPatchSetEvent(self, event, process_parents=True):
        commit = None
        project = _get_value(event, ['change', 'project'])
        branch = _get_value(event, ['change', 'branch'])
        review_id = _get_value(event, ['change', 'id'])
        self.log.debug("DBG: _processPatchSetEvent: project=%s, branch=%s, review=%s" % (project, branch, review_id))
        url = _get_value(event, ['change', 'url'])
        ref = _get_value(event, ['patchSet', 'ref'])
        changeid = self._getCurrentChangeId(event)
        if changeid is None:
            # review is not replicated yet
            # for the first patch set ensure that there will be the same parent 
            for parent in _get_value(event, ['patchSet', 'parents']):
                parent_review_id, parent_event = self._findCommitInGerritMaster(project, branch, parent)
                if parent_review_id is None:
                    self.log.debug("DBG: _processPatchSetEvent: %s: cannot find review id for parent commit %s: skip" %(review_id, parent))
                    return None
                #patch parent event if it has no change inside )it is for merged changes)
                parent_event = self._currentPatchSet2ChangeEvent(parent_event)
                # parent found on master
                parent_changeid = self._getCurrentChangeId(parent_event)
                if parent_changeid is not None:
                    # parent already commited
                    self.log.debug("DBG: _processPatchSetEvent: parent:  %s: already commited" % parent_review_id)
                    continue
                # parent should be pushed first to keep the same commits order
                if self._processPatchSetEvent(parent_event) is None:
                    self.log.debug("DBG: _processPatchSetEvent: failed to push parent %s: skip the child" % parent_review_id)
                    return None
        # process the event itself
        remote = self._getRemote(project, url)
        repo = self.merger.getRepo(self.connection_name, project)
        commit = self._cherryPickFromRemote(repo, remote, ref)
        self.log.debug("DBG: _processPatchSetEvent: commit=%s" % commit)
        # reset author to default (zuul)
        new_message = 'Initial Review: %s\n\n%s' % (url, _get_value(event, ['change', 'commitMessage']))
        commit = self._amendCommitMessage(repo, message=new_message)
        self.log.debug("DBG: _processPatchSetEvent: amended commit=%s" % commit)
        # public changes to gerrit
        repo.push('HEAD', 'refs/publish/%s' % branch)
        self._pauseForGerrit()
        return self._getCurrentChangeId(event)

    def _processChangeRestoredEvent(self, event, message='recheck'):
        action = {'restore': True}
        changeid = self._getCurrentChangeId(event)
        if changeid is None:
            # push as new
            self._processPatchSetEvent(event)
        else:
            self._processChangeRestoredOrAbandonedEvent(event, action, changeid, message=message)

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

    def _findCommitInGerritMaster(self, project, branch, commit_id):
        if self.master is not None:
            return self.master._findCommitInGerrit(project, branch, commit_id)
        return (None, None)

    def _processChangeRestoredOrAbandonedEvent(self, event, action, changeid, message=None):
        project = _get_value(event, ['change', 'project'])
        review_id = _get_value(event, ['change', 'id'])
        self.log.debug("DBG: _processChangeRestoredOrAbandonedEvent: %s: %s: %s" % (project, review_id, action))
        err = self.review(project, changeid, None, action)
        self.log.debug("DBG: _processChangeRestoredOrAbandonedEvent: gerrit review result: %s" % err)
        if message is not None:
            err = self.review(project, changeid, message)
            self.log.debug("DBG: _processChangeRestoredOrAbandonedEvent: gerrit review result: %s" % err)

    def _processChangeMergedEvent(self, event):
        project = _get_value(event, ['change', 'project'])
        branch = _get_value(event, ['change', 'branch'])
        review_id = _get_value(event, ['change', 'id'])
        self.log.debug("DBG: _processChangeMergedEvent: project %s: review_id: %s" % (project, review_id))
        data = self._findReviewInGerrit(review_id, branch=branch)
        if data is None:
            self.log.debug("DBG: _processChangeMergedEvent: cannot find review: nothing todo")
            return
        status = _get_value(data, 'status')
        if status is None:
            status = _get_value(data, ['change', 'status'])
        if status == 'MERGED':
            self.log.debug("DBG: _processChangeMergedEvent: merged in replica: nothing todo")
            return
        changeid = self._getCurrentChangeId(event)
        if changeid is None:
            self.log.debug("DBG: _processChangeMergedEvent: review is not replicated")
            return
        self.log.debug("DBG: _processChangeMergedEvent: FORCE_VERIVIED")
        actions = {
            'code-review': '2',
            'approved': '1'
        }
        self._processChangeRestoredOrAbandonedEvent(event, actions, changeid)

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
        approvals = _get_value(data, 'approvals')
        if approvals is None:
            approvals = _get_value(data, ['currentPatchSet', 'approvals'])
            if approvals is not None:
                data['approvals'] = approvals
        return data

    def abandonAll(self, projects=None):
        self.log.debug("DBG: abandonAll")
        query = "owner:%s status:open" % self.user
        data = self.simpleQuery(query)
        action = {'abandon': True}
        for record in data:
            prj = _get_value(record, 'project')
            if projects is not None and prj not in projects:
                self.log.debug("DBG: abandonAll: %s skipped" % prj)
                continue
            changeid = self._formatCurrentChangeId(record)
            if changeid is None:
                self.log.debug("DBG: abandonAll: cannot get changeid - skipped")
                continue
            event = self._currentPatchSet2ChangeEvent(record)
            self._processChangeRestoredOrAbandonedEvent(event, action, changeid)

    def pushAllOpenedReviews(self, projects=None):
        self.log.debug("DBG: pushAllOpenedReviews")
        events_list = []
        for p in REPLICATE_PROJECTS:
            if projects is not None and p not in projects:
                self.log.debug("DBG: pushAllOpenedReviews: %s skipped" % p)
                continue
            data = self.master._getAllOpenedReviews(p)
            for record in data:
                event = self._currentPatchSet2ChangeEvent(record)
                if self._filterEvent(event):
                    continue
                events_list += [event]
        for event in events_list:
            project = _get_value(event, ['change', 'project'])
            review_id = _get_value(event, ['change', 'id'])
            branch = _get_value(event, ['change', 'branch'])
            data = self._findReviewInGerrit(review_id, branch=branch)
            if data is None:
                self._processPatchSetEvent(event)
            else:
                status = _get_value(data, 'status')
                if status is None:
                    status = _get_value(data, ['change', 'status'])
                if status == 'ABANDONED':
                    # restore event
                    self._processChangeRestoredEvent(event)
                else:
                    self.log.debug(
                        "DBG: pushAllOpenedReviews: review_id %s , status = %s : already pushed - skipped" % (
                            review_id, status))

    def pushReviews(self, reviews=None, branch='master'):
        self.log.debug("DBG: pushReviews")
        events_list = []
        for review in reviews:
            data = self.master._findReviewInGerrit(review, branch=branch)
            if data is None:
                self.log.debug("DBG: pushReviews: cannot find review %s on master" % review)
                continue
            event = self._currentPatchSet2ChangeEvent(data)
            if self._filterEvent(event):
                continue
            events_list += [event]
        for event in events_list:
            review_id = _get_value(event, ['change', 'id'])
            data = self._findReviewInGerrit(review_id, branch=branch)
            status = 'NEW' if data is None else _get_value(data, ['change', 'status'])
            if status == 'ABANDONED':
                # restore event
                self._processChangeRestoredEvent(event)
            # apply latest change if any
            self._processPatchSetEvent(event)

    def recloneProjectsWithOpenedReviews(self, projects=None):
        self.log.debug("DBG: recloneProjectsWithOpenedReviews")
        events_list = []
        for p in REPLICATE_PROJECTS:
            if projects is not None and p not in projects:
                self.log.debug("DBG: recloneProjectsWithOpenedReviews: %s skipped" % p)
                continue
            data = self._getAllOpenedReviews(p)
            if len(data) > 0:
                # skip if there are opened reviews otherwise replacing git repo
                # leads to broken gerrit
                self.log.debug("DBG: recloneProjectsWithOpenedReviews: skip %s becase it has opened reviews")
                continue
            data = self.master._getAllOpenedReviews(p)
            for record in data:
                event = self._currentPatchSet2ChangeEvent(record)
                if self._filterEvent(event):
                    continue
                events_list += [event]
        cloned_projects = []
        for event in events_list:
            prj = _get_value(event, 'project')
            if prj not in cloned_projects:
                cloned_projects += [prj]
                self._fullCloneFromMaster(event)

    def recheckFailedOpenedReviews(self, projects=None):
        self.log.debug("DBG: recheckOpenedReviews")
        events_list = []
        for p in REPLICATE_PROJECTS:
            if projects is not None and p not in projects:
                self.log.debug("DBG: recheckFailedOpenedReviews: %s skipped" % p)
                continue
            data = self._getAllOpenedReviews(p)
            for record in data:
                event = self._currentPatchSet2ChangeEvent(record)
                if self._filterEvent(event):
                    continue
                approvals = _get_value(event, 'approvals')
                if approvals is None:
                    self.log.debug("DBG: recheckOpenedReviews: no approvals yet: skipped")
                    continue
                verified = ''
                for a in approvals:
                    if _get_value(a, 'type') != 'Verified':
                        continue
                    verified = _get_value(a, 'value')
                    break
                if verified != '-1':
                    self.log.debug("DBG: recheckOpenedReviews: verified approvals %s: skipped" % verified)
                    continue
                events_list += [event]
        self.log.debug("DBG: recheckOpenedReviews: events_list: %s" % events_list)
        for event in events_list:
            project = _get_value(event, 'project')
            changeid = self._formatCurrentChangeId(event)
            err = self.review(project, changeid, 'recheck')
            self.log.debug("DBG: recheckFailedOpenedReviews: gerrit review recheck: %s" % err)

    def _pauseForGerrit(self):
        if self.gerrit_event_connector:
            self.gerrit_event_connector._pauseForGerrit()

    def _start_watcher_thread(self):
        pass

    def _start_event_connector(self):
        self.gerrit_event_connector = GerritEventConnectorSlave(self)
        self.gerrit_event_connector.start()

    def compareReviewStates(self, output = None , projects = ''):
        self.log.debug("DBG: compareReviewStates")
        diverged_reviews = []
        total_length = 0
        project_summary = []
        output_file = None
        if output is not None:
            try:
                output_file = open(output , 'w')
            except Exception as e:
                self.log.debug("DBG: compareReviewStates: Can`t open file %s for writing , exception: %s" % ( output ,  e))
                return

        for p in REPLICATE_PROJECTS:
            project_reviews_opened_total = 0
            project_reviews_failed = 0
            if len(projects) > 1 and p not in projects:
                self.log.debug("DBG: compareReviewStates: %s skipped" % p)
                continue
            data = self._getAllOpenedReviews(p)
            project_reviews_total = self._countAllReviews(p)
            total_length += len(data)
            for slave_review in data:
                project_reviews_opened_total += 1
                slave_approval_value = "n/a"
                master_approval_value = "n/a"
                slave_approval = _get_value(slave_review, ['currentPatchSet', 'approvals'])
                if slave_approval is not None:
                    for i in slave_approval:
                        if "value" in i.keys():
                            slave_approval_value = i.get('value')
                slave_url = _get_value(slave_review, ['url'])
                slave_review_id = _get_value(slave_review, 'id')
                branch = _get_value(slave_review, 'branch')
                master_review = self.master._findReviewInGerrit(slave_review_id, branch=branch)
                if master_review is None:
                    res = "n/a\tn/a\t%s\t%s\t" % (
                        slave_url,
                        slave_approval_value)
                    project_reviews_failed += 1
                    diverged_reviews.append(res)
                    continue
                master_approval = _get_value(master_review, ['currentPatchSet', 'approvals'])
                if master_approval is not None:
                    for i in master_approval:
                        if "value" in i.keys():
                            master_approval_value = i.get('value')
                if not (slave_approval_value == master_approval_value or (
                        slave_approval_value == "n/a" == master_approval_value )):
                    master_url = _get_value(master_review, ['url'])
                    slave_url = _get_value(slave_review, ['url'])
                    res = "%s\t%s\t%s\t%s\t" % (
                             slave_approval_value , master_approval_value, slave_url, master_url)
                    project_reviews_failed += 1
                    diverged_reviews.append(res)
            project_summary.append(("%s\t%s\t%s\t%s\t") % (p , project_reviews_total  , project_reviews_opened_total  , project_reviews_failed))
        print("|SLAVE_APPROVAL|\t|MASTER_APPROVAL|\t|SLAVE_URL|\t|MASTER_URL|\t" , file=output_file)
        for diverged_review in diverged_reviews:
            print(diverged_review , file=output_file)
        print("Project\tTotal: all \topened\tFailed" , file=output_file)
        total_all = 0
        total_opened = 0
        total_failed = 0
        for project in project_summary:
            print(project , file = output_file)
            total_all += int(project.split('\t')[1])
            total_opened += int(project.split('\t')[2])
            total_failed += int(project.split('\t')[3])
        print("____\t____\t____\t____", file=output_file)
        print("TOTAL:\t%s\t%s\t%s" %(total_all , total_opened , total_failed) )


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

    parser = argparse.ArgumentParser()
    parser.add_argument('cmd', default='sync')
    parser.add_argument('--projects', default='')
    parser.add_argument('--reviews', default='')
    parser.add_argument('--output' , default=None , help="Name for outputfile. Output in stdout by default")

    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG)

    config_master = {
        "name": "gerrit_master",
        "driver": "gerrit",
        "sshkey": "/var/ssh/zuul_rsa",
        "server": "review.opencontrail.org",
        "user": "alexey-mr",
        "baseurl": "https://review.opencontrail.org"
    }

    config_slave = {
        "name": "gerrit_slave",
        "driver": "gerrit",
        "sshkey": "/var/ssh/zuul_rsa",
        "server": "gerrit",
        "user": "zuul",
        "baseurl": "http://gerrit",
    }

    print(os.environ)
    home = os.environ['HOME']
    path = os.environ['PATH']
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
            while (True):
                time.sleep(1)
        except KeyboardInterrupt as e:
            print("DBG: KeyboardInterrupt: %s" % e)

    elif args.cmd == 'abandon_synced_reviews':
        projects = args.projects.split(',')
        connection_slave.abandonAll(projects=projects)
    elif args.cmd == 'push_opened_reviews':
        projects = args.projects.split(',')
        connection_slave.pushAllOpenedReviews(projects=projects)
    elif args.cmd == 'reclone_for_opened_reviews':
        projects = args.projects.split(',')
        connection_slave.recloneProjectsWithOpenedReviews(projects=projects)
    elif args.cmd == 'recheck_failed_opened_reviews':
        projects = args.projects.split(',')
        connection_slave.recheckFailedOpenedReviews(projects=projects)
    elif args.cmd == 'compare_review_states':
        output = args.output
        projects = args.projects.split(',')
        connection_slave.compareReviewStates(projects=projects , output=output)
    elif args.cmd == 'push_reviews':
        reviews = args.reviews.split(',')
        connection_slave.pushReviews(reviews=reviews)

    connection_slave.onStop()
    connection_master.onStop()
    connection_master.setSlave(None)
    connection_slave.setMaster(None)
    print("DBG: exit")
    sys.exit(0)
