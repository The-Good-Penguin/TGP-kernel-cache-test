SUMMARY = "bootcache binary test data"
DESCRIPTION = "Recipe to include a binary data blob of cache data for testing"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"

SRC_URI = "file://bootcache-test-data.bin"

inherit deploy

do_deploy() {
    install -d ${DEPLOYDIR}
    install -m 0664 ${WORKDIR}/bootcache-test-data.bin ${DEPLOYDIR}/
}

addtask do_deploy after do_compile before do_build

