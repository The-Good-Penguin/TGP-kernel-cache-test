# Test repo for kernel caching work

## Building and booting qemuarm64

The test is designed to do a full boot from u-boot and not a normal direct kernel boot. The reason is that
we want to use u-boot to load the cache into memory and allow the kernel to pick it up.

The patches for the kernel that bring in the cache structure are includes in `meta-caching/recipes-kernel/linux/linux-yocto`,
and can be replaced and updated to allow the build to be used for testing later revisions of the patch easily.

The base kernel used for testing is the `6.16` release from the `linux-yocto-dev` repo hosted at https://git.yoctoproject.org/linux-yocto-dev

### Building

Normal yocto build system with kas container, this has been tested under ubuntu  eben tested under 

```bash
# If kas is not installed
pip3 install kas
# Execute the build (qemuarm64 version)
kas-container  --ssh-agent --ssh-dir $HOME/.ssh build --update kas/qemu-arm.yml 
```

Resulting binaries are then in `build/tmp/deploy/images/qemuarm64`

### Preparing for Emulation

As we're booting from u-boot rather than directly there is some prep work needed to generate some of the files needed. These use the qemu flash interface, and so need to be miniumum of 64Megbytes in size.

u-boot is placed in one of them, and the other is used for the u-boot enviroment.

```bash
#
# Work is assumed to be performed in "build/tmp/deploy/images/qemuarm64"
#
# Build 2 "flash" binaries
dd if=/dev/zero of=flash.bin bs=1M count=64
dd if=/dev/zero of=uboot-env.bin bs=1M count=64
# Copy uboot binary into the flash.bin
dd if=u-boot.bin of=flash.bin conv=notrunc
```

If the u-boot is updated then the last stage needs to be re-done to ensure the new version is integrated.

### Booting the Emulator

You need to have `qemu-system-aarch64` installed for cross emulation of the arm system. Please use what
ever local package manager installation method is available to perform the iinstallation.

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

## Changing the emulation settings

By default `qemu-system-aarch64` doesn't use a device tree when booting, and the yocto machine config for the build
does not generate one. The qemu binary will generate it's own internally and passes it to the kernel. This is fine
when doing direct booting, however the u-boot `booti` command expects a device tree to be present in memory.

The way to get this device tree is to get qemu to dump a binary one out. Altering the `-M virt` to
`-M virt,dumpdtb=qemu.dtb` will produce the binary file.

This is them copied to the `meta-caching/recipes-kernel/qemu-device-tree/qemu-device-tree` directory.

It was then de-compiled with

```bash
### Decompile
dtc -I dtb -O dts -o qemu.dts qemu.dtb
```

The needed device tree nodes for the caching structure were added.

```
    reserved-memory {
        #address-cells = <2>;
        #size-cells = <2>;
        ranges;

        bootcache_reserved: bootcache-reserved@BFFF0000 {
            no-map;
            reg = <0x00 0xBFFF0000 0x00 0x10000>;
			label = "bootcache_backend_memory";
        };
    };
	bootcache-backend@BFFF0000 {
		compatible = "linux,backend-backend-memory";
		reg = <0x00 0xBFFF0000 0x00 0x10000>;
		memory-region = <&bootcache_reserved>;
	};
```

It was then recompiled with dtc

```bash
### Recompile
dtc -I dts -O dtb -o qemu.dtb qemu.dts
```

The recipe `qemu-device-tree.bb` is then used to included in the boot partition of the disk image for u-boot to load.
If you update the device tree, please remember to ensure the resulting binary file is placed inside the recipe

## Fake Cache Data

The script in `scripts/generate_test_cache.py` can create the needed binary blob for the memory based cache backend.
This blob is loaded by the `u-boot` boot script before kernel booting as a test for the system. The patch inside 
`meta-caching/recipes-bsp/u-boot/u-boot/0001-Update-default-env-for-qemu-test-booting.patch` contains the changes made.

The python script can be easily modified to alter the data contained in the binary, and the resulting binary file
should be copied to `meta-caching/recipes-bsp/bootcache-test-data/bootcache-test-data/bootcache-test-data.bin`
where it will be
included in the `/boot` partition of the build, and loaded by `u-boot`

### Testing the Cache Data

A loadable, out of tree, kernel module is included in `meta-caching/recipes-kernel/bootcache-test` which can be
installed into the running system with

```bash
modprobe bootcache-test
```

Where it will attempt to access multiple cache items to check the binary blob has been parsed correctly. The module
can be loaded and unloaded multiple times if needed for testing purposes.

It can be easily modified to alter it's behavior, for either getting or setting cache entries.

## Building and booting x86

TODO... The current system does not have a x86 friendly backend, this is work in progress.

