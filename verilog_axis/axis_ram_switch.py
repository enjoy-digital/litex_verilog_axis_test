#
# This file is part of LiteX-Verilog-AXIS-Test
#
# Copyright (c) 2022 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

# LiteX wrapper around Alex Forencich Verilog-AXIS's axi_ram_switch.v.

import os
import math

from migen import *

from litex.soc.interconnect import stream
from litex.soc.interconnect.axi import *

from verilog_axis.axis_common import *

# AXIS RAM_Switch ----------------------------------------------------------------------------------

class AXISRAMSwitch(Module):
    def __init__(self, platform, s_axis, m_axis, fifo_depth=4096, cmd_fifo_depth=32,
        speedup               = 0,
        user_bad_frame_value  = 1,
        user_bad_frame_mask   = 1,
        drop_bad_frame        = 0,
        drop_when_full        = 0,
        m_base                = 0,
        m_top                 = 0,
        update_tid            = 0,
        arb_type_round_robin  = 1,
        arb_lsb_high_priority = 1,
        ram_pipeline          = 2,
    ):
        self.logger = logging.getLogger("AXISRAMSwitch")

        # FIXME: Add Logs/Checks.
        # FIXME: Add Dynamic support?

        # Get/Check Parameters.
        # ---------------------
        if not isinstance(s_axis, list):
            s_axis = [s_axis]
        if not isinstance(m_axis, list):
            m_axis = [m_axis]

        # Clock Domain.
        clock_domain = s_axis[0].clock_domain
        self.logger.info(f"Clock Domain: {colorer(clock_domain)}")

        # Data widths.
        s_data_width = len(s_axis[0].data)
        m_data_width = len(m_axis[0].data)
        self.logger.info(f"Slave  Data Width: {colorer(s_data_width)}")
        self.logger.info(f"Master Data Width: {colorer(m_data_width)}")

        # ID width.
        id_width = s_axis[0].id_width
        self.logger.info(f"ID Width: {colorer(id_width)}")

        # Dest width.
        dest_width = s_axis[0].data_width
        self.logger.info(f"Dest Width: {colorer(dest_width)}")

        # User width.
        user_width = s_axis[0].user_width
        self.logger.info(f"User Width: {colorer(user_width)}")

        # Status.
        # -------
        self.s_overflow   = Signal(len(s_axis))
        self.s_bad_frame  = Signal(len(s_axis))
        self.s_good_frame = Signal(len(s_axis))

        # Module instance.
        # ----------------

        self.specials += Instance("axis_ram_switch",
            # Parameters.
            # -----------
            p_FIFO_DEPTH            = fifo_depth,
            p_CMD_FIFO_DEPTH        = cmd_fifo_depth,
            p_SPEEDUP               = 0,
            p_S_COUNT               = len(s_axis),
            p_M_COUNT               = len(m_axis),
            p_S_DATA_WIDTH          = s_data_width,
            p_M_DATA_WIDTH          = m_data_width,
            p_ID_ENABLE             = id_width > 0,
            p_S_ID_WIDTH            = max(1, id_width),
            p_M_DEST_WIDTH          = max(1, dest_width),
            p_USER_ENABLE           = user_width > 0,
            p_USER_WIDTH            = max(1, user_width),
            p_USER_BAD_FRAME_VALUE  = user_bad_frame_value,
            p_USER_BAD_FRAME_MASK   = user_bad_frame_mask,
            p_DROP_BAD_FRAME        = drop_bad_frame,
            p_DROP_WHEN_FULL        = drop_when_full,
            p_M_BASE                = m_base,
            p_M_TOP                 = m_top,
            p_UPDATE_TID            = update_tid,
            p_ARB_TYPE_ROUND_ROBIN  = arb_type_round_robin,
            p_ARB_LSB_HIGH_PRIORITY = arb_lsb_high_priority,

            # Clk / Rst.
            # ----------
            i_clk = ClockSignal(clock_domain),
            i_rst = ResetSignal(clock_domain),

            # Status.
            # -------
            o_status_overflow   = self.s_overflow,
            o_status_bad_frame  = self.s_bad_frame,
            o_status_good_frame = self.s_good_frame,

            # AXI Inputs.
            # -----------
            i_s_axis_tdata  = Cat(*[axis.data  for axis in s_axis]),
            i_s_axis_tkeep  = Cat(*[axis.keep  for axis in s_axis]),
            i_s_axis_tvalid = Cat(*[axis.valid for axis in s_axis]),
            o_s_axis_tready = Cat(*[axis.ready for axis in s_axis]),
            i_s_axis_tlast  = Cat(*[axis.last  for axis in s_axis]),
            i_s_axis_tid    = Cat(*[axis.id    for axis in s_axis]),
            i_s_axis_tdest  = Cat(*[axis.dest  for axis in s_axis]),
            i_s_axis_tuser  = Cat(*[axis.user  for axis in s_axis]),

            # AXI Outputs.
            # ------------
            o_m_axis_tdata  = Cat(*[axis.data  for axis in m_axis]),
            o_m_axis_tkeep  = Cat(*[axis.keep  for axis in m_axis]),
            o_m_axis_tvalid = Cat(*[axis.valid for axis in m_axis]),
            i_m_axis_tready = Cat(*[axis.ready for axis in m_axis]),
            o_m_axis_tlast  = Cat(*[axis.last  for axis in m_axis]),
            o_m_axis_tid    = Cat(*[axis.id    for axis in m_axis]),
            o_m_axis_tdest  = Cat(*[axis.dest  for axis in m_axis]),
            o_m_axis_tuser  = Cat(*[axis.user  for axis in m_axis]),
        )

        # Add Sources.
        # ------------
        self.add_sources(platform)

    @staticmethod
    def add_sources(platform):
        rtl_dir = os.path.join(os.path.dirname(__file__), "verilog", "rtl")
        platform.add_source(os.path.join(rtl_dir, "arbiter.v"))
        platform.add_source(os.path.join(rtl_dir, "axis_adapter.v"))
        platform.add_source(os.path.join(rtl_dir, "axis_ram_switch.v"))
