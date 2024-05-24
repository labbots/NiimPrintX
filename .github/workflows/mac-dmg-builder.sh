#!/usr/bin/env bash

VERSION="${1}"
APP_NAME="NiimPrintX"
DMG_FILE_NAME="${APP_NAME}-Installer-${VERSION}-MacOSX.dmg"
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

echo killing...; sudo pkill -9 XProtect >/dev/null || true;
echo waiting...; while pgrep XProtect; do sleep 3; done;
# Create the DMG
create-dmg \
  --volname "${VOLUME_NAME}" \
  --background "../assets/images/niimprintx-background.png" \
  --window-pos 200 120 \
  --window-size 800 400 \
  --icon-size 100 \
  --icon "${APP_NAME}.app" 200 190 \
  --hide-extension "${APP_NAME}.app" \
  --app-drop-link 600 185 \
  --no-internet-enable \
  "${DMG_FILE_NAME}" \
  "${SOURCE_FOLDER_PATH}"