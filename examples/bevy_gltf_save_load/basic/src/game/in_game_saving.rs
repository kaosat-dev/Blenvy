use bevy::{core_pipeline::clear_color::ClearColorConfig, prelude::*};

use crate::state::InGameSaving;

pub fn setup_saving_screen(mut commands: Commands) {
    /*commands.spawn((
        Camera2dBundle{
            /*camera_2d: Camera2d{
                clear_color: ClearColorConfig::Custom(Color::BLACK)
            },*/
            camera: Camera {
                // renders after / on top of the main camera
                order: 1,
                ..default()
            },
            ..Default::default()
        },
        InGameSaving
    ));*/

    commands.spawn((
        TextBundle::from_section(
            "Saving...",
            TextStyle {
                //font: asset_server.load("fonts/FiraMono-Medium.ttf"),
                font_size: 28.0,
                color: Color::WHITE,
                ..Default::default()
            },
        )
        .with_style(Style {
            position_type: PositionType::Relative,
            top: Val::Percent(90.0),
            left: Val::Percent(80.0),
            ..default()
        }),
        InGameSaving,
    ));
}

pub fn teardown_saving_screen(
    in_main_menu: Query<Entity, With<InGameSaving>>,
    mut commands: Commands,
) {
    for entity in in_main_menu.iter() {
        commands.entity(entity).despawn_recursive();
    }
}
