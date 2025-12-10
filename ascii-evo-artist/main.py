#!/usr/bin/env python3

import argparse
import os
import random
import sys

def density(c):
    densities = {' ': 0, '.': 1, ',': 2, ':': 3, '-': 4, '=': 5, '+': 6, '*': 7, '#': 8, '%': 9, '@': 10}
    return densities.get(c, 5)

def fitness(individual, dens_target):
    return -sum(abs(density(individual[i]) - dens_target[i]) for i in range(len(individual)))

def create_individual(length, charset):
    return ''.join(random.choice(charset) for _ in range(length))

def render(flat, width):
    return '\n'.join([flat[i:i + width] for i in range(0, len(flat), width)])

def tournament_selection(scored_pop, tourn_size):
    tournament = random.sample(scored_pop, tourn_size)
    return max(tournament)

def crossover(p1, p2):
    point = random.randint(1, len(p1) - 1)
    return p1[:point] + p2[point:]

def mutate(ind, charset, rate):
    ind_list = list(ind)
    for i in range(len(ind_list)):
        if random.random() < rate:
            ind_list[i] = random.choice(charset)
    return ''.join(ind_list)

def get_default_target():
    return [
        "   ^   ",
        "  ^^^  ",
        " ^^^^^ ",
        "^^^^^^^",
        "  |||  ",
        "   |   "
    ]

def main():
    parser = argparse.ArgumentParser(description="Evolve ASCII art with genetic algorithms.")
    parser.add_argument('--generations', '-g', type=int, default=200)
    parser.add_argument('--population-size', '-p', type=int, default=50)
    parser.add_argument('--mutation-rate', '-m', type=float, default=0.01)
    parser.add_argument('--tournament-size', '-t', type=int, default=3)
    parser.add_argument('--elite-size', '-e', type=int, default=2)
    parser.add_argument('--target-file', type=str, default=None)
    parser.add_argument('--output-file', type=str, default='output/best.txt')
    parser.add_argument('--seed', type=int, default=42)
    args = parser.parse_args()

    random.seed(args.seed)

    charset = list(' .,:=-+*#%@')

    if args.target_file:
        try:
            with open(args.target_file, 'r') as f:
                raw_lines = f.readlines()
        except FileNotFoundError:
            sys.exit(f"Target file '{args.target_file}' not found.")
        target_lines = [line.rstrip('\n\r').rstrip() for line in raw_lines if line.strip()]
    else:
        target_lines = get_default_target()

    if not target_lines:
        sys.exit("No valid target lines found.")

    width = max(len(line) for line in target_lines)
    target_lines = [line.ljust(width) for line in target_lines]
    height = len(target_lines)
    length = width * height
    target_flat = ''.join(target_lines)
    dens_target = [density(c) for c in target_flat]

    print(f"Evolving {width}×{height} ({length} chars) ASCII art.")
    print("Target:")
    print(render(target_flat, width))
    print()

    pop = [create_individual(length, charset) for _ in range(args.population_size)]

    for gen in range(args.generations):
        scored_pop = [(fitness(ind, dens_target), ind) for ind in pop]
        scored_pop.sort(reverse=True)  # Best first (higher/less negative fitness)

        if gen % 20 == 0 or gen == args.generations - 1:
            best_score, best_ind = scored_pop[0]
            print(f"Gen {gen:4d}: fitness {best_score:6.0f}")
            print(render(best_ind, width))
            print()

        # Elitism
        new_pop = [ind for _, ind in scored_pop[:args.elite_size]]

        # Fill rest
        while len(new_pop) < args.population_size:
            _, parent1 = tournament_selection(scored_pop, args.tournament_size)
            _, parent2 = tournament_selection(scored_pop, args.tournament_size)
            child = crossover(parent1, parent2)
            child = mutate(child, charset, args.mutation_rate)
            new_pop.append(child)

        pop = new_pop

    # Final best
    final_scored = [(fitness(ind, dens_target), ind) for ind in pop]
    final_scored.sort(reverse=True)
    best_score, best_ind = final_scored[0]
    print("Final best (fitness {}):".format(best_score))
    print(render(best_ind, width))

    if args.output_file:
        output_dir = os.path.dirname(args.output_file)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        with open(args.output_file, 'w') as f:
            f.write(render(best_ind, width))
        print(f"\nSaved to '{args.output_file}'")

if __name__ == '__main__':
    main()
