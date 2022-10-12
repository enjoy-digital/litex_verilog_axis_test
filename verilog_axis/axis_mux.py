#
# This file is part of LiteX-Verilog-AXIS-Test
#
# Copyright (c) 2022 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

# LiteX wrapper around Alex Forencich Verilog-AXIS's axi_mux.v.

import os
import math

from migen import *

from litex.soc.interconnect import stream
from litex.soc.interconnect.axi import *

from verilog_axis.axis_common import *

# AXIS Mux -----------------------------------------------------------------------------------------

class AXISMux(Module):
    def __init__(self, platform, s_axis, m_axis):
        self.logger = logging.getLogger("AXISMux")

        # FIXME: Add Logs/Checks.
        # FIXME: Add Dynamic support?

        # Get/Check Parameters.
        # ---------------------
        if not isinstance(s_axis, list):
            s_axis = [s_axis]
        assert isinstance(m_axis, AXIStreamInterface)

        # Clock Domain.
        clock_domain = s_axis[0].clock_domain
        self.logger.info(f"Clock Domain: {colorer(clock_domain)}")

        # Data width.
        data_width = len(s_axis[0].data)
        self.logger.info(f"Data Width: {colorer(data_width)}")

        # ID width.
        id_width = s_axis[0].id_width
        self.logger.info(f"ID Width: {colorer(id_width)}")

        # Dest width.
        dest_width = s_axis[0].data_width
        self.logger.info(f"Dest Width: {colorer(dest_width)}")

        # User width.
        user_width = s_axis[0].user_width
        self.logger.info(f"User Width: {colorer(user_width)}")

        # Controls.
        # ---------
        self.enable = Signal(reset=1)
        self.select = Signal(max=len(s_axis))

        # Module instance.
        # ----------------

        self.specials += Instance("axis_mux",
            # Parameters.
            # -----------
            p_S_COUNT     = len(s_axis),
            p_DATA_WIDTH  = data_width,
            p_ID_ENABLE   = id_width > 0,
            p_ID_WIDTH    = max(1, id_width),
            p_DEST_ENABLE = dest_width > 0,
            p_DEST_WIDTH  = max(1, dest_width),
            p_USER_ENABLE = user_width > 0,
            p_USER_WIDTH  = max(1, user_width),

            # Clk / Rst.
            # ----------
            i_clk = ClockSignal(clock_domain),
            i_rst = ResetSignal(clock_domain),

            # Controls.
            # ---------
            i_enable = self.enable,
            i_select = self.select,

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

            # AXI Output.
            # -----------
            o_m_axis_tdata  = m_axis.data,
            o_m_axis_tkeep  = m_axis.keep,
            o_m_axis_tvalid = m_axis.valid,
            i_m_axis_tready = m_axis.ready,
            o_m_axis_tlast  = m_axis.last,
            o_m_axis_tid    = m_axis.id,
            o_m_axis_tdest  = m_axis.dest,
            o_m_axis_tuser  = m_axis.user,
        )

        # Add Sources.
        # ------------
        self.add_sources(platform)

    @staticmethod
    def add_sources(platform):
        rtl_dir = os.path.join(os.path.dirname(__file__), "verilog", "rtl")
        platform.add_source(os.path.join(rtl_dir, "axis_mux.v"))
