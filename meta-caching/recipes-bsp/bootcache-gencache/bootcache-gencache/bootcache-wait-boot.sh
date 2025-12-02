#! /bin/sh

# Wait for systemd to finish booting
while ! systemctl is-system-running | grep -qE "running|degraded"; do
  echo "waiting for systemd to finish booting..."
  dbus-wait org.freedesktop.systemd1.Manager StartupFinished
done

echo "systemd finished booting...processing cache to /tmp/test.bin"

bootcache-gencache --source-dir /sys/kernel/bootcache --output-file /tmp/test.bin
