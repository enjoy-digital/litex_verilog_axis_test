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

# AXIS FIFO ----------------------------------------------------------------------------------------

class AXISFIFO(Module):
    def __init__(self, platform, s_axis, m_axis, depth=4096):
        self.logger = logging.getLogger("AXISFIFO")

        # Get/Check Parameters.
        # ---------------------

        # Data width.
        data_width = len(s_axis.data)
        self.logger.info(f"Data Width: {colorer(data_width)}")

        # ID width.
        id_width = s_axis.id_width
        self.logger.info(f"ID Width: {colorer(id_width)}")

        # Dest width.
        dest_width = s_axis.dest_width
        self.logger.info(f"Dest Width: {colorer(dest_width)}")

        # User width.
        user_width = s_axis.user_width
        self.logger.info(f"User Width: {colorer(user_width)}")

        # Module instance.
        # ----------------

        self.specials += Instance("axis_fifo",
            # Parameters.
            # -----------
            p_DEPTH                = depth,
            p_DATA_WIDTH           = data_width,
            p_LAST_ENABLE          = 1, # FIXME: Expose.
            p_ID_ENABLE            = id_width > 0,
            p_ID_WIDTH             = max(1, id_width),
            p_DEST_ENABLE          = dest_width > 0,
            p_DEST_WIDTH           = max(1, dest_width),
            p_USER_ENABLE          = user_width > 0,
            p_USER_WIDTH           = max(1, user_width),
            p_PIPELINE_OUTPUT      = 2, # FIXME: Epose.
            p_FRAME_FIFO           = 0, # FIXME: Epose.
            p_USER_BAD_FRAME_VALUE = 1, # FIXME: Epose.
            p_USER_BAD_FRAME_MASK  = 1, # FIXME: Epose.
            p_DROP_OVERSIZE_FRAME  = 0, # FIXME: Epose.
            p_DROP_BAD_FRAME       = 0, # FIXME: Epose.
            p_DROP_WHEN_FULL       = 0, # FIXME: Epose.

            # Clk / Rst.
            # ----------
            i_clk = ClockSignal("sys"), # FIXME. clock_domain.
            i_rst = ResetSignal("sys"), # FIXME: clock_domain.

            # Status.
            # -------
            o_status_overflow   = Open(), # FIXME: Expose.
            o_status_bad_frame  = Open(), # FIXME: Expose.
            o_status_good_frame = Open(), # FIXME: Expose.

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
        platform.add_source(os.path.join(rtl_dir, "axis_fifo.v"))