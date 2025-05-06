from mesh.mesh import Mesh

if __name__ == "__main__":
    mesh = Mesh("samples/armchair.obj")
    print(f"Loaded mesh with {mesh.vertex_count} vertices, {mesh.face_count} faces and {mesh.edge_count} edges.")
    simplification_factor = 0.1
    target_vertex_count = int(mesh.vertex_count * simplification_factor)
    print(f"Target vertex count: {target_vertex_count}")
    mesh.simplify(target_vertex_count)
    mesh.export_obj("output/armchair_simplified.obj")
    
    # print(f"Vertices: {mesh.vertices[0].faces}")