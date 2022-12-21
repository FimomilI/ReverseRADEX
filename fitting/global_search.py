from pyswarms.backend.topology import Pyramid
from pyswarms.single.general_optimizer import GeneralOptimizerPSO


def global_search(RADEX_model, dims, bounds):
    # Set-up hyperparameters and topology
    options = {'c1': 0.5, 'c2': 0.3, 'w': 0.9}
    topology = Pyramid(static=False)

    # Call instance of GlobalBestPSO
    optimizer = GeneralOptimizerPSO(
        n_particles=25, dimensions=dims, options=options, topology=topology
    )
    
    # define RADEX model function suitable for optimization
    def RADEX_optimize(x):
        return RADEX_model()

    # Perform optimization
    stats = optimizer.optimize(RADEX_optimize, iters=100)
    
    return stats
