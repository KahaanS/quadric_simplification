import numpy as np
import trimesh

def symmetric_surface_error(mesh_a: trimesh.Trimesh, mesh_b: trimesh.Trimesh, n_samples: int = 10000) -> float:
    # Sample points from the surface of both meshes
    samples_a, _, _ = trimesh.sample.sample_surface(mesh_a, n_samples)
    samples_b, _, _ = trimesh.sample.sample_surface(mesh_b, n_samples)

    # Build proximity queries
    prox_b = trimesh.proximity.ProximityQuery(mesh_b)
    prox_a = trimesh.proximity.ProximityQuery(mesh_a)

    # Compute shortest surface distances
    dists_a_to_b = prox_b.on_surface(samples_a)[1]
    dists_b_to_a = prox_a.on_surface(samples_b)[1]

    # Mean squared error
    mse = (np.sum(dists_a_to_b**2) + np.sum(dists_b_to_a**2)) / (2 * n_samples)
    return mse

def evaluate_mesh_difference(original_path: str, simplified_path: str, n_samples: int = 10000):

    mesh_original = trimesh.load_mesh(original_path, process=True)
    mesh_simplified = trimesh.load_mesh(simplified_path, process=True)

    error = symmetric_surface_error(mesh_original, mesh_simplified, n_samples)
    
    return error