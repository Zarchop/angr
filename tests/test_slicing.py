#!/usr/bin/env python

import logging
l = logging.getLogger("angr.tests.slicing")

import time
import nose
import angr

# Load the tests
import os
test_location = str(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../binaries/tests"))

def test_control_flow_slicing():
    slicing_test = angr.Project(test_location + "/x86_64/cfg_1",
                                use_sim_procedures=True,
                                default_analysis_mode='symbolic')
    l.info("Control Flow Slicing")
    start = time.time()
    cfg = slicing_test.analyses.CFG(context_sensitivity_level=2)
    end = time.time()
    duration = end - start
    l.info("CFG generation is done in %f seconds.", duration)

    target = cfg.get_any_node(0x400594)
    bs = slicing_test.analyses.BackwardSlice(cfg, None, None, target, -1, control_flow_slice=True)
    anno_cfg = bs.annotated_cfg()
    nose.tools.assert_equal(anno_cfg.get_whitelisted_statements(0x40057c), None)
    nose.tools.assert_equal(anno_cfg.get_whitelisted_statements(0x400594), None)
    nose.tools.assert_equal(anno_cfg.get_whitelisted_statements(0x4005a4), None)

def broken_backward_slice():
    #TODO: Fix this test case. There seems to be a bug with CDG itself.

    slicing_test = angr.Project(test_location + "/x86_64/cfg_1",
                                use_sim_procedures=True,
                                default_analysis_mode='symbolic')
    l.info("Control Flow Slicing")
    start = time.time()
    cfg = slicing_test.analyses.CFG(context_sensitivity_level=2, keep_input_state=True)
    end = time.time()
    duration = end - start
    l.info("CFG generation is done in %f seconds.", duration)

    cdg = slicing_test.analyses.CDG()
    ddg = slicing_test.analyses.DDG(cfg=cfg)

    target = cfg.get_any_node(0x4005d3)
    bs = slicing_test.analyses.BackwardSlice(cfg, cdg, ddg, target, -1, control_flow_slice=False)
    anno_cfg = bs.annotated_cfg()
    nose.tools.assert_not_equal(anno_cfg.get_whitelisted_statements(0x40057c), None)
    nose.tools.assert_not_equal(anno_cfg.get_whitelisted_statements(0x400594), None)
    nose.tools.assert_not_equal(anno_cfg.get_whitelisted_statements(0x4005a4), None)

def test_last_branching_statement():
    slicing_test = angr.Project(test_location + '/armel/fauxware',
                                use_sim_procedures=True)
    l.info('Testing _search_for_last_branching_statement.')

    # The IRSB:

    # ------ IMark(0x86dc, 4, 0) ------
    # t1 = GET:I32(r0)
    # PUT(pc) = 0x000086e0
    # ------ IMark(0x86e0, 4, 0) ------
    # t14 = GET:I32(r11)
    # t13 = Sub32(t14,0x00000024)
    # STle(t13) = t1
    # PUT(pc) = 0x000086e4
    # ------ IMark(0x86e4, 4, 0) ------
    # t15 = t13
    # t8 = LDle:I32(t15)
    # PUT(r3) = t8
    # ------ IMark(0x86e8, 4, 0) ------
    # PUT(cc_op) = 0x00000002
    # PUT(cc_dep1) = t8
    # PUT(cc_dep2) = 0x00000000
    # PUT(cc_ndep) = 0x00000000
    # PUT(pc) = 0x000086ec
    # ------ IMark(0x86ec, 4, 0) ------
    # t26 = CmpEQ32(t8,0x00000000)
    # t25 = 1Uto32(t26)
    # t27 = 32to1(t25)
    # if (t27) { PUT(68) = 0x86f8; Ijk_Boring }

    target_path = slicing_test.factory.path(slicing_test.factory.blank_state(addr=0x86dc))
    target_path.step()
    target = target_path.next_run
    l.debug("IRSB:")
    for line in target.irsb._pp_str().split('\n'):
        l.debug(line)

    bs = slicing_test.analyses.BackwardSlice(None, None, None, target, -1, no_construct=True)

    stmt_idx, tmp = bs._last_branching_statement(target.statements)

    nose.tools.assert_equal(stmt_idx, 22)
    nose.tools.assert_equal(tmp, 27)

if __name__ == "__main__":
    logging.getLogger("angr.cfg").setLevel(logging.DEBUG)
    test_last_branching_statement()
    test_control_flow_slicing()
    # test_backward_slice()
