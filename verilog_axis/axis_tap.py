#
# This file is part of LiteX-Verilog-AXIS-Test
#
# Copyright (c) 2022 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

# LiteX wrapper around Alex Forencich Verilog-AXIS's axi_tap.v.

import os
import math

from migen import *

from litex.soc.interconnect import stream
from litex.soc.interconnect.axi import *

from verilog_axis.axis_common import *

# AXIS Tap -----------------------------------------------------------------------------------------

class AXISTap(Module):
    def __init__(self, platform, tap_axis, m_axis):
        self.logger = logging.getLogger("AXISTap")

        # Get/Check Parameters.
        # ---------------------

        # Clock Domain.
        clock_domain = tap_axis.clock_domain
        if tap_axis.clock_domain != m_axis.clock_domain:
            self.logger.error("{} on {} (Tap: {} / Master: {}), should be {}.".format(
                colorer("Different Clock Domain", color="red"),
                colorer("AXI-Stream interfaces."),
                colorer(tap_axis.clock_domain),
                colorer(m_axis.clock_domain),
                colorer("the same")))
            raise AXIError()
        else:
            self.logger.info(f"Clock Domain: {colorer(clock_domain)}")

        # Data width.
        data_width = len(tap_axis.data)
        self.logger.info(f"Data Width: {colorer(data_width)}")

        # ID width.
        id_width = tap_axis.id_width
        self.logger.info(f"ID Width: {colorer(id_width)}")

        # Dest width.
        dest_width = tap_axis.dest_width
        self.logger.info(f"Dest Width: {colorer(dest_width)}")

        # User width.
        user_width = tap_axis.user_width
        self.logger.info(f"User Width: {colorer(user_width)}")

        # Module instance.
        # ----------------

        self.specials += Instance("axis_tap",
            # Parameters.
            # -----------
            p_DATA_WIDTH           = data_width,
            p_ID_ENABLE            = id_width > 0,
            p_ID_WIDTH             = max(1, id_width),
            p_DEST_ENABLE          = dest_width > 0,
            p_DEST_WIDTH           = max(1, dest_width),
            p_USER_ENABLE          = user_width > 0,
            p_USER_WIDTH           = max(1, user_width),
            p_USER_BAD_FRAME_VALUE = 1, # FIXME: Expose.
            p_USER_BAD_FRAME_MASK  = 1, # FIXME: Expose.

            # Clk / Rst.
            # ----------
            i_clk = ClockSignal(clock_domain),
            i_rst = ResetSignal(clock_domain),

            # AXI Input.
            # ----------
            i_tap_axis_tdata  = tap_axis.data,
            i_tap_axis_tkeep  = tap_axis.keep,
            i_tap_axis_tvalid = tap_axis.valid,
            o_tap_axis_tready = tap_axis.ready,
            i_tap_axis_tlast  = tap_axis.last,
            i_tap_axis_tid    = tap_axis.id,
            i_tap_axis_tdest  = tap_axis.dest,
            i_tap_axis_tuser  = tap_axis.user,

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
        platform.add_source(os.path.join(rtl_dir, "axis_tap.v"))
