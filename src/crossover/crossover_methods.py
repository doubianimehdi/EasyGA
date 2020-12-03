import random

def append_to_next_population(population_method):
    """Appends the new chromosomes to the next population.
    Also modifies the input to include the mating pool.
    """

    return lambda ga:\
        ga.population.append_children(
            population_method(ga, ga.population.mating_pool)
        )


def check_weight(individual_method):
    """Checks if the weight is between 0 and 1 before running.
    Exception may occur when using ga.adapt, which will catch
    the error and try again with valid weight.
    """

    def new_method(ga, parent_1, parent_2, weight):

        if 0 < weight < 1:
            return individual_method(ga, parent_1, parent_2, weight)
        else:
            raise ValueError("Weight must be between 0 and 1 when using the given crossover method.")

    return new_method


def genes_to_chromosome(individual_method):
    """Converts a collection of genes into a chromosome.
    Note: Will recreate the gene list if given gene list.
          Built-in methods do not construct gene lists
          and use yield for efficiency.
    """

    return lambda ga, parent_1, parent_2, weight:\
        ga.make_chromosome(
            individual_method(ga, parent_1, parent_2, weight)
        )


def values_to_genes(individual_method):
    """Converts a collection of values into genes.
    Returns a generator of genes to avoid storing a new list.
    """

    return lambda ga, parent_1, parent_2, weight:\
        (
            ga.make_gene(value)
            for value
            in individual_method(ga, parent_1, parent_2, weight)
        )


class Crossover_Methods:

    # Private method decorators, see above.
    _append_to_next_population = append_to_next_population
    _check_weight              = check_weight
    _genes_to_chromosome       = genes_to_chromosome
    _values_to_genes           = values_to_genes


    class Population:
        """Methods for selecting chromosomes to crossover."""


        @append_to_next_population
        def sequential_selection(ga, mating_pool):
            """Select sequential pairs from the mating pool.
            Every parent is paired with the previous parent.
            The first parent is paired with the last parent.
            """

            for index in range(len(mating_pool)):    # for each parent in the mating pool
                yield ga.crossover_individual_impl(  #     apply crossover to
                    ga,                              # 
                    mating_pool[index],              #         the parent and
                    mating_pool[index-1],            #         the previous parent
                    0.5                              #         with equal weight
                )


        @append_to_next_population
        def random_selection(ga, mating_pool):
            """Select random pairs from the mating pool.
            Every parent is paired with a random parent.
            """

            for parent in mating_pool:               # for each parent in the mating pool
                yield ga.crossover_individual_impl(  #     apply crossover to
                    ga,                              # 
                    parent,                          #         the parent and
                    random.choice(mating_pool),      #         a random parent
                    0.5                              #         with equal weight
                )


    class Individual:
        """Methods for crossing parents."""


        @check_weight
        @genes_to_chromosome
        def single_point(ga, parent_1, parent_2, weight = 0.5):
            """Cross two parents by swapping genes at one random point."""

            # Equally weighted indexes
            if weight == 0.5:
                swap_index = random.randrange(N)

            # Use weighted random index.
            else:
                n = min(len(parent_1), len(parent_2))
                t = 2*weight if (weight < 0.5) else 0.5 / (1-weight)
                x = random.random()
                swap_index = int(n * (1-(1-x)**t)**(1/t))

            # Randomly choose which parent's genes are selected first.
            if random.choice([True, False]):
                return parent_1[:swap_index] + parent_2[swap_index:]
            else:
                return parent_2[:-swap_index] + parent_1[-swap_index:]


        @check_weight
        @genes_to_chromosome
        def multi_point(ga, parent_1, parent_2, weight = 0.5):
            """Cross two parents by swapping genes at multiple points."""
            pass


        @check_weight
        @genes_to_chromosome
        def uniform(ga, parent_1, parent_2, weight = 0.5):
            """Cross two parents by swapping all genes randomly."""

            for gene_pair in zip(parent_1, parent_2):
                yield random.choice(gene_pair, cum_weights = [weight, 1])


        class Arithmetic:
            """Crossover methods for numerical genes."""

            @genes_to_chromosome
            @values_to_genes
            def average(ga, parent_1, parent_2, weight = 0.5):
                """Cross two parents by taking the average of the genes."""

                values_1 = parent_1.gene_value_iter
                values_2 = parent_2.gene_value_iter

                for value_1, value_2 in zip(values_1, values_2):

                    value = weight*value_1 + (1-weight)*value_2

                    if type(value_1) == type(value_2) == int:
                        value = round(value + random.uniform(-0.5, 0.5))

                    yield value


            @genes_to_chromosome
            @values_to_genes
            def extrapolate(ga, parent_1, parent_2, weight = 0.5):

                """Cross two parents by extrapolating towards the first parent.
                May result in gene values outside the expected domain.
                """

                values_1 = parent_1.gene_value_iter
                values_2 = parent_2.gene_value_iter

                for value_1, value_2 in zip(values_1, values_2):

                    value = (2-weight)*value_1 + (weight-1)*value_2

                    if type(value_1) == type(value_2) == int:
                        value = round(value + random.uniform(-0.5, 0.5))

                    yield value


            @check_weight
            @genes_to_chromosome
            @values_to_genes
            def random(ga, parent_1, parent_2, weight = 0.5):
                """Cross two parents by taking a random integer or float value between each of the genes."""

                values_1 = parent_1.gene_value_iter
                values_2 = parent_2.gene_value_iter

                for value_1, value_2 in zip(values_1, values_2):

                    # Use equally weighted values.
                    if weight == 0.5:
                        value = random.uniform(value_1, value_2)

                    # Use weighted random value, which gives values closer
                    # to value_1 if weight < 0.5 or values closer to value_2
                    # if weight > 0.5.
                    else:
                        t = 2*weight if (weight < 0.5) else 0.5 / (1-weight)
                        x = random.random()
                        value = value_1 + (value_2-value_1) * (1-(1-x)**t)**(1/t)

                    if type(value_1) == type(value_2) == int:
                        value = round(value + random.uniform(-0.5, 0.5))

                    yield value
