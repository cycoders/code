use crate::generators::IdGenerator;
use rayon::prelude::*;
use std::collections::HashSet;
use std::time::Instant;

pub fn speed_bench(
    gens: &[Box<dyn IdGenerator>],
    count: u64,
    threads: u32,
) -> Vec<(String, f64, f64, usize)> {
    gens.iter()
        .map(|gen| {
            let res = single_speed_bench(gen.as_ref(), count, threads);
            (
                gen.name().to_string(),
                res.0,
                count as f64 / res.0,
                res.1,
            )
        })
        .collect()
}

fn single_speed_bench(gen: &dyn IdGenerator, count: u64, threads: u32) -> (f64, usize) {
    let chunk_size = count.saturating_div(threads.max(1));
    let num_chunks = threads as usize;

    let start = Instant::now();

    let ids: Vec<String> = (0..num_chunks)
        .into_par_iter()
        .flat_map(|_| {
            let mut chunk = Vec::with_capacity(chunk_size as _);
            for _ in 0..chunk_size {
                chunk.push(gen.generate());
            }
            chunk
        })
        .collect();

    let elapsed = start.elapsed().as_secs_f64();

    let avg_len = if ids.is_empty() {
        0
    } else {
        ids.iter().map(|s| s.len()).sum::<usize>() / ids.len()
    };

    (elapsed, avg_len)
}

pub fn mono_bench(
    gens: &[Box<dyn IdGenerator>],
    count: u64,
    threads: u32,
) -> Vec<(String, f64)> {
    gens.iter()
        .map(|gen| {
            let mono_pct = single_mono_bench(gen.as_ref(), count, threads);
            (gen.name().to_string(), mono_pct)
        })
        .collect()
}

fn single_mono_bench(gen: &dyn IdGenerator, count: u64, threads: u32) -> f64 {
    let chunk_size = count.saturating_div(threads.max(1));
    let num_chunks = threads as usize;

    let mut ids: Vec<String> = (0..num_chunks)
        .into_par_iter()
        .flat_map(|_| {
            let mut chunk = Vec::with_capacity(chunk_size as _);
            for _ in 0..chunk_size {
                chunk.push(gen.generate());
            }
            chunk
        })
        .collect();

    if ids.len() < 2 {
        return 100.0;
    }

    ids.sort_unstable();

    let mut increasing = 0u64;
    for i in 1..ids.len() {
        if ids[i] > ids[i - 1] {
            increasing += 1;
        }
    }

    (increasing as f64 / (ids.len() as f64 - 1.0)) * 100.0
}

pub fn collision_bench(
    gens: &[Box<dyn IdGenerator>],
    sim_count: u64,
    est_count: u64,
) -> Vec<(String, usize, f64, f64)> {
    gens.iter()
        .map(|gen| {
            let (colls, sim_pct) = single_collision_bench(gen.as_ref(), sim_count);
            let est_prob = crate::generators::theoretical_prob(est_count, gen.bits()) * 100.0;
            (
                gen.name().to_string(),
                colls,
                sim_pct,
                est_prob,
            )
        })
        .collect()
}

fn single_collision_bench(gen: &dyn IdGenerator, count: u64) -> (usize, f64) {
    let mut set = HashSet::with_capacity(count as usize);
    let mut collisions = 0;

    for _ in 0..count {
        let id = gen.generate();
        if !set.insert(id) {
            collisions += 1;
        }
    }

    let sim_pct = if count > 0 {
        (collisions as f64 / count as f64) * 100.0
    } else {
        0.0
    };

    (collisions, sim_pct)
}
