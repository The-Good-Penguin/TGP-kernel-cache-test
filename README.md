# Test repo for kernel caching work

## Building and booting qemuarm64

The test is designed to do a full boot from u-boot and not a normal direct kernel boot. The reason is that we want to use u-boot to load the cache into memory and allow the kernel to pick it up.

### Building

Normal yocto build system with

```bash
kas-container  --ssh-agent --ssh-dir $HOME/.ssh build --update kas/qemu-arm.yml 
```

Resulting binaries are then in `build/tmp/deploy/images/qemuarm64`

### Preparing for Emulation

As we're booting from u-boot rather than directly there is some prep work needed to generate some of the files needed. These use the qemu flash interface, and so need to be miniumum of 64Megbytes in size.

u-boot is placed in one of them, and the other is used for the u-boot enviroment.

```bash
# Build 2 "flash" binaries
dd if=/dev/zero of=flash.bin bs=1M count=64
dd if=/dev/zero of=uboot-env.bin bs=1M count=64
# Copy uboot binary into the flash.bin
dd if=u-boot.bin of=flash.bin conv=notrunc
```

If the u-boot is updated then the last stage needs to be re-done to ensure the new version is used.

### Booting the Emulator

You need to have `qemu-system-aarch64` installed for cross emulation of the arm system.

```bash
qemu-system-aarch64 \
  -M virt \
  -cpu cortex-a57 -smp 4 -m 2G \
  -nographic \
  -serial mon:stdio \
  -drive file=core-image-minimal-qemuarm64.rootfs.wic.qcow2,format=qcow2,if=virtio \
  -drive if=pflash,format=raw,file=flash.bin,readonly=on,unit=0 \
  -drive if=pflash,format=raw,file=uboot-env.bin,unit=1 
```

This should bring up a u-boot terminal and then after the 3 second delay it should boot into the kernel.

### Changing the emulation settings

By default `qemu-system-aarch64` doesn't use a device tree when booting, and the yocto machine config for the build does not generate one. The qemu binary will generate it's own internally and passes it to the kernel. This is fine when doing direct booting, however the u-boot `booti` command expects a device tree to be present in memory.

The way to get this device tree is to get qemu to dump a binary one out. Altering the `-M virt` to `-M virt,dumpdtb=qemu.dtb` will produce the binary file.

This is them copied to the `meta-caching/recipes-kernel/qemu-device-tree/qemu-device-tree` directory where the `qemu-device-tree.bb` recipe will ensure it is included in the boot partition of the disk image for u-boot to load.

## Building and booting x86

TODO... but it involves qemu and some stuff using uefi bios...just make sure not the secure mode uefi bios, or things don't work too well

See [Boot_Cache_Test_x86.xml](./Boot_Cache_Test_x86.xml) for an example `libvirt` machine config

