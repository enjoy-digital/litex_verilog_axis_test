#!/usr/bin/env python3

#
# This file is part of LiteX-Verilog-AXIS-Test
#
# Copyright (c) 2022 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

import argparse

from migen import *

from litex.build.generic_platform import *
from litex.build.sim import SimPlatform
from litex.build.sim.config import SimConfig
from litex.build.sim.verilator import verilator_build_args, verilator_build_argdict

from litex.soc.interconnect.csr import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.builder import *
from litex.soc.interconnect.axi import *

from verilog_axis.axis_common import *

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst.
    ("sys_clk", 0, Pins(1)),
    ("sys_rst", 0, Pins(1)),

    # Serial.
    ("serial", 0,
        Subsignal("source_valid", Pins(1)),
        Subsignal("source_ready", Pins(1)),
        Subsignal("source_data",  Pins(8)),

        Subsignal("sink_valid", Pins(1)),
        Subsignal("sink_ready", Pins(1)),
        Subsignal("sink_data",  Pins(8)),
    ),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(SimPlatform):
    name = "sim"
    def __init__(self):
        SimPlatform.__init__(self, "SIM", _io)

# AXIS Generator -----------------------------------------------------------------------------------

# FIXME: Minimal Generator, Improve.

class AXISGenerator(Module):
    def __init__(self, axis):
        self.comb += axis.valid.eq(1)
        self.sync += If(axis.valid & axis.ready, axis.data.eq(axis.data + 1))

# AXIS Checker -------------------------------------------------------------------------------------

# FIXME: Minimal Checker, Improve.

class AXISChecker(Module):
    def __init__(self, axis):
        self.errors = Signal(32)
        self.cycles = Signal(32)

        axis_data_last = Signal(len(axis.data), reset=(2**len(axis.data)-1))
        self.comb += axis.ready.eq(1)
        self.sync += [
            If(axis.valid & axis.ready,
                self.cycles.eq(self.cycles + 1),
                If(axis.data != (axis_data_last + 1),
                    self.errors.eq(self.errors + 1)
                ),
                axis_data_last.eq(axis.data)
            )
        ]

# AXISSimSoC ---------------------------------------------------------------------------------------

