import numpy as np

def breakup_smpl_space(sim_time, tle_time):
    '''
    This function receive the samplinzg space (a vector of time containing all the instances when we want to
    simulate the orbit) as well as the selected TLEs which are the references for orbit propagation. The idea is to
    locate instances
    of time in the sampling space, where we need to update the reference TLE.
    '''

    idx_tle = []
    idx_sim = []
    idx_redundant = []

    # Find corresponding indices of tle and simulation time vectors
    for i in range(len(tle_time)):
        idx_tle.append(i)
        idx_sim.append(np.argmax(sim_time > tle_time[i]))

    # Find redundant tle time references
    idx_sim_unique = np.unique(idx_sim)
    for j in range(len(idx_sim_unique)):
        idx = idx_sim == idx_sim_unique[j]
        if sum(idx) > 1:
            loc = [i for i, val in enumerate(idx) if val]
            for k in range(len(loc) - 1):
                idx_redundant.append(loc[k])

    # Delete redundant tle time references
    idx_redundant.reverse()
    for i in idx_redundant:
        del idx_tle[i]
        del idx_sim[i]

    return(idx_sim, idx_tle)





