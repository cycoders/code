import argparse
import math
import random


def create_cities(n):
    return [[random.randint(0, 50), random.randint(0, 50)] for _ in range(n)]


def calc_distance(c1, c2):
    dx = c1[0] - c2[0]
    dy = c1[1] - c2[1]
    return math.sqrt(dx * dx + dy * dy)


def create_distance_matrix(cities):
    n = len(cities)
    dists = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            dists[i][j] = calc_distance(cities[i], cities[j])
    return dists


def total_distance(perm, dists):
    n = len(perm)
    td = 0.0
    for i in range(n):
        td += dists[perm[i]][perm[(i + 1) % n]]
    return td


def fitness(perm, dists):
    return 1.0 / (total_distance(perm, dists) + 1e-10)


def create_individual(n):
    ind = list(range(n))
    random.shuffle(ind)
    return ind


def tournament_selection(pop, fits, k):
    candidates = random.sample(range(len(pop)), k)
    best_idx = max(candidates, key=lambda i: fits[i])
    return pop[best_idx][:]


def order_crossover(p1, p2):
    size = len(p1)
    start, end = sorted(random.sample(range(size), 2))
    child = [-1] * size
    child[start:end] = p1[start:end]
    remaining = [p2[i] for i in range(size) if p2[i] not in p1[start:end]]
    j = 0
    for i in range(size):
        if child[i] == -1:
            child[i] = remaining[j]
            j += 1
    return child


def mutate(ind, rate):
    if random.random() < rate:
        i = random.randrange(len(ind))
        j = random.randrange(len(ind))
        if i != j:
            ind[i], ind[j] = ind[j], ind[i]
    return ind


def visualize(cities, best_perm, grid_size=25):
    n = len(cities)
    if n == 0:
        return
    xs = [c[0] for c in cities]
    ys = [c[1] for c in cities]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    if max_x == min_x:
        max_x += 1
    if max_y == min_y:
        max_y += 1
    w, h = grid_size, grid_size
    grid = [['.' for _ in range(w)] for _ in range(h)]
    labels = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    for tour_pos, city_idx in enumerate(best_perm):
        c = cities[city_idx]
        col = int((c[0] - min_x) / (max_x - min_x) * (w - 1))
        row = int((c[1] - min_y) / (max_y - min_y) * (h - 1))
        grid[row][col] = labels[tour_pos % len(labels)]
    print('\nASCII Grid (tour order A/B/0/...):')
    for row in grid:
        print(''.join(row))
    print()


def main():
    parser = argparse.ArgumentParser(description='Genetic Algorithm TSP Solver')
    parser.add_argument('--num-cities', type=int, default=12, help='Number of cities')
    parser.add_argument('--pop-size', type=int, default=200, help='Population size')
    parser.add_argument('--generations', type=int, default=1000, help='Generations')
    parser.add_argument('--mutation-rate', type=float, default=0.05, help='Mutation rate')
    parser.add_argument('--tournament-size', type=int, default=3, help='Tournament size')
    args = parser.parse_args()

    random.seed(42)  # Reproducible

    n_cities = args.num_cities
    cities = create_cities(n_cities)
    dists = create_distance_matrix(cities)

    pop_size = args.pop_size
    pop = [create_individual(n_cities) for _ in range(pop_size)]

    print(f'Starting GA: {n_cities} cities, pop={pop_size}, gens={args.generations}')

    for gen in range(args.generations):
        fits = [fitness(ind, dists) for ind in pop]
        elite = tournament_selection(pop, fits, args.tournament_size)
        new_pop = [elite]
        for _ in range((pop_size - 1) // 2):
            p1 = tournament_selection(pop, fits, args.tournament_size)
            p2 = tournament_selection(pop, fits, args.tournament_size)
            c1 = order_crossover(p1, p2)
            c2 = order_crossover(p2, p1)
            mutate(c1, args.mutation_rate)
            mutate(c2, args.mutation_rate)
            new_pop += [c1, c2]
        if len(new_pop) > pop_size:
            new_pop.pop()
        pop = new_pop
        if gen % 100 == 99:
            best_fit = max(fits)
            print(f'Gen {gen+1}: best fitness {best_fit:.4f}')

    # Final best
    fits = [fitness(ind, dists) for ind in pop]
    best_idx = max(range(len(pop)), key=lambda i: fits[i])
    best_perm = pop[best_idx]
    best_dist = total_distance(best_perm, dists)

    print(f'\nBest distance: {best_dist:.2f}')
    print('Best path:', best_perm)
    print('\nCity positions:')
    for i, c in enumerate(cities):
        print(f'{i}: {c}')
    visualize(cities, best_perm)


if __name__ == '__main__':
    main()