class AXISSimSoC(SoCCore):
    def __init__(self):
        # Parameters.
        sys_clk_freq = int(100e6)

        # Platform.
        platform     = Platform()
        self.comb += platform.trace.eq(1)

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = CRG(platform.request("sys_clk"))

        # SoCCore ----------------------------------------------------------------------------------
        SoCMini.__init__(self, platform, clk_freq=sys_clk_freq)

        # AXIS Tests --------------------------------------------------------------------------------
        def axis_syntax_test():
            # AXIS FIFO.
            # ----------
            from verilog_axis.axis_fifo import AXISFIFO
            s_axis = AXIStreamInterface(data_width=32)
            m_axis = AXIStreamInterface(data_width=32)
            self.submodules.axis_fifo = AXISFIFO(platform, s_axis, m_axis, depth=4096)

            # AXIS SRL FIFO.
            # --------------
            from verilog_axis.axis_srl_fifo import AXISSRLFIFO
            s_axis = AXIStreamInterface(data_width=32)
            m_axis = AXIStreamInterface(data_width=32)
            self.submodules.axis_srl_fifo = AXISSRLFIFO(platform, s_axis, m_axis, depth=16)

            # AXIS Async FIFO.
            # ----------------
            from verilog_axis.axis_async_fifo import AXISAsyncFIFO
            s_axis = AXIStreamInterface(data_width=32)
            m_axis = AXIStreamInterface(data_width=32)
            self.submodules.axis_async_fifo = AXISAsyncFIFO(platform, s_axis, m_axis, depth=4096)

            # AXIS Regiser.
            # -------------
            from verilog_axis.axis_register import AXISRegister
            s_axis = AXIStreamInterface(data_width=32)
            m_axis = AXIStreamInterface(data_width=32)
            self.submodules.axis_register = AXISRegister(platform, s_axis, m_axis)

            # AXIS SRL Regiser.
            # -----------------
            from verilog_axis.axis_srl_register import AXISSRLRegister
            s_axis = AXIStreamInterface(data_width=32)
            m_axis = AXIStreamInterface(data_width=32)
            self.submodules.axis_srl_register = AXISSRLRegister(platform, s_axis, m_axis)

            # AXIS Adapter.
            # -------------
            from verilog_axis.axis_adapter import AXISAdapter
            s_axis = AXIStreamInterface(data_width=32)
            m_axis = AXIStreamInterface(data_width=32)
            self.submodules.axis_adapter = AXISAdapter(platform, s_axis, m_axis)

            # AXIS Rate Limit.
            # ----------------
            from verilog_axis.axis_rate_limit import AXISRateLimit
            s_axis = AXIStreamInterface(data_width=32)
            m_axis = AXIStreamInterface(data_width=32)
            self.submodules.axis_rate_limit = AXISRateLimit(platform, s_axis, m_axis)

            # AXIS Tap.
            # ---------
            from verilog_axis.axis_tap import AXISTap
            s_axis = AXIStreamInterface(data_width=32)
            m_axis = AXIStreamInterface(data_width=32)
            self.submodules.axis_tap = AXISTap(platform, s_axis, m_axis)

            # AXIS Broadcast.
            # ---------------
            from verilog_axis.axis_broadcast import AXISBroadcast
            s_axis  = AXIStreamInterface(data_width=32)
            m_axis0 = AXIStreamInterface(data_width=32)
            m_axis1 = AXIStreamInterface(data_width=32)
            self.submodules.axis_broadcast = AXISBroadcast(platform, s_axis, [m_axis0, m_axis1])

            # AXIS Arb Mux.
            # -------------
            from verilog_axis.axis_arb_mux import AXISArbMux
            s_axis0 = AXIStreamInterface(data_width=32)
            s_axis1 = AXIStreamInterface(data_width=32)
            m_axis  = AXIStreamInterface(data_width=32)
            self.submodules.axis_arb_mux = AXISArbMux(platform, [m_axis0, m_axis1], m_axis)

            # AXIS Mux.
            # ---------
            from verilog_axis.axis_mux import AXISMux
            s_axis0 = AXIStreamInterface(data_width=32)
            s_axis1 = AXIStreamInterface(data_width=32)
            m_axis  = AXIStreamInterface(data_width=32)
            self.submodules.axis_mux = AXISMux(platform, [s_axis0, s_axis1], m_axis)

            # AXIS Demux.
            # -----------
            from verilog_axis.axis_demux import AXISDemux
            s_axis  = AXIStreamInterface(data_width=32)
            m_axis0 = AXIStreamInterface(data_width=32)
            m_axis1 = AXIStreamInterface(data_width=32)
            self.submodules.axis_mux = AXISDemux(platform, s_axis, [m_axis0, m_axis1])

            # AXIS Crosspoint.
            # ----------------
            from verilog_axis.axis_crosspoint import AXISCrosspoint
            s_axis0 = AXIStreamInterface(data_width=32)
            s_axis1 = AXIStreamInterface(data_width=32)
            m_axis0 = AXIStreamInterface(data_width=32)
            m_axis1 = AXIStreamInterface(data_width=32)
            # FIXME: Verilator compil issue.
            #self.submodules.axis_crosspoint = AXISCrosspoint(platform,
            #    s_axis=[s_axis0, s_axis1],
            #    m_axis=[m_axis0, m_axis1]
            #)

            # AXIS Switch.
            # ------------
            from verilog_axis.axis_switch import AXISSwitch
            s_axis0 = AXIStreamInterface(data_width=32)
            s_axis1 = AXIStreamInterface(data_width=32)
            m_axis0 = AXIStreamInterface(data_width=32)
            m_axis1 = AXIStreamInterface(data_width=32)
            self.submodules.axis_switch = AXISSwitch(platform,
                s_axis=[s_axis0, s_axis1],
                m_axis=[m_axis0, m_axis1]
            )

            # AXIS RAM Switch.
            # ----------------
            # FIXME: Verilator compil issue.
            #from verilog_axis.axis_ram_switch import AXISRAMSwitch
            #s_axis0 = AXIStreamInterface(data_width=32)
            #s_axis1 = AXIStreamInterface(data_width=32)
            #m_axis0 = AXIStreamInterface(data_width=32)
            #m_axis1 = AXIStreamInterface(data_width=32)
            #self.submodules.axis_ram_switch = AXISRAMSwitch(platform,
            #    s_axis=[s_axis0, s_axis1],
            #    m_axis=[m_axis0, m_axis1]
            #)

        def axis_integration_test():
            # AXIS FIFO.
            # ----------
            from verilog_axis.axis_fifo import AXISFIFO
            s_axis = AXIStreamInterface(data_width=32)
            m_axis = AXIStreamInterface(data_width=32)
            self.submodules.axis_fifo = AXISFIFO(platform, s_axis, m_axis, depth=4096)

            axis_fifo_generator = AXISGenerator(s_axis)
            axis_fifo_checker   = AXISChecker(m_axis)
            self.submodules += axis_fifo_generator, axis_fifo_checker

            # AXIS SRL FIFO.
            # --------------
            from verilog_axis.axis_srl_fifo import AXISSRLFIFO
            s_axis = AXIStreamInterface(data_width=32)
            m_axis = AXIStreamInterface(data_width=32)
            self.submodules.axis_srl_fifo = AXISFIFO(platform, s_axis, m_axis, depth=4096)

            axis_srl_fifo_generator = AXISGenerator(s_axis)
            axis_srl_fifo_checker   = AXISChecker(m_axis)
            self.submodules += axis_srl_fifo_generator, axis_srl_fifo_checker

            # AXIS Async FIFO.
            # ----------------
            from verilog_axis.axis_async_fifo import AXISAsyncFIFO
            s_axis = AXIStreamInterface(data_width=32)
            m_axis = AXIStreamInterface(data_width=32)
            self.submodules.axis_async_fifo = AXISAsyncFIFO(platform, s_axis, m_axis, depth=4096)

            axis_async_fifo_generator = AXISGenerator(s_axis)
            axis_async_fifo_checker   = AXISChecker(m_axis)
            self.submodules += axis_async_fifo_generator, axis_async_fifo_checker

            # AXIS Register.
            # --------------
            from verilog_axis.axis_register import AXISRegister
            s_axis = AXIStreamInterface(data_width=32)
            m_axis = AXIStreamInterface(data_width=32)
            self.submodules.axis_register = AXISRegister(platform, s_axis, m_axis)

            axis_register_generator = AXISGenerator(s_axis)
            axis_register_checker  = AXISChecker(m_axis)
            self.submodules += axis_register_generator, axis_register_checker

            # AXIS SRL Register.
            # ------------------
            from verilog_axis.axis_srl_register import AXISSRLRegister
            s_axis = AXIStreamInterface(data_width=32)
            m_axis = AXIStreamInterface(data_width=32)
            self.submodules.axis_srl_register = AXISSRLRegister(platform, s_axis, m_axis)

            axis_srl_register_generator = AXISGenerator(s_axis)
            axis_srl_register_checker   = AXISChecker(m_axis)
            self.submodules += axis_srl_register_generator, axis_srl_register_checker

            # AXIS Adapter.
            # -------------
            from verilog_axis.axis_adapter import AXISAdapter
            s_axis = AXIStreamInterface(data_width=32)
            m_axis = AXIStreamInterface(data_width=32)
            self.submodules.axis_adapter = AXISAdapter(platform, s_axis, m_axis)

            axis_adapter_generator = AXISGenerator(s_axis)
            axis_adapter_checker   = AXISChecker(m_axis)
            self.submodules += axis_adapter_generator, axis_adapter_checker

            # AXIS Rate Limit.
            # ----------------
            from verilog_axis.axis_rate_limit import AXISRateLimit
            s_axis = AXIStreamInterface(data_width=32)
            m_axis = AXIStreamInterface(data_width=32)
            self.submodules.axis_rate_limit = AXISRateLimit(platform, s_axis, m_axis)

            axis_rate_limit_generator = AXISGenerator(s_axis)
            axis_rate_limit_checker   = AXISChecker(m_axis)
            self.submodules += axis_rate_limit_generator, axis_rate_limit_checker

            # AXIS Tap.
            # ---------
            from verilog_axis.axis_tap import AXISTap
            s_axis = AXIStreamInterface(data_width=32)
            m_axis = AXIStreamInterface(data_width=32)
            self.submodules.axis_tap = AXISTap(platform, s_axis, m_axis)

            axis_tap_generator = AXISGenerator(s_axis)
            axis_tap_checker   = AXISChecker(m_axis)
            self.submodules += axis_tap_generator, axis_tap_checker

            # AXIS Broadcast.
            # ---------------
            from verilog_axis.axis_broadcast import AXISBroadcast
            s_axis = AXIStreamInterface(data_width=32)
            m_axis0 = AXIStreamInterface(data_width=32)
            m_axis1 = AXIStreamInterface(data_width=32)
            self.submodules.axis_broadcast = AXISBroadcast(platform, s_axis, [m_axis0, m_axis1])

            axis_broadcast_generator = AXISGenerator(s_axis)
            axis_broadcast_checker0  = AXISChecker(m_axis0)
            axis_broadcast_checker1  = AXISChecker(m_axis1)
            self.submodules += axis_broadcast_generator, axis_broadcast_checker0, axis_broadcast_checker1

            # AXIS Arb Mux.
            # -------------
            from verilog_axis.axis_arb_mux import AXISArbMux
            s_axis0 = AXIStreamInterface(data_width=32)
            s_axis1 = AXIStreamInterface(data_width=32)
            m_axis  = AXIStreamInterface(data_width=32)
            self.submodules.axis_arb_mux = AXISArbMux(platform, [m_axis0, m_axis1], m_axis)

            axis_arb_mux_generator = AXISGenerator(s_axis0)
            axis_arb_mux_checker   = AXISChecker(m_axis)
            self.submodules += axis_arb_mux_generator, axis_arb_mux_checker

            # AXIS Mux.
            # ---------
            from verilog_axis.axis_mux import AXISMux
            s_axis0 = AXIStreamInterface(data_width=32)
            s_axis1 = AXIStreamInterface(data_width=32)
            m_axis  = AXIStreamInterface(data_width=32)
            self.submodules.axis_mux = AXISMux(platform, [s_axis0, s_axis1], m_axis)

            axis_mux_generator = AXISGenerator(s_axis0)
            axis_mux_checker   = AXISChecker(m_axis)
            self.submodules += axis_mux_generator, axis_mux_checker

            # AXIS Demux.
            # -----------
            from verilog_axis.axis_demux import AXISDemux
            s_axis  = AXIStreamInterface(data_width=32)
            m_axis0 = AXIStreamInterface(data_width=32)
            m_axis1 = AXIStreamInterface(data_width=32)
            self.submodules.axis_demux = AXISDemux(platform, s_axis, [m_axis0, m_axis1])

            axis_demux_generator = AXISGenerator(s_axis)
            axis_demux_checker   = AXISChecker(m_axis0)
            self.submodules += axis_demux_generator, axis_demux_checker

            # AXIS Switch.
            # ------------
            from verilog_axis.axis_switch import AXISSwitch
            s_axis0 = AXIStreamInterface(data_width=32)
            s_axis1 = AXIStreamInterface(data_width=32)
            m_axis0 = AXIStreamInterface(data_width=32)
            m_axis1 = AXIStreamInterface(data_width=32)
            self.submodules.axis_demux = AXISSwitch(platform,
                s_axis=[s_axis0, s_axis1],
                m_axis=[m_axis0, m_axis1]
            )
            axis_switch_generator = AXISGenerator(s_axis0)
            axis_switch_checker   = AXISChecker(m_axis0)
            self.submodules += axis_switch_generator, axis_switch_checker

            # Finish -------------------------------------------------------------------------------
            cycles = Signal(32)
            self.sync += cycles.eq(cycles + 1)
            self.sync += If(cycles == 10000,
                Display("-"*80),
                Display("Cycles                   : %d", cycles),
                Display("AXIS FIFO         Errors : %d / Cycles: %d",
                    axis_fifo_checker.errors,
                    axis_fifo_checker.cycles),
                Display("AXIS SRL FIFO     Errors : %d / Cycles: %d",
                    axis_srl_fifo_checker.errors,
                    axis_srl_fifo_checker.cycles),
                Display("AXIS Async FIFO   Errors : %d / Cycles: %d",
                    axis_async_fifo_checker.errors,
                    axis_async_fifo_checker.cycles),
                Display("AXIS Register     Errors : %d / Cycles: %d",
                    axis_register_checker.errors,
                    axis_register_checker.cycles),
                Display("AXIS SRL Register Errors : %d / Cycles: %d",
                    axis_srl_register_checker.errors,
                    axis_srl_register_checker.cycles),
                Display("AXIS Adapter      Errors : %d / Cycles: %d",
                    axis_adapter_checker.errors,
                    axis_adapter_checker.cycles),
                Display("AXIS Rate Limit   Errors : %d / Cycles: %d",
                    axis_rate_limit_checker.errors,
                    axis_rate_limit_checker.cycles),
                Display("AXIS Tap          Errors : %d / Cycles: %d",
                    axis_tap_checker.errors,
                    axis_tap_checker.cycles),
                Display("AXIS Broadcast 0  Errors : %d / Cycles: %d",
                    axis_broadcast_checker0.errors,
                    axis_broadcast_checker0.cycles),
                Display("AXIS Broadcast 1  Errors : %d / Cycles: %d",
                    axis_broadcast_checker1.errors,
                    axis_broadcast_checker1.cycles),
               Display("AXIS Arb Mux       Errors : %d / Cycles: %d",
                    axis_arb_mux_checker.errors,
                    axis_arb_mux_checker.cycles),
               Display("AXIS Mux           Errors : %d / Cycles: %d",
                    axis_mux_checker.errors,
                    axis_mux_checker.cycles),
               Display("AXIS Demux         Errors : %d / Cycles: %d",
                    axis_demux_checker.errors,
                    axis_demux_checker.cycles),
               Display("AXIS Switch        Errors : %d / Cycles: %d",
                    axis_switch_checker.errors,
                    axis_switch_checker.cycles),
                Finish(),
            )

        axis_syntax_test()
        axis_integration_test()

# Build --------------------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="LiteX Verilog AXIS test simulation SoC ")
    verilator_build_args(parser)
    args = parser.parse_args()
    verilator_build_kwargs = verilator_build_argdict(args)
    sim_config = SimConfig(default_clk="sys_clk")

    soc = AXISSimSoC()
    builder = Builder(soc)
    builder.build(sim_config=sim_config, **verilator_build_kwargs)

if __name__ == "__main__":
    main()
