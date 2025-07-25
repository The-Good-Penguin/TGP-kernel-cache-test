#
# Add fstab entries.
#
do_install_append () {
    cat >> ${D}${sysconfdir}/fstab <<EOF

# Plan9 host mount
host               /host                9p      trans=virtio,version=9p2000.L   0       0

EOF
}
