[> Intro
--------
This repository is an experiment to wrap Alex Forenchich's Verilog-AXI-Stream core with LiteX to easily compose AXI systems with it.

[> AXI-Stream Status
---------------------

| Module                        | Status                                                           |
|-------------------------------|------------------------------------------------------------------|
| axis_adapter                  | Done, passing simple tests                                       |
| axis_arb_mux                  | Done, passing simple tests                                       |
| axis_async_fifo               | Done, passing simple tests                                       |
| axis_async_fifo_adapter       | Useless, will be composed with LiteX and axis_fifo/adapter       |
| axis_broadcast                | Done, passing simple tests                                       |
| axis_cobs_decode              | TODO                                                             |
| axis_cobs_encode              | TODO                                                             |
| axis_crosspoint               | Done, Verilator compil issue                                     |
| axis_demux                    | Done, passing simple tests                                       |
| axis_fifo                     | Done, passing simple tests                                       |
| axis_fifo_adapter             | TODO                                                             |
| axis_frame_join               | TODO                                                             |
| axis_frame_length_adjust      | TODO                                                             |
| axis_frame_length_adjust_fifo | TODO                                                             |
| axis_mux                      | Done, passing simple tests                                       |
| axis_pipeline_fifo            | Useless, will be composed with LiteX and axis_fifo               |
| axis_pipeline_register        | Useless, will be composed with LiteX and axis_register           |
| axis_ram_switch               | Done, Verilator compil issue                                     |
| axis_rate_limit               | Done, passing simple tests                                       |
| axis_register                 | Done, passing simple tests                                       |
| axis_srl_fifo                 | Done, passing simple tests                                       |
| axis_srl_register             | Done, passing simple tests                                       |
| axis_stat_counter             | TODO                                                             |
| axis_switch                   | Done, passing simple tests                                       |
| axis_tap                      | Done, need testing                                               |

[> AXI-Stream <-> LocalLink Status
----------------------------------

| Module                        | Status                     |
|-------------------------------|----------------------------|
| axis_ll_bridge                | TODO                       |
| ll_axis_bridge                | TODO                       |
