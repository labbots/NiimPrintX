#!/usr/bin/env bash

VERSION="${1}"
ARCH="${2}"
APP_NAME="NiimPrintX"
DMG_FILE_NAME="${APP_NAME}-Installer-${VERSION}-MacOSX-${ARCH}.dmg"
VOLUME_NAME="${APP_NAME} Installer"
SOURCE_FOLDER_PATH="NiimprintX/"
DIST_FOLDER="dist"

cd "${DIST_FOLDER}"

if [[ -d "${APP_NAME}.app" ]]
then
  [[ -d "${SOURCE_FOLDER_PATH}" ]] && rm -rf "${SOURCE_FOLDER_PATH}"
  mkdir "${SOURCE_FOLDER_PATH}"
  cp -r "${APP_NAME}.app" "${SOURCE_FOLDER_PATH}"
fi

# Since create-dmg does not clobber, be sure to delete previous DMG
[[ -f "${DMG_FILE_NAME}" ]] && rm "${DMG_FILE_NAME}"

# Function to kill and wait for XProtect processes
kill_xprotect() {
  echo "Killing XProtect processes..."
  sudo pkill -9 XProtect || true
  echo "Waiting for XProtect processes to terminate..."
  while pgrep XProtect; do sleep 5; done
  echo "XProtect processes terminated."
  sudo mdutil -a -i off || true
}


# Function to unmount all mounted disk images
unmount_all_disks() {
  echo "Unmounting all mounted disk images..."
  while read -r disk; do
    hdiutil detach "$disk" || true
  done < <(hdiutil info | grep '/dev/' | awk '{print $1}')
  echo "Unmounted all disk images."
}

# Create the DMG
# Retry logic to handle resource busy error
success=0

for i in {1..5}; do
  kill_xprotect
  unmount_all_disks
  sudo create-dmg \
    --volname "${VOLUME_NAME}" \
    --background "../assets/images/niimprintx-background.png" \
    --window-pos 200 120 \
    --window-size 800 400 \
    --icon-size 100 \
    --icon "${APP_NAME}.app" 200 190 \
    --hide-extension "${APP_NAME}.app" \
    --app-drop-link 600 185 \
    --no-internet-enable \
    --hdiutil-verbose \
    "${DMG_FILE_NAME}" \
    "${SOURCE_FOLDER_PATH}" && { success=1; break; }

  echo "Attempt $i: Resource busy, retrying in 5 seconds..."
  sleep 5
done

if [[ $success -ne 1 ]]; then
    echo "Failed to create disk image after 5 attempts."
    exit 1
fi