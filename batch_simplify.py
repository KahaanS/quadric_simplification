import os
import argparse
from tqdm import tqdm
from mesh.mesh import Mesh
import time

def get_args():
    parser = argparse.ArgumentParser(description='Quadric Simplification')
    parser.add_argument('-i', '--input', type=str, required=True, help='Input directory')
    parser.add_argument('-o', '--output', type=str, required=True, default='output', help='Output directory')
    
    args = parser.parse_args()
    return args

def simplify_mesh(input_path, output_path, target_ratio=0.5):
    start_time = time.time()
    mesh = Mesh(input_path)
    num_vertices = mesh.vertex_count
    target_vertex_count = int(mesh.vertex_count * target_ratio)  # Simplify to 50% of original vertices
    # print(f"Target vertex count: {target_vertex_count}")
    mesh.simplify(target_vertex_count)
    end_time = time.time()
    
    print(f"Simplification completed in {end_time - start_time:.2f} seconds.")
    
    mesh.export_obj(output_path)
    return end_time - start_time, num_vertices

if __name__ == "__main__":
    args = get_args()
    input_dir = args.input
    output_dir = args.output
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Get all .obj files in the input directory
    input_files = [f for f in os.listdir(input_dir) if f.endswith('.obj')]
    ratios = [0.2, 0.5, 0.8]
    
    log_file = os.path.join(output_dir, 'simplification_log.csv')
    with open(log_file, 'w') as log:
        log.write("Input File,Target Ratio,Time Taken (s),Original Vertex Count\n")
        for input_file in tqdm(input_files):
            input_path = os.path.join(input_dir, input_file)
            for ratio in ratios:
                output_path = os.path.join(output_dir, f"{os.path.splitext(input_file)[0]}_ratio_{ratio}.obj")
                try:
                    time_taken, num_vertices = simplify_mesh(input_path, output_path, target_ratio=ratio)
                except:
                    print(f"Error processing {input_file} with ratio {ratio}. Skipping...")
                    log.write(f"{input_file},{ratio},Error,0\n")
                    continue
                log.write(f"{input_file},{ratio},{time_taken:.4f},{num_vertices}\n")
                log.flush()
                
    print(f"All simplifications completed. Log saved to {log_file}.")