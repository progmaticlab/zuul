This is special fork of zuul project that came from Juniper. It has some fixes that are absent in upstream but these fixes are required to work with vexxhost and in new TF CI. Branch 'contrail/feature/zuulv3' is used for deploying TF CI.

Zuul
====

Zuul is a project gating system.

The latest documentation for Zuul v3 is published at:
https://docs.openstack.org/infra/zuul/

If you are looking for the Edge routing service named Zuul that is
related to Netflix, it can be found here:
https://github.com/Netflix/zuul

If you are looking for the Javascript testing tool named Zuul, it
can be found here:
https://github.com/defunctzombie/zuul

Getting Help
------------

There are two Zuul-related mailing lists:

`zuul-announce <http://lists.zuul-ci.org/cgi-bin/mailman/listinfo/zuul-announce>`_
  A low-traffic announcement-only list to which every Zuul operator or
  power-user should subscribe.

`zuul-discuss <http://lists.zuul-ci.org/cgi-bin/mailman/listinfo/zuul-discuss>`_
  General discussion about Zuul, including questions about how to use
  it, and future development.

You will also find Zuul developers in the `#zuul` channel on Freenode
IRC.

Contributing
------------

To browse the latest code, see: https://git.openstack.org/cgit/openstack-infra/zuul/tree/
To clone the latest code, use `git clone git://git.openstack.org/openstack-infra/zuul`

Bugs are handled at: https://storyboard.openstack.org/#!/project/679

Code reviews are handled by gerrit at https://review.openstack.org

After creating a Gerrit account, use `git review` to submit patches.
Example::

    # Do your commits
    $ git review
    # Enter your username if prompted

Join `#zuul` on Freenode to discuss development or usage.

License
-------

Zuul is free software.  Most of Zuul is licensed under the Apache
License, version 2.0.  Some parts of Zuul are licensed under the
General Public License, version 3.0.  Please see the license headers
at the tops of individual source files.

Python Version Support
----------------------

Zuul v3 requires Python 3. It does not support Python 2.

As Ansible is used for the execution of jobs, it's important to note that
while Ansible does support Python 3, not all of Ansible's modules do. Zuul
currently sets ``ansible_python_interpreter`` to python2 so that remote
content will be executed with Python 2.
