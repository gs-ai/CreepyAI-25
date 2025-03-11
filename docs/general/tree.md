(creepyai25ENV) mbaosint@Mac CreepyAI % tree
.
├── LICENSE
├── app
│   ├── __init__.py
│   ├── __pycache__
│   │   └── __init__.cpython-311.pyc
│   ├── controllers
│   │   ├── application_controller.py
│   │   └── map_controller.py
│   ├── core
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   │   ├── __init__.cpython-311.pyc
│   │   │   ├── config.cpython-311.pyc
│   │   │   ├── engine.cpython-311.pyc
│   │   │   ├── import_helper.cpython-311.pyc
│   │   │   └── path_utils.cpython-311.pyc
│   │   ├── check_compatibility.py
│   │   ├── cli
│   │   │   ├── __init__.py
│   │   │   └── handler
│   │   │       ├── __init__.py
│   │   │       ├── cli_handler.py
│   │   │       └── ollama_file_analysis.txt
│   │   ├── config.py
│   │   ├── config_manager.py
│   │   ├── creepy
│   │   │   ├── CreepyMain.py
│   │   │   ├── __init__.py
│   │   │   ├── creepy_resources_rc.py
│   │   │   ├── creepyai
│   │   │   ├── creepyai.py
│   │   │   ├── launch_creepyai.py
│   │   │   └── run_plugin_cli.py
│   │   ├── data
│   │   │   ├── __init__.py
│   │   │   └── data_manager.py
│   │   ├── engine.py
│   │   ├── errors.py
│   │   ├── factory.py
│   │   ├── geo
│   │   │   ├── __init__.py
│   │   │   └── geocoding.py
│   │   ├── git_manager.py
│   │   ├── import_helper.py
│   │   ├── include
│   │   │   ├── __init__.py
│   │   │   ├── __pycache__
│   │   │   │   ├── __init__.cpython-311.pyc
│   │   │   │   ├── config_manager.cpython-311.pyc
│   │   │   │   ├── constants.cpython-311.pyc
│   │   │   │   └── logger_setup.cpython-311.pyc
│   │   │   ├── button_styles.py
│   │   │   ├── config_manager.py
│   │   │   ├── constants.py
│   │   │   ├── creepy_resources.qrc
│   │   │   ├── export_template.html
│   │   │   ├── kml_template.xml
│   │   │   ├── logger_setup.py
│   │   │   ├── map.html
│   │   │   ├── mapSetPoint.html
│   │   │   ├── platform_utils.py
│   │   │   ├── style.qss
│   │   │   └── style_dark.qss
│   │   ├── initialization.py
│   │   ├── logger.py
│   │   ├── main
│   │   │   └── __init__.py
│   │   ├── main.py
│   │   ├── models
│   │   │   ├── Database.py
│   │   │   ├── InputPlugin.py
│   │   │   ├── Location.py
│   │   │   ├── LocationsList.py
│   │   │   ├── PluginConfigurationListModel.py
│   │   │   ├── PluginManager.py
│   │   │   ├── Project.py
│   │   │   ├── ProjectTree.py
│   │   │   ├── ProjectWizardPluginListModel.py
│   │   │   ├── ProjectWizardPossibleTargetsTable.py
│   │   │   ├── ProjectWizardSelectedTargetsTable.py
│   │   │   ├── README.md
│   │   │   ├── ScrapingPlugin.py
│   │   │   ├── __init__.py
│   │   │   ├── config
│   │   │   │   ├── __init__.py
│   │   │   │   └── model_config.yaml
│   │   │   └── model_manager.py
│   │   ├── others
│   │   │   ├── __init__.py
│   │   │   └── main_window.py
│   │   ├── path_utils.py
│   │   ├── plugins
│   │   │   ├── __init__.py
│   │   │   ├── __pycache__
│   │   │   │   ├── __init__.cpython-311.pyc
│   │   │   │   └── standardize.cpython-311.pyc
│   │   │   ├── registry.py
│   │   │   ├── standard
│   │   │   │   ├── __init__.py
│   │   │   │   ├── __pycache__
│   │   │   │   │   ├── exif_extractor.cpython-311.pyc
│   │   │   │   │   └── osm_search.cpython-311.pyc
│   │   │   │   ├── exif_extractor.py
│   │   │   │   └── osm_search.py
│   │   │   └── standardize.py
│   │   ├── resources
│   │   │   ├── README.md
│   │   │   ├── __init__.py
│   │   │   ├── assets
│   │   │   │   ├── README.md
│   │   │   │   └── __init__.py
│   │   │   ├── creepy_resources.qrc
│   │   │   ├── creepyai_resources.qrc
│   │   │   ├── data
│   │   │   │   ├── __init__.py
│   │   │   │   └── location_schema.json
│   │   │   ├── html
│   │   │   │   ├── __init__.py
│   │   │   │   ├── export_template.html
│   │   │   │   └── map_template.html
│   │   │   ├── icons.py
│   │   │   ├── resource_manager.py
│   │   │   ├── styles
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base.qss
│   │   │   │   └── dark.qss
│   │   │   └── templates
│   │   │       ├── __init__.py
│   │   │       ├── plugins
│   │   │       │   ├── __init__.py
│   │   │       │   ├── main.py.template
│   │   │       │   └── manifest.json.template
│   │   │       └── projects
│   │   │           ├── __init__.py
│   │   │           └── config.yaml.template
│   │   ├── style_manager.py
│   │   ├── styles
│   │   │   ├── __init__.py
│   │   │   └── map-icons.css
│   │   ├── theme_manager.py
│   │   ├── ui_bridge.py
│   │   ├── update_env_detection.py
│   │   ├── update_exports.py
│   │   ├── utils
│   │   │   ├── __init__.py
│   │   │   ├── logging_utils.py
│   │   │   ├── resource_manager.py
│   │   │   └── version_utils.py
│   │   ├── utils.py
│   │   └── validate_paths.py
│   ├── data
│   │   └── data_pipeline.py
│   ├── exporters
│   │   ├── gpx_exporter.py
│   │   └── kml_exporter.py
│   ├── gui
│   │   ├── CheckUpdateDialog.py
│   │   ├── README.md
│   │   ├── SettingsDialog.py
│   │   ├── UpdateCheckDialog.py
│   │   ├── VerifyDeleteDialog.py
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   │   ├── __init__.cpython-311.pyc
│   │   │   ├── map_view.cpython-311.pyc
│   │   │   └── plugin_browser.cpython-311.pyc
│   │   ├── aboutDialog.py
│   │   ├── common
│   │   │   └── __init__.py
│   │   ├── exportDirDialog.py
│   │   ├── filterLocationsDateDialog.py
│   │   ├── filterLocationsPointDialog.py
│   │   ├── fix_imports.py
│   │   ├── main
│   │   │   ├── CreepyMain.py
│   │   │   ├── CreepyMainWindow.py
│   │   │   ├── CreepyUI.py
│   │   │   ├── PluginConfigCheckdialog.py
│   │   │   ├── PluginsConfig.py
│   │   │   ├── PluginsConfigurationDialogUI.py
│   │   │   ├── UpdateCheckDialogUI.py
│   │   │   ├── VerifyDeleteDialogUI.py
│   │   │   ├── __init__.py
│   │   │   ├── creepy_map_view.py
│   │   │   ├── creepy_resources_rc.py
│   │   │   ├── creepyai_gui.py
│   │   │   ├── creepyai_gui_fixed.py
│   │   │   ├── gui_preview.py
│   │   │   ├── icon_loader.py
│   │   │   ├── plugin_dialog_fix.py
│   │   │   ├── pyqt5_ui.py
│   │   │   ├── ui_template.py
│   │   │   └── update_check_dialog.py
│   │   ├── map_resources
│   │   │   └── __init__.py
│   │   ├── map_view.py
│   │   ├── plugin_browser.py
│   │   ├── plugin_config_dialog.py
│   │   ├── resources
│   │   │   ├── __init__.py
│   │   │   ├── __pycache__
│   │   │   │   ├── __init__.cpython-311.pyc
│   │   │   │   └── icons.cpython-311.pyc
│   │   │   ├── aboutDialog_ai25.ui
│   │   │   ├── about_dialog.ui
│   │   │   ├── creepyai_mainwindow.ui
│   │   │   ├── creepyai_mainwindow.ui.bak
│   │   │   ├── exportDirDialog_ai25.ui
│   │   │   ├── filterLocationsDateDialog_ai25.ui
│   │   │   ├── filterLocationsPointDialog_ai25.ui
│   │   │   ├── icons
│   │   │   │   └── plugin_icons.py
│   │   │   ├── icons.py
│   │   │   ├── map.html
│   │   │   ├── personProjectWizard_ai25.ui
│   │   │   ├── personProject_ai25.ui
│   │   │   ├── pluginConfigCheckDialog_ai25.ui
│   │   │   ├── pluginImportWizard_ai25.ui
│   │   │   ├── plugin_config_dialog.ui
│   │   │   ├── pluginsConfig_ai25.ui
│   │   │   ├── settings_dialog.ui
│   │   │   └── styles
│   │   │       └── plugin_list.css
│   │   ├── ui
│   │   │   ├── __init__.py
│   │   │   ├── __pycache__
│   │   │   │   ├── __init__.cpython-311.pyc
│   │   │   │   └── creepyai_mainwindow_ui.cpython-311.pyc
│   │   │   ├── components
│   │   │   │   ├── dashboard_view.py
│   │   │   │   ├── location_list_view.py
│   │   │   │   └── timeline_view.py
│   │   │   ├── creepyai25_ui.py
│   │   │   ├── creepyai_mainwindow.ui
│   │   │   ├── creepyai_mainwindow_ui.py
│   │   │   ├── dialogs
│   │   │   │   ├── about_dialog.py
│   │   │   │   ├── error_dialog.py
│   │   │   │   ├── import_dialog.py
│   │   │   │   ├── location_detail_dialog.py
│   │   │   │   ├── preferences_dialog.py
│   │   │   │   └── welcome_dialog.py
│   │   │   ├── fallback.py
│   │   │   └── main
│   │   │       ├── __init__.py
│   │   │       ├── creepyai_gui.py
│   │   │       ├── main_window.py
│   │   │       └── toolbar_manager.py
│   │   ├── updateCheckDialog.ui
│   │   ├── utils
│   │   │   └── __init__.py
│   │   ├── verifyDeleteDialog.ui
│   │   ├── widgets
│   │   │   └── __init__.py
│   │   └── wizards
│   │       ├── PersonProjectWizard.py
│   │       └── __init__.py
│   ├── main.py
│   ├── models
│   │   ├── Location.py
│   │   ├── Project.py
│   │   ├── ProjectTree.py
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   │   ├── Location.cpython-311.pyc
│   │   │   ├── Project.cpython-311.pyc
│   │   │   ├── ProjectTree.cpython-311.pyc
│   │   │   ├── __init__.cpython-311.pyc
│   │   │   └── location_data.cpython-311.pyc
│   │   └── location_data.py
│   ├── plugin_registry.py
│   ├── plugins
│   │   ├── DummyPlugin.py
│   │   ├── GeoIPPlugin.py
│   │   ├── PluginIntegration.py
│   │   ├── SocialMediaPlugin.py
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   │   ├── __init__.cpython-311.pyc
│   │   │   ├── base_plugin.cpython-311.pyc
│   │   │   ├── enhanced_geocoding_helper.cpython-311.pyc
│   │   │   ├── geocoding_helper.cpython-311.pyc
│   │   │   ├── plugin_adapter.cpython-311.pyc
│   │   │   ├── plugin_base.cpython-311.pyc
│   │   │   ├── plugin_manager.cpython-311.pyc
│   │   │   └── plugin_paths.cpython-311.pyc
│   │   ├── base_plugin.py
│   │   ├── benchmark_plugins.py
│   │   ├── configs
│   │   │   ├── __init__.py
│   │   │   └── __pycache__
│   │   │       └── __init__.cpython-311.pyc
│   │   ├── data_extraction
│   │   │   ├── __init__.py
│   │   │   ├── __pycache__
│   │   │   │   └── __init__.cpython-311.pyc
│   │   │   ├── email_plugin.py
│   │   │   ├── google_takeout_plugin.py
│   │   │   └── idcrawl_plugin.py
│   │   ├── descriptors
│   │   │   ├── __init__.py
│   │   │   └── __pycache__
│   │   │       └── __init__.cpython-311.pyc
│   │   ├── email_plugin.py
│   │   ├── enhanced_geocoding_helper.py
│   │   ├── example_plugin.py
│   │   ├── facebook_plugin.py
│   │   ├── flickr_plugin.py
│   │   ├── foursquare_plugin.py
│   │   ├── geocoding_helper.py
│   │   ├── google_maps_plugin.py
│   │   ├── google_takeout_plugin.py
│   │   ├── idcrawl_plugin.py
│   │   ├── init_plugins.py
│   │   ├── instagram_plugin.py
│   │   ├── linkedin_plugin.py
│   │   ├── local_files_plugin.py
│   │   ├── location_history_plugin.py
│   │   ├── location_services
│   │   │   ├── GeoIPPlugin.py
│   │   │   ├── __init__.py
│   │   │   ├── __pycache__
│   │   │   │   └── __init__.cpython-311.pyc
│   │   │   ├── foursquare_plugin.py
│   │   │   ├── google_maps_plugin.py
│   │   │   ├── location_history_plugin.py
│   │   │   ├── wifi_analysis_plugin.py
│   │   │   └── wifi_mapper_plugin.py
│   │   ├── other
│   │   │   ├── PluginIntegration.py
│   │   │   ├── SocialMediaPlugin.py
│   │   │   ├── __init__.py
│   │   │   ├── __pycache__
│   │   │   │   ├── PluginIntegration.cpython-311.pyc
│   │   │   │   ├── __init__.cpython-311.pyc
│   │   │   │   ├── benchmark_plugins.cpython-311.pyc
│   │   │   │   ├── flickr_plugin.cpython-311.pyc
│   │   │   │   ├── init_plugins.cpython-311.pyc
│   │   │   │   ├── local_files_plugin.cpython-311.pyc
│   │   │   │   └── plugins.cpython-311.pyc
│   │   │   ├── base_plugin.py
│   │   │   ├── benchmark_plugins.py
│   │   │   ├── flickr_plugin.py
│   │   │   ├── init_plugins.py
│   │   │   ├── local_files_plugin.py
│   │   │   └── plugins.py
│   │   ├── pinterest_plugin.py
│   │   ├── plugin_adapter.py
│   │   ├── plugin_base.py
│   │   ├── plugin_cli.py
│   │   ├── plugin_compatibility.py
│   │   ├── plugin_creator.py
│   │   ├── plugin_dashboard.py
│   │   ├── plugin_data_manager.py
│   │   ├── plugin_fixer.py
│   │   ├── plugin_health.py
│   │   ├── plugin_manager.py
│   │   ├── plugin_monitor.py
│   │   ├── plugin_paths.py
│   │   ├── plugin_registry.py
│   │   ├── plugin_test.py
│   │   ├── plugin_testing_utils.py
│   │   ├── plugin_uimap.py
│   │   ├── plugin_utils.py
│   │   ├── plugin_validator.py
│   │   ├── plugins.py
│   │   ├── plugins.yaml
│   │   ├── run_plugin_cli.py
│   │   ├── snapchat_plugin.py
│   │   ├── social_media
│   │   │   ├── __init__.py
│   │   │   ├── __pycache__
│   │   │   │   ├── __init__.cpython-311.pyc
│   │   │   │   ├── facebook_plugin.cpython-311.pyc
│   │   │   │   ├── instagram_plugin.cpython-311.pyc
│   │   │   │   ├── linkedin_plugin.cpython-311.pyc
│   │   │   │   ├── pinterest_plugin.cpython-311.pyc
│   │   │   │   ├── plugin_tester.cpython-311.pyc
│   │   │   │   ├── snapchat_plugin.cpython-311.pyc
│   │   │   │   ├── tiktok_plugin.cpython-311.pyc
│   │   │   │   ├── twitter_plugin.cpython-311.pyc
│   │   │   │   └── yelp_plugin.cpython-311.pyc
│   │   │   ├── facebook_plugin.py
│   │   │   ├── instagram_plugin.py
│   │   │   ├── linkedin_plugin.py
│   │   │   ├── pinterest_plugin.py
│   │   │   ├── plugin_tester.py
│   │   │   ├── snapchat_plugin.py
│   │   │   ├── tiktok_plugin.py
│   │   │   ├── twitter_plugin.py
│   │   │   └── yelp_plugin.py
│   │   ├── src
│   │   │   ├── __init__.py
│   │   │   ├── __pycache__
│   │   │   │   └── __init__.cpython-311.pyc
│   │   │   ├── base_plugin.py
│   │   │   └── plugins.py
│   │   ├── test_plugins.py
│   │   ├── tiktok_plugin.py
│   │   ├── tools
│   │   │   ├── DummyPlugin.py
│   │   │   ├── __init__.py
│   │   │   ├── __pycache__
│   │   │   │   ├── __init__.cpython-311.pyc
│   │   │   │   ├── plugin_adapter.cpython-311.pyc
│   │   │   │   ├── plugin_base.cpython-311.pyc
│   │   │   │   ├── plugin_compatibility.cpython-311.pyc
│   │   │   │   ├── plugin_health.cpython-311.pyc
│   │   │   │   └── plugin_paths.cpython-311.pyc
│   │   │   ├── example_plugin.py
│   │   │   ├── plugin_adapter.py
│   │   │   ├── plugin_base.py
│   │   │   ├── plugin_cli.py
│   │   │   ├── plugin_compatibility.py
│   │   │   ├── plugin_creator.py
│   │   │   ├── plugin_dashboard.py
│   │   │   ├── plugin_data_manager.py
│   │   │   ├── plugin_fixer.py
│   │   │   ├── plugin_health.py
│   │   │   ├── plugin_monitor.py
│   │   │   ├── plugin_paths.py
│   │   │   ├── plugin_registry.py
│   │   │   ├── plugin_test.py
│   │   │   ├── plugin_testing_utils.py
│   │   │   ├── plugin_uimap.py
│   │   │   ├── plugin_utils.py
│   │   │   ├── plugin_validator.py
│   │   │   ├── run_plugin_cli.py
│   │   │   └── test_plugins.py
│   │   ├── twitter_plugin.py
│   │   ├── wifi_analysis_plugin.py
│   │   ├── wifi_mapper_plugin.py
│   │   └── yelp_plugin.py
│   ├── resources
│   │   ├── icons
│   │   │   └── README.md
│   │   └── map
│   │       └── index.html
│   ├── ui
│   │   └── plugin_selector.py
│   ├── utilities
│   │   ├── PluginManager.py
│   │   ├── WebScrapingUtility.py
│   │   ├── __init__.py
│   │   ├── folium_stub.py
│   │   ├── pyqt_manager.py
│   │   ├── webengine.py
│   │   └── webengine_compat.py
│   └── utils
│       ├── ExportUtils.py
│       ├── GeneralUtilities.py
│       ├── GeocodingUtility.py
│       ├── Initialization.py
│       ├── ResourceLoader.py
│       ├── __init__.py
│       ├── cli_utils.py
│       ├── create_app_icon.py
│       ├── create_missing_icons.py
│       ├── date_utils.py
│       ├── error_handling.py
│       ├── file_utils.py
│       ├── formatter.py
│       ├── gui_compatibility.py
│       ├── icon_mapping.py
│       ├── icon_path_fix.py
│       ├── icons.py
│       ├── location_clustering.py
│       ├── string_utils.py
│       ├── system_info.py
│       └── validation.py
├── assets
│   ├── icons
│   ├── images
│   └── sounds
├── check_plugins.py
├── cleanup_original_plugins.py
├── configs
│   ├── README.md
│   ├── __init__.py
│   ├── app
│   │   └── kml_template.xml
│   ├── app_config.json
│   ├── config_compat.py
│   ├── config_loader.py
│   ├── config_utils.py
│   ├── defaults.py
│   ├── logging
│   ├── logging_config.json
│   ├── plugins
│   │   ├── DocumentAnalyzer.conf
│   │   ├── DummyPlugin.conf
│   │   ├── FileSystemWatcher.conf
│   │   ├── GeoIPPlugin.conf
│   │   ├── GeoTrackingPlugin.conf
│   │   ├── LocalDataHarvester.conf
│   │   ├── MetadataExtractor.conf
│   │   ├── NetworkScanner.conf
│   │   ├── OfflineReconPlugin.conf
│   │   ├── PasswordAuditor.conf
│   │   ├── SocialMediaPlugin.conf
│   │   ├── SocialMediaScraper.conf
│   │   ├── WifiMonitor.conf
│   │   ├── enhanced_geocoding_helper.conf
│   │   ├── plugin_schema.json
│   │   └── plugins.yaml
│   ├── reorganize_configs.py
│   └── settings_manager.py
├── data
├── docs
│   ├── SOCIAL_MEDIA_PLUGINS.md
│   ├── general
│   │   ├── CHANGELOG.md
│   │   ├── HOWTO.md
│   │   ├── README.md
│   │   ├── SECURITY.md
│   │   ├── TODO.md
│   │   ├── configuration.md
│   │   ├── next_steps.md
│   │   └── tree.md
│   ├── guides
│   │   ├── README-plugins-cli.md
│   │   ├── kml_export_guide.md
│   │   ├── migration_guide.md
│   │   ├── plugin_development.md
│   │   ├── plugin_development_guide.md
│   │   └── python_requirements.md
│   ├── misc
│   │   └── creepy_bckup.txt
│   └── troubleshooting
│       ├── IconUsage.md
│       ├── ManualFixInstructions.md
│       └── MapIconTroubleshooting.md
├── fix_plugin_syntax.py
├── generate_ui.sh
├── include
│   ├── __init__.py
│   └── map.html
├── inspect_plugin_directories.py
├── logs
├── move_plugins.py
├── projects
├── regenerate_ui.py
├── requirements.txt
├── resources
│   ├── README.md
│   ├── __init__.py
│   ├── assets
│   │   ├── __init__.py
│   │   ├── asset_manager.py
│   │   ├── icons
│   │   │   ├── __init__.py
│   │   │   └── map
│   │   │       ├── info_16dp_000000.png
│   │   │       └── info_24dp_000000.png
│   │   ├── images
│   │   └── sounds
│   ├── creepy.qrc
│   ├── data
│   ├── html
│   │   └── map_template.html
│   ├── icons
│   │   ├── __init__.py
│   │   ├── add_16dp_000000.png
│   │   ├── add_24dp_000000.png
│   │   ├── add_circle_outline_24dp_000000.png
│   │   ├── analytics_24dp_000000.png
│   │   ├── app_icon.png
│   │   ├── clear_24dp_000000.png
│   │   ├── clear_all_16dp_000000.png
│   │   ├── clear_all_24dp_000000.png
│   │   ├── close_16dp_000000.png
│   │   ├── close_24dp_000000.png
│   │   ├── date_range_24dp_000000.png
│   │   ├── default.png
│   │   ├── edit_note_16dp_000000.png
│   │   ├── edit_note_24dp_000000.png
│   │   ├── export_24dp_000000.png
│   │   ├── file_download_24dp_000000.png
│   │   ├── folder_open_24dp_000000.png
│   │   ├── menu_24dp_000000.png
│   │   ├── new.png
│   │   ├── open.png
│   │   ├── open_in_new_24dp_000000.png
│   │   ├── person_24dp_000000.png
│   │   ├── person_32dp_000000.png
│   │   ├── place_24dp_000000.png
│   │   ├── play_arrow_24dp_000000.png
│   │   ├── refresh_24dp_000000.png
│   │   ├── remove_16dp_000000.png
│   │   ├── remove_24dp_000000.png
│   │   ├── remove_circle_outline_24dp_000000.png
│   │   ├── save.png
│   │   ├── save_24dp_000000.png
│   │   ├── security_24dp_000000.png
│   │   ├── settings.png
│   │   ├── settings_24dp_000000.png
│   │   ├── settings_32dp_000000.png
│   │   └── toggle_off_24dp_000000.png
│   ├── icons.py
│   ├── leaflet
│   │   ├── __init__.py
│   │   └── images
│   │       └── marker-icon.png
│   ├── resource_manager.py
│   ├── samples
│   │   └── config.yaml.sample
│   ├── styles
│   │   ├── base.qss
│   │   ├── dark.qss
│   │   ├── icons.css
│   │   └── light.qss
│   └── templates
│       ├── default_project.yaml
│       ├── plugins
│       │   ├── main.py.template
│       │   └── manifest.json.template
│       └── projects
│           └── config.yaml.template
├── scripts
│   └── download_icons.py
├── temp
├── test_categorized_plugins.py
└── test_plugin_map.py

111 directories, 513 files
(creepyai25ENV) mbaosint@Mac CreepyAI % 