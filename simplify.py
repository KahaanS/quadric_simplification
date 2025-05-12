from mesh.mesh import Mesh
import os
import argparse

def get_args():
    parser = argparse.ArgumentParser(description='Quadric Simplification')
    parser.add_argument('-i', '--input', type=str, required=True, help='Input file')
    parser.add_argument('-o', '--output', type=str, required=True, default='output', help='Output folder path')
    parser.add_argument('-r', '--ratio', type=float, default=0.5, help='Simplification factor (ignored by -t)')
    parser.add_argument('-t', '--target', type=int, help='Target vertex count')
    
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    
    args = get_args()
    filename = args.input.split('/')[-1].split('.')[0]
    mesh = Mesh(args.input)
    
    if args.target:
        target_vertex_count = args.target
    else:
        target_vertex_count = int(mesh.vertex_count * args.ratio)

    print(f"Target vertex count: {target_vertex_count}")
    mesh.simplify(target_vertex_count)
    
    output_path = os.path.join(args.output, filename+'_simplified.obj')
    
    mesh.export_obj(output_path)