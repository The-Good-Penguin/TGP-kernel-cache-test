#
# Common packages for both architectures
#
IMAGE_INSTALL:append = " \
    kernel-module-bootcache-test \
"
#
# Conditional packages and WIC file for x86-64
#
IMAGE_INSTALL:append:qemux86-64 = " \
    grub-efi \
    dosfstools \
    "
#
# Conditional packages and WIC file for ARM64
#
IMAGE_INSTALL:append:qemuarm64 = " \
    u-boot \
    u-boot-fw-utils \
    "

IMAGE_BOOT_FILES:qemuarm64 += "Image qemu.dtb bootcache-test-data.bin"
WKS_FILE_DEPENDS:qemuarm64 += "virtual/kernel qemu-device-tree bootcache-test-data"

do_image_wic[depends] += "virtual/kernel:do_deploy"
do_image_wic[depends] += "qemu-device-tree:do_deploy"
do_image_wic[depends] += "bootcache-test-data:do_deploy"