FILESEXTRAPATHS:prepend := "${THISDIR}/bootcache:"

# Add the Plan9 stuff for testing
SRC_URI += " \
    file://qemu-usage-fragment.cfg \
    file://bootcache.cfg \
"
