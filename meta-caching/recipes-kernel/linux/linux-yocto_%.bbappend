FILESEXTRAPATHS:prepend := "${THISDIR}/${PN}:"

SRC_URI += " \
    file://efi-bootcache-fragment.cfg \
    file://qemu-usage-fragment.cfg \
    file://0001-Add-EFI-backed-bootcache-framework.patch \
    "

