SUMMARY = "Generate Bootcache binary data from sysfs"
DESCRIPTION = "Recipe to include tools to generate bootcache binary data from a running system via the sysfs interface"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"

SRC_URI = " \
    file://bootcache-gencache.py \
    file://bootcache-gencache.service \
    file://bootcache-wait-boot.sh \
"

S = "${WORKDIR}"

RDEPENDS:${PN} += " python3 dbus-wait"
REQUIRED_DISTRO_FEATURES= " systemd"
inherit systemd

# SYSTEMD_AUTO_ENABLE:${PN} = "disable"
SYSTEMD_SERVICE:${PN} = "bootcache-gencache.service"

do_install:append() {
    install -d 644 ${D}${sbindir}
    install -m 0755 ${WORKDIR}/bootcache-gencache.py  ${D}${sbindir}/bootcache-gencache
    install -m 0755 ${WORKDIR}/bootcache-wait-boot.sh  ${D}${sbindir}/bootcache-wait-boot

    install -d ${D}${systemd_system_unitdir}
    install -m 0644 ${WORKDIR}/bootcache-gencache.service  ${D}${systemd_system_unitdir}
}

FILES:${PN} += "${sbindir}/bootcache-gencache"
FILES:${PN} += "${sbindir}/bootcache-wait-boot"
FILES:${PN} += "${systemd_system_unitdir}/bootcache-gencache.service"