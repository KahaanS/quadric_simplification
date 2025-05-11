import os
import argparse
import pandas as pd
import trimesh
from trimesh.sample import sample_surface
import numpy as np
from tqdm import tqdm

def symmetric_surface_error(mesh_a: trimesh.Trimesh, mesh_b: trimesh.Trimesh, n_samples: int = 10000) -> float:
    # Sample points from the surface of both meshes
    samples_a, _ = trimesh.sample.sample_surface(mesh_a, n_samples)
    samples_b, _ = trimesh.sample.sample_surface(mesh_b, n_samples)

    # Build proximity queries
    prox_b = trimesh.proximity.ProximityQuery(mesh_b)
    prox_a = trimesh.proximity.ProximityQuery(mesh_a)

    # Compute shortest surface distances
    dists_a_to_b = prox_b.on_surface(samples_a)[1]
    dists_b_to_a = prox_a.on_surface(samples_b)[1]

    mse = (np.sum(dists_a_to_b**2) + np.sum(dists_b_to_a**2)) / (2 * n_samples)
    return mse

def main(input_dir, output_dir):
    csv_path = os.path.join(output_dir, "simplification_log.csv")
    df = pd.read_csv(csv_path)

    errors = []

    for _, row in tqdm(df.iterrows(), total=len(df), desc="Evaluating errors"):
        input_filename = row["Input File"]
        target_ratio = row["Target Ratio"]

        input_path = os.path.join(input_dir, input_filename)
        base_name = os.path.splitext(os.path.basename(input_filename))[0]
        output_filename = f"{base_name}_ratio_{target_ratio}.obj"
        output_path = os.path.join(output_dir, output_filename)

        if not os.path.exists(input_path) or not os.path.exists(output_path):
            errors.append(np.nan)
            continue

        try:
            mesh_input = trimesh.load_mesh(input_path, force='mesh')
            mesh_output = trimesh.load_mesh(output_path, force='mesh')
            err = symmetric_surface_error(mesh_input, mesh_output)
            errors.append(err)
        except Exception as e:
            print(f"Error processing {input_filename}: {e}")
            errors.append(np.nan)

    df["error"] = errors
    df.to_csv(csv_path, index=False)
    print(f"Updated CSV with error column written to {csv_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate symmetric surface error for simplified meshes.")
    parser.add_argument("-i","--input_dir", type=str, required=True, help="Path to the input OBJ files")
    parser.add_argument("-o","--output_dir", type=str, required=True, help="Path to the output simplified files and log CSV")

    args = parser.parse_args()
    main(args.input_dir, args.output_dir)
