SUMMARY = "Upstream Linus Mainline Kernel"
SECTION = "kernel"
LICENSE = "GPL-2.0-only"
LIC_FILES_CHKSUM = "file://COPYING;md5=6bc538ed5abe897c867d73ad2967ffb8"

inherit kernel
inherit kernel-yocto

FILESEXTRAPATHS:prepend := "${THISDIR}/${PN}:"

# Mainline kernel
SRC_URI = "git://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git;protocol=https;branch=master;nobranch=1"

# Add the defconfig to the SRC_URI
SRC_URI += "file://defconfig"

KBRANCH = "master"
# Update based on current version
LINUX_VERSION = "7.0"
# Use a specific tag or SRCREV (hash)
SRCREV = "v${LINUX_VERSION}" 
PV = "${LINUX_VERSION}+git${SRCPV}"
# Warning: Ensure your hardware is supported upstream!
COMPATIBLE_MACHINE = "(.*)"