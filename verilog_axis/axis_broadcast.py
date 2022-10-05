#
# This file is part of LiteX-Verilog-AXIS-Test
#
# Copyright (c) 2022 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

# LiteX wrapper around Alex Forencich Verilog-AXIS's axi_fifo.v.

import os
import math

from migen import *

from litex.soc.interconnect import stream
from litex.soc.interconnect.axi import *

from verilog_axis.axis_common import *

# AXIS Broadcast -----------------------------------------------------------------------------------

class AXISBroadcast(Module):
    def __init__(self, platform, s_axis, m_axis):
        self.logger = logging.getLogger("AXIBroadcast")

        # FIXME: Add Logs/Checks.
        # FIXME: Add Dynamic support?

        # Get/Check Parameters.
        # ---------------------

        assert isinstance(s_axis, AXIStreamInterface)
        if not isinstance(m_axis, list):
            m_axis = [m_axis]

        # Clock Domain.
        clock_domain = s_axis.clock_domain
        self.logger.info(f"Clock Domain: {colorer(clock_domain)}")

        # Data width.
        data_width = len(s_axis.data)
        self.logger.info(f"Data Width: {colorer(data_width)}")

        # ID width.
        id_width = len(s_axis.id)
        self.logger.info(f"ID Width: {colorer(id_width)}")

        # Dest width.
        dest_width = len(s_axis.id)
        self.logger.info(f"Dest Width: {colorer(dest_width)}")

        # User width.
        user_width = len(s_axis.user)
        self.logger.info(f"User Width: {colorer(user_width)}")

        # Module instance.
        # ----------------

        self.specials += Instance("axis_broadcast",
            # Parameters.
            # -----------
            p_M_COUNT              = len(m_axis),
            p_DATA_WIDTH           = data_width,
            p_LAST_ENABLE          = 1, # FIXME: Expose.
            p_ID_ENABLE            = 0, # FIXME: Expose.
            p_ID_WIDTH             = id_width,
            p_DEST_ENABLE          = 0, # FIXME: Expose.
            p_DEST_WIDTH           = dest_width,
            p_USER_ENABLE          = 0, # FIXME: Expose.
            p_USER_WIDTH           = user_width,

            # Clk / Rst.
            # ----------
            i_clk = ClockSignal(clock_domain),
            i_rst = ResetSignal(clock_domain),

            # AXI Input.
            # ----------
            i_s_axis_tdata  = s_axis.data,
            i_s_axis_tkeep  = s_axis.keep,
            i_s_axis_tvalid = s_axis.valid,
            o_s_axis_tready = s_axis.ready,
            i_s_axis_tlast  = s_axis.last,
            i_s_axis_tid    = s_axis.id,
            i_s_axis_tdest  = s_axis.dest,
            i_s_axis_tuser  = s_axis.user,

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
        platform.add_source(os.path.join(rtl_dir, "axis_broadcast.v"))
