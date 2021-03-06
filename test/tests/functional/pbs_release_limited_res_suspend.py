# coding: utf-8

# Copyright (C) 1994-2016 Altair Engineering, Inc.
# For more information, contact Altair at www.altair.com.
#
# This file is part of the PBS Professional ("PBS Pro") software.
#
# Open Source License Information:
#
# PBS Pro is free software. You can redistribute it and/or modify it under the
# terms of the GNU Affero General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# PBS Pro is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE. See the GNU Affero General Public License for more
# details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# Commercial License Information:
#
# The PBS Pro software is licensed under the terms of the GNU Affero General
# Public License agreement ("AGPL"), except where a separate commercial license
# agreement for PBS Pro version 14 or later has been executed in writing with
# Altair.
#
# Altair’s dual-license business model allows companies, individuals, and
# organizations to create proprietary derivative works of PBS Pro and
# distribute them - whether embedded or bundled with other software - under
# a commercial license agreement.
#
# Use of Altair’s trademarks, including but not limited to "PBS™",
# "PBS Professional®", and "PBS Pro™" and Altair’s logos is subject to Altair's
# trademark licensing policies.

import time
from tests.functional import *


class TestReleaseLimitedResOnSuspend(TestFunctional):
    """
    Test that based on admin's input only limited number of resources are
    released when suspending a running job.
    """

    def setUp(self):
        TestFunctional.setUp(self)
        # Set default resources available on the default mom
        a = {ATTR_rescavail+'.ncpus': 4, ATTR_rescavail+'.mem': '2gb'}
        self.server.manager(MGR_CMD_SET, NODE, a, self.mom.shortname)
        # Create an express queue
        b = {ATTR_qtype: 'Execution', ATTR_enable: 'True',
             ATTR_start: 'True', ATTR_p: '200'}
        self.server.manager(MGR_CMD_CREATE, QUEUE, b, "expressq")

    def test_do_not_release_mem_sched_susp(self):
        """
        During preemption by suspension test that only ncpus are released from
        the running job and memory is not released.
        """

        # Set restrict_res_to_release_on_suspend server attribute
        a = {ATTR_restrict_res_to_release_on_suspend: 'ncpus'}
        self.server.manager(MGR_CMD_SET, SERVER, a, expect=True)

        # Submit a low priority job
        j1 = Job(TEST_USER)
        j1.set_attributes({ATTR_l+'.select': '1:ncpus=4:mem=512mb'})
        jid1 = self.server.submit(j1)
        self.server.expect(JOB, {ATTR_state: 'R'}, id=jid1)

        # Submit a high priority job
        j2 = Job(TEST_USER)
        j2.set_attributes(
            {ATTR_l+'.select': '1:ncpus=2:mem=512mb',
             ATTR_q: 'expressq'})
        jid2 = self.server.submit(j2)
        self.server.expect(JOB, {ATTR_state: 'R'}, id=jid2)
        self.server.expect(JOB, {ATTR_state: 'S', ATTR_substate: 45}, id=jid1)

        ras_mem = ATTR_rescassn + '.mem'
        ras_ncpus = ATTR_rescassn + '.ncpus'

        rv = self.server.status(
            NODE, [ras_ncpus, ras_mem], id=self.mom.shortname)
        self.assertNotEqual(rv, None)

        self.assertEqual(rv[0][ras_mem], "1048576kb",
                         msg="pbs should not release memory")
        self.assertEqual(rv[0][ras_ncpus], "2",
                         msg="pbs did not release ncpus")

    def test_do_not_release_mem_qsig_susp(self):
        """
        If a running job is suspended using qsig, test that only ncpus are
        released from the running job and memory is not released.
        """

        # Set restrict_res_to_release_on_suspend server attribute
        a = {ATTR_restrict_res_to_release_on_suspend: 'ncpus'}
        self.server.manager(MGR_CMD_SET, SERVER, a, expect=True)

        # Submit a low priority job
        j1 = Job(TEST_USER)
        j1.set_attributes({ATTR_l+'.select': '1:ncpus=4:mem=512mb'})
        jid1 = self.server.submit(j1)
        self.server.expect(JOB, {ATTR_state: 'R'}, id=jid1)

        # suspend job
        self.server.sigjob(jobid=jid1, signal="suspend")

        ras_mem = ATTR_rescassn + '.mem'
        ras_ncpus = ATTR_rescassn + '.ncpus'

        rv = self.server.status(
            NODE, [ras_ncpus, ras_mem], id=self.mom.shortname)
        self.assertNotEqual(rv, None)

        self.assertEqual(rv[0][ras_mem], "524288kb",
                         msg="pbs should not release memory")
        self.assertEqual(rv[0][ras_ncpus], "0",
                         msg="pbs did not release ncpus")

    def test_change_in_res_to_release_on_suspend(self):
        """
        set restrict_res_to_release_on_suspend to only ncpus and then suspend
        a job after the job is suspended change
        restrict_res_to_release_on_suspend to release only memory and check
        if the suspended job resumes and do not account for memory twice.
        """

        # Set restrict_res_to_release_on_suspend server attribute
        a = {ATTR_restrict_res_to_release_on_suspend: 'ncpus'}
        self.server.manager(MGR_CMD_SET, SERVER, a, expect=True)

        # Submit a low priority job
        j1 = Job(TEST_USER)
        j1.set_attributes({ATTR_l+'.select': '1:ncpus=4:mem=512mb'})
        jid1 = self.server.submit(j1)
        self.server.expect(JOB, {ATTR_state: 'R'}, id=jid1)

        # Submit a high priority job
        j2 = Job(TEST_USER)
        j2.set_attributes(
            {ATTR_l+'.select': '1:ncpus=2:mem=256mb',
             ATTR_q: 'expressq'})
        jid2 = self.server.submit(j2)
        self.server.expect(JOB, {ATTR_state: 'R'}, id=jid2)
        self.server.expect(JOB, {ATTR_state: 'S', ATTR_substate: 45}, id=jid1)

        # Change restrict_res_to_release_on_suspend server attribute
        a = {ATTR_restrict_res_to_release_on_suspend: 'mem'}
        self.server.manager(MGR_CMD_SET, SERVER, a, expect=True)

        rc = 0
        try:
            rc = self.server.deljob(jid2, wait=True)
        except PbsDeljobError, e:
            self.assertEqual(rc, 0, e.msg[0])

        self.server.expect(JOB, {ATTR_state: 'R'}, id=jid1)
        ras_mem = ATTR_rescassn + '.mem'
        ras_ncpus = ATTR_rescassn + '.ncpus'

        rv = self.server.status(
            NODE, [ras_ncpus, ras_mem], id=self.mom.shortname)
        self.assertNotEqual(rv, None)

        self.assertEqual(rv[0][ras_mem], "524288kb",
                         msg="pbs did not account for memory correctly")
        self.assertEqual(rv[0][ras_ncpus], "4",
                         msg="pbs did not account for ncpus correctly")

    def test_res_released_sched_susp(self):
        """
        Test if job's resources_released attribute is correctly set when
        it is suspended.
        """

        # Set restrict_res_to_release_on_suspend server attribute
        a = {ATTR_restrict_res_to_release_on_suspend: 'ncpus'}
        self.server.manager(MGR_CMD_SET, SERVER, a, expect=True)

        # Submit a low priority job
        j1 = Job(TEST_USER)
        j1.set_attributes({ATTR_l+'.select': '1:ncpus=4:mem=512mb'})
        jid1 = self.server.submit(j1)
        self.server.expect(JOB, {ATTR_state: 'R'}, id=jid1)

        # Submit a high priority job
        j2 = Job(TEST_USER)
        j2.set_attributes(
            {ATTR_l+'.select': '1:ncpus=2:mem=512mb',
             ATTR_q: 'expressq'})
        jid2 = self.server.submit(j2)
        self.server.expect(JOB, {ATTR_state: 'R'}, id=jid2)
        self.server.expect(JOB, {ATTR_state: 'S', ATTR_substate: 45}, id=jid1)

        job = self.server.status(JOB, id=jid1)
        self.assertNotEqual(job, None)

        rr = "(%s:ncpus=4)" % self.mom.shortname
        self.assertEqual(job[0][ATTR_released], rr,
                         msg="resources_released incorrect")

    def test_res_released_sched_susp_multi_vnode(self):
        """
        Test if job's resources_released attribute is correctly set when
        a multi vnode job is suspended.
        """

        # Set restrict_res_to_release_on_suspend server attribute
        a = {ATTR_restrict_res_to_release_on_suspend: 'ncpus'}
        self.server.manager(MGR_CMD_SET, SERVER, a, expect=True)

        vn_attrs = {ATTR_rescavail + '.ncpus': 8,
                    ATTR_rescavail + '.mem': '1024mb'}
        self.server.create_vnodes("vnode1", vn_attrs, 1,
                                  self.mom, fname="vnodedef1")
        # Append a vnode
        vn_attrs = {ATTR_rescavail + '.ncpus': 6,
                    ATTR_rescavail + '.mem': '1024mb'}
        self.server.create_vnodes("vnode2", vn_attrs, 1,
                                  self.mom, additive=True, fname="vnodedef2")

        # Submit a low priority job
        j1 = Job(TEST_USER)
        j1.set_attributes({ATTR_l+'.select':
                           '1:ncpus=8:mem=512mb+1:ncpus=6:mem=256mb'})
        jid1 = self.server.submit(j1)
        self.server.expect(JOB, {ATTR_state: 'R'}, id=jid1)

        # Submit a high priority job
        j2 = Job(TEST_USER)
        j2.set_attributes(
            {ATTR_l+'.select': '1:ncpus=8:mem=256mb',
             ATTR_q: 'expressq'})
        jid2 = self.server.submit(j2)
        self.server.expect(JOB, {ATTR_state: 'R'}, id=jid2)
        self.server.expect(JOB, {ATTR_state: 'S', ATTR_substate: 45}, id=jid1)

        job = self.server.status(JOB, id=jid1)
        self.assertNotEqual(job, None)

        rr = "(vnode1[0]:ncpus=8)+(vnode2[0]:ncpus=6)"
        print job[0][ATTR_released]
        self.assertEqual(job[0][ATTR_released], rr,
                         msg="resources_released incorrect")

    def test_res_released_sched_susp_arrayjob(self):
        """
        Test if array subjob's resources_released attribute is correctly
        set when it is suspended.
        """

        # Set restrict_res_to_release_on_suspend server attribute
        a = {ATTR_restrict_res_to_release_on_suspend: 'ncpus'}
        self.server.manager(MGR_CMD_SET, SERVER, a, expect=True)

        # Submit a low priority job
        j1 = Job(TEST_USER)
        j1.set_attributes({ATTR_l+'.select': '1:ncpus=4:mem=512mb',
                           ATTR_J: '1-3'})
        jid1 = self.server.submit(j1)
        subjobs = self.server.status(JOB, id=jid1, extend='t')
        sub_jid1 = subjobs[1]['id']
        self.server.expect(JOB, {ATTR_state: 'R'}, id=sub_jid1)

        # Submit a high priority job
        j2 = Job(TEST_USER)
        j2.set_attributes(
            {ATTR_l+'.select': '1:ncpus=2:mem=512mb',
             ATTR_q: 'expressq'})
        jid2 = self.server.submit(j2)
        self.server.expect(JOB, {ATTR_state: 'R'}, id=jid2)
        self.server.expect(JOB, {ATTR_state: 'S', ATTR_substate: 45},
                           id=sub_jid1)

        job = self.server.status(JOB, id=sub_jid1)
        self.assertNotEqual(job, None)

        rr = "(%s:ncpus=4)" % self.mom.shortname
        self.assertEqual(job[0][ATTR_released], rr,
                         msg="resources_released incorrect")

    def test_res_released_list_sched_susp_arrayjob(self):
        """
        Test if array subjob's resources_released_list attribute is correctly
        set when it is suspended.
        """

        # Set restrict_res_to_release_on_suspend server attribute
        a = {ATTR_restrict_res_to_release_on_suspend: 'ncpus,mem'}
        self.server.manager(MGR_CMD_SET, SERVER, a, expect=True)

        # Submit a low priority job
        j1 = Job(TEST_USER)
        j1.set_attributes({ATTR_l+'.select': '1:ncpus=4:mem=512mb',
                           ATTR_J: '1-3'})
        jid1 = self.server.submit(j1)
        subjobs = self.server.status(JOB, id=jid1, extend='t')
        sub_jid1 = subjobs[1]['id']
        self.server.expect(JOB, {ATTR_state: 'R'}, id=sub_jid1)

        # Submit a high priority job
        j2 = Job(TEST_USER)
        j2.set_attributes(
            {ATTR_l+'.select': '1:ncpus=2:mem=256mb',
             ATTR_q: 'expressq'})
        jid2 = self.server.submit(j2)
        self.server.expect(JOB, {ATTR_state: 'R'}, id=jid2)
        self.server.expect(JOB, {ATTR_state: 'S', ATTR_substate: 45},
                           id=sub_jid1)

        job = self.server.status(JOB, id=sub_jid1)
        self.assertNotEqual(job, None)

        rr_l_ncpus = job[0][ATTR_rel_list + ".ncpus"]
        self.assertEqual(rr_l_ncpus, "4", msg="ncpus not released")
        rr_l_mem = job[0][ATTR_rel_list + ".mem"]
        self.assertEqual(rr_l_mem, "524288kb", msg="memory not released")

    def test_res_released_list_sched_susp(self):
        """
        Test if job's resources_released_list attribute is correctly set when
        it is suspended.
        """

        # Set restrict_res_to_release_on_suspend server attribute
        a = {ATTR_restrict_res_to_release_on_suspend: 'ncpus,mem'}
        self.server.manager(MGR_CMD_SET, SERVER, a, expect=True)

        # Submit a low priority job
        j1 = Job(TEST_USER)
        j1.set_attributes({ATTR_l+'.select': '1:ncpus=4:mem=512mb'})
        jid1 = self.server.submit(j1)
        self.server.expect(JOB, {ATTR_state: 'R'}, id=jid1)

        # Submit a high priority job
        j2 = Job(TEST_USER)
        j2.set_attributes(
            {ATTR_l+'.select': '1:ncpus=2:mem=256mb',
             ATTR_q: 'expressq'})
        jid2 = self.server.submit(j2)
        self.server.expect(JOB, {ATTR_state: 'R'}, id=jid2)
        self.server.expect(JOB, {ATTR_state: 'S', ATTR_substate: 45}, id=jid1)

        job = self.server.status(JOB, id=jid1)
        self.assertNotEqual(job, None)

        rr_l_ncpus = job[0][ATTR_rel_list + ".ncpus"]
        self.assertEqual(rr_l_ncpus, "4", msg="ncpus not released")
        rr_l_mem = job[0][ATTR_rel_list + ".mem"]
        self.assertEqual(rr_l_mem, "524288kb", msg="memory not released")

    def test_res_released_list_sched_susp_multi_vnode(self):
        """
        Test if job's resources_released_list attribute is correctly set when
        a multi vnode job is suspended.
        """

        # Set restrict_res_to_release_on_suspend server attribute
        a = {ATTR_restrict_res_to_release_on_suspend: 'ncpus,mem'}
        self.server.manager(MGR_CMD_SET, SERVER, a, expect=True)

        vn_attrs = {ATTR_rescavail + '.ncpus': 8,
                    ATTR_rescavail + '.mem': '1024mb'}
        self.server.create_vnodes("vnode1", vn_attrs, 1,
                                  self.mom, fname="vnodedef1")
        # Append a vnode
        vn_attrs = {ATTR_rescavail + '.ncpus': 6,
                    ATTR_rescavail + '.mem': '1024mb'}
        self.server.create_vnodes("vnode2", vn_attrs, 1,
                                  self.mom, additive=True, fname="vnodedef2")

        # Submit a low priority job
        j1 = Job(TEST_USER)
        j1.set_attributes({ATTR_l+'.select':
                           '1:ncpus=8:mem=512mb+1:ncpus=6:mem=256mb'})
        jid1 = self.server.submit(j1)
        self.server.expect(JOB, {ATTR_state: 'R'}, id=jid1)

        # Submit a high priority job
        j2 = Job(TEST_USER)
        j2.set_attributes(
            {ATTR_l+'.select': '1:ncpus=8:mem=256mb',
             ATTR_q: 'expressq'})
        jid2 = self.server.submit(j2)
        self.server.expect(JOB, {ATTR_state: 'R'}, id=jid2)
        self.server.expect(JOB, {ATTR_state: 'S', ATTR_substate: 45}, id=jid1)

        job = self.server.status(JOB, id=jid1)
        self.assertNotEqual(job, None)

        rr_l_ncpus = job[0][ATTR_rel_list + ".ncpus"]
        self.assertEqual(rr_l_ncpus, "14", msg="ncpus not released")
        rr_l_mem = job[0][ATTR_rel_list + ".mem"]
        self.assertNotEqual(rr_l_mem, "2097152kb", msg="memory not released")

    def test_node_res_after_deleting_suspended_job(self):
        """
        Test that once a suspended job is deleted node's resources assigned
        are back to 0.
        """

        # Set restrict_res_to_release_on_suspend server attribute
        a = {ATTR_restrict_res_to_release_on_suspend: 'ncpus'}
        self.server.manager(MGR_CMD_SET, SERVER, a, expect=True)

        # Submit a low priority job
        j1 = Job(TEST_USER)
        j1.set_attributes({ATTR_l+'.select': '1:ncpus=4:mem=512mb'})
        jid1 = self.server.submit(j1)
        self.server.expect(JOB, {ATTR_state: 'R'}, id=jid1)

        # suspend job
        self.server.sigjob(jobid=jid1, signal="suspend")
        self.server.expect(JOB, {ATTR_state: 'S', ATTR_substate: 43}, id=jid1)

        ras_mem = ATTR_rescassn + '.mem'
        ras_ncpus = ATTR_rescassn + '.ncpus'

        rv = self.server.status(
            NODE, [ras_ncpus, ras_mem], id=self.mom.shortname)
        self.assertNotEqual(rv, None)

        self.assertEqual(
            rv[0][ras_mem], "524288kb",
            msg="pbs did not retain memory correctly on the node")
        self.assertEqual(
            rv[0][ras_ncpus], "0",
            msg="pbs did not release ncpus correctly on the node")

        rc = 0
        try:
            rc = self.server.deljob(jid1, wait=True)
        except PbsDeljobError, e:
            self.assertEqual(rc, 0, e.msg[0])

        rv = self.server.status(
            NODE, [ras_ncpus, ras_mem], id=self.mom.shortname)
        self.assertNotEqual(rv, None)

        self.assertEqual(
            rv[0][ras_mem], "0kb",
            msg="pbs did not reassign memory correctly on the node")
        self.assertEqual(
            rv[0][ras_ncpus], "0",
            msg="pbs did not reassign ncpus correctly on the node")

    def test_default_restrict_res_released_on_suspend(self):
        """
        Test the default value of restrict_res_to_release_on_suspend.
        It should release all the resources by default.
        """
        # Submit a low priority job
        j1 = Job(TEST_USER)
        j1.set_attributes({ATTR_l+'.select': '1:ncpus=4:mem=512mb'})
        jid1 = self.server.submit(j1)
        self.server.expect(JOB, {ATTR_state: 'R'}, id=jid1)

        # Submit a high priority job
        j2 = Job(TEST_USER)
        j2.set_attributes(
            {ATTR_l+'.select': '1:ncpus=2:mem=256mb',
             ATTR_q: 'expressq'})
        jid2 = self.server.submit(j2)
        self.server.expect(JOB, {ATTR_state: 'R'}, id=jid2)
        self.server.expect(JOB, {ATTR_state: 'S', ATTR_substate: 45}, id=jid1)

        ras_mem = ATTR_rescassn + '.mem'
        ras_ncpus = ATTR_rescassn + '.ncpus'

        rv = self.server.status(
            NODE, [ras_ncpus, ras_mem], id=self.mom.shortname)
        self.assertNotEqual(rv, None)

        self.assertEqual(rv[0][ras_mem], "262144kb",
                         msg="pbs did not release memory")
        self.assertEqual(rv[0][ras_ncpus], "2",
                         msg="pbs did not release ncpus")

    def test_setting_unknown_resc(self):
        """
        Set a non existing resource in restrict_res_to_release_on_suspend
        and expect an unknown resource error
        """

        # Set restrict_res_to_release_on_suspend server attribute
        a = {ATTR_restrict_res_to_release_on_suspend: 'ncpus,abc'}
        try:
            self.server.manager(MGR_CMD_SET, SERVER, a)
        except PbsManagerError as e:
            self.assertTrue("Unknown resource" in e.msg[0])

    def test_delete_res_busy_on_res_to_release_list(self):
        """
        Create a resource, set it in restrict_res_to_release_on_suspend
        then delete the resource and check for resource busy error
        """

        # create a custom resource
        attr = {ATTR_RESC_TYPE: 'long'}
        self.server.manager(MGR_CMD_CREATE, RSC, attr, id='foo')
        self.server.manager(MGR_CMD_CREATE, RSC, attr, id='bar')

        # Set restrict_res_to_release_on_suspend server attribute
        a = {ATTR_restrict_res_to_release_on_suspend: 'ncpus,foo,bar'}
        self.server.manager(MGR_CMD_SET, SERVER, a)

        # delete the custom resources
        try:
            self.server.manager(MGR_CMD_DELETE, RSC, id='foo')
        except PbsManagerError as e:
            self.assertTrue("Resource busy on server" in e.msg[0])

        try:
            self.server.manager(MGR_CMD_DELETE, RSC, id='bar')
        except PbsManagerError as e:
            self.assertTrue("Resource busy on server" in e.msg[0])
