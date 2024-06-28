########################################################################
# The Wiener PL506 power supply is used to provide 24V to a pacman.
# This code turns off the PL506 and its active channels
########################################################################

# os is used to issue system commands (in this case SNMP commands) via
# python code, as needed to initialize the Wiener PL506
import os

# turn off chosen channel(s)
cmd = "snmpset -v 2c -m+WIENER-CRATE-MIB -c guru 192.168.1.2 outputSwitch.u0 i 0"
os.system(cmd)

# turn off the Wiener PL506 power supply
cmd = "snmpset -v 2c -m+WIENER-CRATE-MIB -c private 192.168.1.2 sysMainSwitch.0 i 0"
os.system(cmd)
