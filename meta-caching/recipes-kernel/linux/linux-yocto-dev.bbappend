#
# Use latest yocto dev git
#

FILESEXTRAPATHS:prepend := "${THISDIR}/linux-yocto:"

# Patches
SRC_URI += " \
    file://0002-drivers-misc-add-boot-time-module-caching.patch \
    file://0003-moved-headers-in-include-linux.patch \
    file://0004-xadded-sysfs-writeout-moved-file-to-base.patch \
    file://0005-RAID4-5-6-cache-strategy.patch \
    file://0006-init-main.c-Revert-accidental-change.patch \
    file://0007-bootcache-Move-makefile-integration.patch \
"

# Configs
SRC_URI += " \
    file://bootcache-fragment.cfg \
    file://qemu-usage-fragment.cfg \
    "


KBRANCH = "v6.16/standard/base"
LINUX_VERSION = "6.16"

# Ignore upstream issues in the patches for now, issue warnings
INSANE_SKIP:${PN}:append = "patch-status"
ERROR_QA:remove = "patch-status"
WARN_QA:append = "patch-status"
