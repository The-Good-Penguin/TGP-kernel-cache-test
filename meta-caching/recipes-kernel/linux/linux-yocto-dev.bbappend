#
# Use latest yocto dev git
#

FILESEXTRAPATHS:prepend := "${THISDIR}/linux-yocto:"

SRC_URI += " \
    file://qemu-usage-fragment.cfg \
    "


KBRANCH = "v6.16/standard/base"
LINUX_VERSION = "6.16"

