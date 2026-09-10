FILESEXTRAPATHS:prepend := "${THISDIR}/bootcache/bootcache:"

# Add all the bootcache patches
SRC_URI += " \
    file://0001-base-bootcache-initial-commit.patch \
    file://0002-raid6-Add-bootcache.patch \
    file://0003-crypto-use-bootcache-to-cache-fastest-algorithm.patch \
    file://0004-base-bootcache-Add-bootcache-test-backend.patch \
    file://0005-base-bootcache-Add-bootcache-memory-backend.patch \
    file://0006-base-bootcache-Add-kernel-command-line-backend.patch \
    file://0007-dt-bindings-bootcache-Add-bindings-for-bootcache-bac.patch \
"