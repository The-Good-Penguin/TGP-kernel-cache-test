#
# Use latest yocto dev git
#

FILESEXTRAPATHS:prepend := "${THISDIR}/linux-yocto:"

# Patches
SRC_URI += " \
    file://0001-base-bootcache-initial-commit.patch \
    file://0002-raid6-Add-bootcache.patch \
    file://0003-crypto-use-bootcache-to-cache-fastest-algorithm.patch \
    file://0004-base-bootcache-Add-bootcache-test-backend.patch \
    file://0005-base-bootcache-Add-bootcache-memory-backend.patch \
    file://0006-dt-bindings-bootcache-Add-bindings-for-bootcache-bac.patch \
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
