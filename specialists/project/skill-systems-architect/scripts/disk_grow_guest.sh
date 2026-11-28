#!/usr/bin/env bash
# Grow the partition and filesystem under one mount point to fill its (already enlarged) disk, online.
#
# Run line (inside the guest, as root):  bash disk_grow_guest.sh [--apply] [--mount /]
# Remote:  ssh root@host 'bash -s -- --apply --mount /' < disk_grow_guest.sh   (disk_grow.py does this)
# Safety: without --apply it only reads and prints the plan (growpart --dry-run). With --apply it rescans the disk,
# runs growpart, pvresize/lvextend for a single-PV LVM root, then resize2fs, xfs_growfs or btrfs resize. It never shrinks:
# growpart and the filesystem tools only extend. Refuses multi-PV volume groups and unknown filesystems.
# Exit 0: done or nothing to do, 1: a step failed, 2: bad arguments or unsupported layout.

set -euo pipefail

APPLY=0
MOUNT=/

# usage: print the run line and exit 2.
# Args: none. Returns: never (exit 2). Raises: none.
usage() {
  echo "usage: $0 [--apply] [--mount <path>]" >&2
  exit 2
}

# run: print a command, and run it only with --apply.
# Args: the command and its arguments. Returns: the command's status, or 0 in plan mode. Raises: none.
run() {
  echo "+ $*"
  if [[ ${APPLY} -eq 1 ]]; then
    "$@"
  fi
}

# grow_partition: growpart one partition; NOCHANGE (exit 1 with that word) counts as success.
# Args: $1 parent disk name (nvme0n1), $2 partition number. Returns: 0 grown or nothing to grow, 1 failure. Raises: none.
grow_partition() {
  local disk=$1 num=$2 out rc
  command -v growpart >/dev/null || {
    echo "growpart missing (package cloud-guest-utils / cloud-utils-growpart)" >&2
    return 1
  }
  if [[ -w /sys/class/block/${disk}/device/rescan ]]; then
    run sh -c "echo 1 > /sys/class/block/${disk}/device/rescan"
  fi
  if [[ ${APPLY} -eq 1 ]]; then
    echo "+ growpart /dev/${disk} ${num}"
    out=$(growpart "/dev/${disk}" "${num}" 2>&1) && rc=0 || rc=$?
  else
    echo "+ growpart --dry-run /dev/${disk} ${num}"
    out=$(growpart --dry-run "/dev/${disk}" "${num}" 2>&1) && rc=0 || rc=$?
  fi
  echo "${out}"
  if [[ ${rc} -eq 0 ]] || grep -q NOCHANGE <<<"${out}"; then
    return 0
  fi
  return 1
}

# grow_fs: extend the filesystem on a block device to fill it.
# Args: $1 device path, $2 filesystem type. Returns: the tool's status. Raises: exit 2 for an unsupported type.
grow_fs() {
  local dev=$1 fstype=$2
  case ${fstype} in
    ext2 | ext3 | ext4) run resize2fs "${dev}" ;;
    xfs) run xfs_growfs "${MOUNT}" ;;
    btrfs) run btrfs filesystem resize max "${MOUNT}" ;;
    *)
      echo "unsupported filesystem ${fstype} on ${dev}" >&2
      exit 2
      ;;
  esac
}

while [[ $# -gt 0 ]]; do
  case $1 in
    --apply) APPLY=1 ;;
    --mount)
      [[ $# -ge 2 ]] || usage
      MOUNT=$2
      shift
      ;;
    *) usage ;;
  esac
  shift
done

[[ $(id -u) -eq 0 ]] || {
  echo "run as root" >&2
  exit 2
}
findmnt -n "${MOUNT}" >/dev/null || {
  echo "${MOUNT} is not a mount point" >&2
  exit 2
}

FSTYPE=$(findmnt -nvo FSTYPE "${MOUNT}" | tr -d ' ')
MAJMIN=$(findmnt -nvo MAJ:MIN "${MOUNT}" | tr -d ' ')
NAME=$(basename "$(readlink -f "/sys/dev/block/${MAJMIN}")")
TYPE=$(lsblk -dno TYPE "/dev/${NAME}")
echo "mount ${MOUNT}: device ${NAME} type ${TYPE} fs ${FSTYPE} (mode: $([[ ${APPLY} -eq 1 ]] && echo apply || echo plan))"
lsblk -o NAME,SIZE,TYPE,MOUNTPOINT "/dev/$(lsblk -dno PKNAME "/dev/${NAME}" 2>/dev/null || echo "${NAME}")" 2>/dev/null || lsblk
df -hT "${MOUNT}"

case ${TYPE} in
  part)
    DISK=$(lsblk -dno PKNAME "/dev/${NAME}")
    grow_partition "${DISK}" "$(cat "/sys/class/block/${NAME}/partition")"
    grow_fs "/dev/${NAME}" "${FSTYPE}"
    ;;
  disk)
    if [[ -w /sys/class/block/${NAME}/device/rescan ]]; then
      run sh -c "echo 1 > /sys/class/block/${NAME}/device/rescan"
    fi
    grow_fs "/dev/${NAME}" "${FSTYPE}"
    ;;
  lvm)
    LV=/dev/mapper/$(cat "/sys/class/block/${NAME}/dm/name")
    VG=$(lvs --noheadings -o vg_name "${LV}" | tr -d ' ')
    mapfile -t PVS < <(pvs --noheadings -o pv_name -S "vg_name=${VG}" | tr -d ' ')
    if [[ ${#PVS[@]} -ne 1 ]]; then
      echo "volume group ${VG} has ${#PVS[@]} PVs; grow it by hand" >&2
      exit 2
    fi
    PV=${PVS[0]}
    PVNAME=$(basename "$(readlink -f "${PV}")")
    if [[ $(lsblk -dno TYPE "/dev/${PVNAME}") == part ]]; then
      grow_partition "$(lsblk -dno PKNAME "/dev/${PVNAME}")" "$(cat "/sys/class/block/${PVNAME}/partition")"
    fi
    run pvresize "${PV}"
    if [[ ${APPLY} -eq 1 && $(vgs --noheadings -o vg_free_count "${VG}" | tr -d ' ') -eq 0 ]]; then
      echo "volume group ${VG} has no free extents: nothing to extend"
    else
      # lvextend -r runs the filesystem grow itself (fsadm).
      run lvextend -r -l +100%FREE "${LV}"
    fi
    ;;
  *)
    echo "unsupported block device type ${TYPE} for ${MOUNT}" >&2
    exit 2
    ;;
esac

if [[ ${APPLY} -eq 1 ]]; then
  df -hT "${MOUNT}"
fi
