mod benchmark;
mod generators;
mod table;

use benchmark::{collision_bench, mono_bench, speed_bench};
use clap::{Parser, Subcommand};
use generators::{IdGenerator, KsuidGen, NanoIdGen, UlidGen, UuidGen};
use std::thread;

type Result<T> = std::io::Result<T>;

#[derive(Parser)]
#[command(name = "idgen-benchmarker", about = "Benchmark ID generators for distributed systems")]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Benchmark generation speed and size
    Speed(SpeedArgs),
    /// Benchmark monotonicity under concurrency
    Mono(MonoArgs),
    /// Benchmark collisions (sim + theoretical)
    Collision(CollisionArgs),
}

#[derive(clap::Args)]
struct SpeedArgs {
    #[arg(long, default_value_t = 1_000_000u64)]
    count: u64,

    #[arg(long)]
    threads: Option<u32>,
}

#[derive(clap::Args)]
struct MonoArgs {
    #[arg(long, default_value_t = 1_000_000u64)]
    count: u64,

    #[arg(long)]
    threads: Option<u32>,
}

#[derive(clap::Args)]
struct CollisionArgs {
    #[arg(long, default_value_t = 1_000_000u64)]
    sim_count: u64,

    #[arg(long, default_value_t = 1_000_000_000u64)]
    est_count: u64,
}

fn main() -> Result<()> {
    let cli = Cli::parse();

    let gens: Vec<Box<dyn IdGenerator>> = vec![
        Box::new(UuidGen),
        Box::new(UlidGen),
        Box::new(KsuidGen),
        Box::new(NanoIdGen::default()),
    ];

    match cli.command {
        Commands::Speed(args) => {
            let threads = args.threads.unwrap_or_else(|| {
                thread::available_parallelism()
                    .map_or(1u32, |p| p.get() as u32)
            });
            println!("Benchmarking speed: {} IDs, {} threads", args.count, threads);
            let results = speed_bench(&gens, args.count, threads);
            table::print_speed_table(results);
        }
        Commands::Mono(args) => {
            let threads = args.threads.unwrap_or_else(|| {
                thread::available_parallelism()
                    .map_or(1u32, |p| p.get() as u32)
            });
            println!("Benchmarking monotonicity: {} IDs, {} threads", args.count, threads);
            let results = mono_bench(&gens, args.count, threads);
            table::print_mono_table(results);
        }
        Commands::Collision(args) => {
            println!(
                "Benchmarking collisions: sim={} IDs, est={} IDs",
                args.sim_count, args.est_count
            );
            let results = collision_bench(&gens, args.sim_count, args.est_count);
            table::print_collision_table(results);
        }
    }

    Ok(())
}
