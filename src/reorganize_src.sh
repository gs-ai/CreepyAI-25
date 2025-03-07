#!/bin/zsh

# 1. Create the new folder structure
mkdir -p cli/handler
mkdir -p core
mkdir -p creepy
mkdir -p gui/dialogs
mkdir -p gui/components
mkdir -p gui/main
mkdir -p gui/resources
mkdir -p gui/ui
mkdir -p gui/utils
mkdir -p gui/wizards
mkdir -p gui/backup
mkdir -p include
mkdir -p models/config
mkdir -p others
mkdir -p styles

# 2. Reorganize CLI files:
# Move files from cli/cli into cli/handler (preserving all names)
if [ -d "cli/cli" ]; then
  mv cli/cli/* cli/handler/
  rmdir cli/cli
fi

# 3. For the "creepy" folder, leave the folder and its file names as is.
# If you want to group some files into subfolders without renaming, uncomment below:
# mkdir -p creepy/launchers
# mv creepy/launch_creepyai.py creepy/launchers/

# 4. Reorganize GUI files:
# Move top-level GUI files into the "gui/main" folder (keeping names unchanged)
mv gui/CreepyMainWindow.py gui/main/
mv gui/CreepyUI.py gui/main/
mv gui/PluginConfigCheckdialog.py gui/main/
mv gui/PluginsConfig.py gui/main/
mv gui/PluginsConfigurationDialogUI.py gui/main/
mv gui/UpdateCheckDialogUI.py gui/main/
mv gui/VerifyDeleteDialogUI.py gui/main/
mv gui/creepy_map_view.py gui/main/
mv gui/creepy_resources_rc.py gui/main/
mv gui/creepyai_gui.py gui/main/
mv gui/gui_preview.py gui/main/
mv gui/icon_loader.py gui/main/
mv gui/plugin_dialog_fix.py gui/main/
mv gui/ui_template.py gui/main/
mv gui/update_check_dialog.py gui/main/
mv gui/pyqt5_ui.py gui/main/

# Move backup files (those with .import_backup) into a subfolder
mkdir -p gui/backup
mv gui/*.import_backup gui/backup/ 2>/dev/null

# Move JavaScript files into gui/backup (or another suitable folder)
mv gui/migration.js gui/backup/ 2>/dev/null
mv gui/index.js gui/backup/ 2>/dev/null
mv gui/structure.js gui/backup/ 2>/dev/null
mv gui/update-imports.js gui/backup/ 2>/dev/null
mv gui/personProjectWizard.py gui/backup/ 2>/dev/null

# Move .ui files from the top-level of gui into gui/resources
mv gui/*ai25.ui gui/resources/ 2>/dev/null

echo "Reorganization complete."
