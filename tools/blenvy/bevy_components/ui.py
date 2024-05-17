def draw_settings_ui(layout, registry):
    row = layout.row()
    col = row.column()
    col.enabled = False
    col.prop(registry, "schemaPath", text="Registry Schema path")
    col = row.column()
    col.operator(operator="blenvy.open_schemafilebrowser", text="Browse for registry schema file (json)")

    layout.separator()
    layout.operator(operator="object.reload_registry", text="reload registry" , icon="FILE_REFRESH")

    layout.separator()
    row = layout.row()

    row.prop(registry, "watcher_enabled", text="enable registry file polling")
    row.prop(registry, "watcher_poll_frequency", text="registry file poll frequency (s)")

    layout.separator()
    layout.separator()