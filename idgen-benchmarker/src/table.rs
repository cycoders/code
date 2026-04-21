use comfy_table::{
    modifiers::UTF8_ROUND_BORDERS,
    presets::UTF8_FULL_CONDENSED,
    *,
};

pub fn print_speed_table(results: Vec<(String, f64, f64, usize)>) {
    let mut table = Table::new();
    table.load_preset(UTF8_FULL_CONDENSED);
    table.apply_modifier(UTF8_ROUND_BORDERS);

    table.set_header(vec![
        Cell::new("Generator"),
        Cell::new("Time (s)"),
        Cell::new("IDs/sec"),
        Cell::new("Avg Len"),
    ]);

    for (name, time, ips, len) in results {
        table.add_row(vec![
            Cell::new(&name),
            Cell::new(&format!("{:.3}", time)),
            Cell::new(&format!("{:.1e}", ips)),
            Cell::new(&len.to_string()),
        ]);
    }

    println!("{table}");
}

pub fn print_mono_table(results: Vec<(String, f64)>) {
    let mut table = Table::new();
    table.load_preset(UTF8_FULL_CONDENSED);
    table.apply_modifier(UTF8_ROUND_BORDERS);

    table.set_header(vec![Cell::new("Generator"), Cell::new("Monotonicity %")]);

    for (name, pct) in results {
        table.add_row(vec![
            Cell::new(&name),
            Cell::new(&format!("{:.1}", pct)),
        ]);
    }

    println!("{table}");
}

pub fn print_collision_table(results: Vec<(String, usize, f64, f64)>) {
    let mut table = Table::new();
    table.load_preset(UTF8_FULL_CONDENSED);
    table.apply_modifier(UTF8_ROUND_BORDERS);

    table.set_header(vec![
        Cell::new("Generator"),
        Cell::new("Collisions"),
        Cell::new("Sim %"),
        Cell::new("Est % @1e9"),
    ]);

    for (name, colls, sim_pct, est_pct) in results {
        table.add_row(vec![
            Cell::new(&name),
            Cell::new(&colls.to_string()),
            Cell::new(&format!("{:.4}", sim_pct)),
            Cell::new(&format!("{:.2e}", est_pct)),
        ]);
    }

    println!("{table}");
}
