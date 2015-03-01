from mibuild.generic_platform import *
from mibuild.platforms import kc705

_sata_io = [
	("sata", 0,
		Subsignal("refclk_p", Pins("C8")),
		Subsignal("refclk_n", Pins("C7")),
		Subsignal("txp", Pins("D2")),
		Subsignal("txn", Pins("D1")),
		Subsignal("rxp", Pins("E4")),
		Subsignal("rxn", Pins("E3")),
	)
]

class SpecializedPlatform:
	def __init__(self, platform):
		self._platform = platform

	def __getattr__(self, name):
		return getattr(self._platform, name)

class Platform(SpecializedPlatform):
	def __init__(self, *args, **kwargs):
		SpecializedPlatform.__init__(self, kc705.Platform(*args, **kwargs))
		self.add_extension(_sata_io)

	def do_finalize(self, fragment):
			try:
				self.add_period_constraint(self.lookup_request("clk156").p, 6.4)
			except ConstraintError:
				pass
			try:
				self.add_period_constraint(self.lookup_request("clk200").p, 5.0)
			except ConstraintError:
				pass
			try:
				self.add_period_constraint(self.lookup_request("sata_host").refclk_p, 6.66)
			except ConstraintError:
				pass
			self.add_platform_command("""
create_clock -name sys_clk -period 6 [get_nets sys_clk]
create_clock -name sata_rx_clk -period 3.33 [get_nets sata_rx_clk]
create_clock -name sata_tx_clk -period 3.33 [get_nets sata_tx_clk]

set_false_path -from [get_clocks sys_clk] -to [get_clocks sata_rx_clk]
set_false_path -from [get_clocks sys_clk] -to [get_clocks sata_tx_clk]
set_false_path -from [get_clocks sata_rx_clk] -to [get_clocks sys_clk]
set_false_path -from [get_clocks sata_tx_clk] -to [get_clocks sys_clk]

set_property CFGBVS VCCO [current_design]
set_property CONFIG_VOLTAGE 2.5 [current_design]
""")
