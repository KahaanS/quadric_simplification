import numpy as np
from tqdm import tqdm
from typing import List, Set
import heapq

from mesh.vertex import Vertex
from mesh.face import Face
from mesh.edge import Edge

class Mesh:
    def __init__(self, file_path):
        self.file_path = file_path

        # Load the mesh from the file
        with open(self.file_path, 'r') as f:
            lines = f.readlines()

        self.vertices: List[Vertex] = []
        self.faces: List[Face] = []
        self.edges: List[Edge] = []  # Changed from set to list
        self.edge_lookup = dict()    # Still used for deduplication

        print(f"Loading mesh from {self.file_path}...")
        for line in tqdm(lines):
            split_line = line.split()

            if len(split_line) == 0:
                continue

            if split_line[0] == 'v':
                # Add new vertex
                new_vert = Vertex(len(self.vertices), [float(coord) for coord in split_line[1:]])
                self.vertices.append(new_vert)

            elif split_line[0] == 'f':
                assert len(split_line) == 4, "Only triangle meshes are supported"
                face_verts = [int(idx.split('/')[0]) - 1 for idx in split_line[1:]]
                face_vertices = [self.vertices[i] for i in face_verts]
                new_face = Face(len(self.faces), face_vertices)
                self.faces.append(new_face)

                # Register face with vertices
                for vertex in face_vertices:
                    vertex.add_face(new_face)

                # Create or retrieve edges
                for i in range(3):
                    v1 = face_vertices[i]
                    v2 = face_vertices[(i + 1) % 3]
                    edge_key = frozenset((v1.index, v2.index))

                    if edge_key in self.edge_lookup:
                        edge = self.edge_lookup[edge_key]
                    else:
                        edge = Edge(v1, v2)
                        self.edges.append(edge)
                        self.edge_lookup[edge_key] = edge
                        v1.add_edge(edge)
                        v2.add_edge(edge)

                    # Link edge and face
                    edge.add_face(new_face)
                    new_face.add_edge(edge)

        self.vertex_count = len(self.vertices)
        self.face_count = len(self.faces)
        self.edge_count = len(self.edges)
        
    def simplify(self, target_vertex_count: int):
        print("Computing initial quadrics for vertices...")
        for vertex in tqdm(self.vertices):
            vertex.compute_quadric()
         
        self.active_vertex_count = sum(1 for v in self.vertices if v.mask)
        
        # Priority queue of edges sorted by error
        edge_heap = []
        for edge in self.edges:
            if edge.mask:
                edge.compute_error()
                heapq.heappush(edge_heap, (edge.error, edge))
        
        pbar = tqdm(total=self.active_vertex_count - target_vertex_count, desc="Simplifying mesh")
        while self.active_vertex_count > target_vertex_count and edge_heap:
            _, edge = heapq.heappop(edge_heap)

            if not edge.mask:
                continue

            v1, v2 = edge.vertices
            if not v1.mask or not v2.mask:
                continue
            
            # Create new vertex at optimal location
            new_pos = edge.optimal_point
            new_vertex = Vertex(len(self.vertices), new_pos)
            new_vertex.quadric = v1.quadric + v2.quadric
            new_vertex.mask = True
            self.vertices.append(new_vertex)

            # Mark old vertices and edge as removed
            v1.mask = False
            v2.mask = False
            edge.mask = False
            self.active_vertex_count -= 1

            # Mark shared faces as degenerate
            shared_faces = set(v1.faces) & set(v2.faces)
            for face in shared_faces:
                face.mask = False

            # Update remaining faces
            affected_faces = (set(v1.faces) | set(v2.faces)) - shared_faces
            for face in affected_faces:
                if not face.mask:
                    continue

                # Replace v1/v2 with new_vertex
                face.vertices = [new_vertex if v in (v1, v2) else v for v in face.vertices]
                face.normal = face.compute_normal()
                face.centre = face.compute_centre()
                new_vertex.add_face(face)

            # Update edges
            adjacent_edges = set(v1.edges + v2.edges)
            for old_edge in adjacent_edges:
                if not old_edge.mask:
                    continue

                ov1, ov2 = old_edge.vertices
                if ov1 in (v1, v2):
                    ov1 = new_vertex
                if ov2 in (v1, v2):
                    ov2 = new_vertex

                if ov1 == ov2:
                    old_edge.mask = False
                    continue

                edge_key = frozenset((ov1.index, ov2.index))
                if edge_key in self.edge_lookup:
                    existing_edge = self.edge_lookup[edge_key]
                    if existing_edge.mask:
                        continue

                # Create new or updated edge
                new_edge = Edge(ov1, ov2)
                for face in old_edge.faces:
                    if face.mask:
                        new_edge.add_face(face)
                new_edge.compute_error()
                self.edges.append(new_edge)
                self.edge_lookup[edge_key] = new_edge
                ov1.add_edge(new_edge)
                ov2.add_edge(new_edge)
                heapq.heappush(edge_heap, (new_edge.error, new_edge))

            pbar.update(1)

        pbar.close()
        
        # Finalize the mesh
        self.finalize_mesh()
        print("Mesh simplification completed.")
        
    def finalize_mesh(self):
        # Keep only valid vertices
        old_vertices = [v for v in self.vertices if v.mask]
        index_map = {v.index: i for i, v in enumerate(old_vertices)}
        
        for i, v in enumerate(old_vertices):
            v.index = i
        self.vertices = old_vertices

        # Keep only valid faces and update indices
        old_faces = [f for f in self.faces if f.mask]
        for i, f in enumerate(old_faces):
            f.index = i
        self.faces = old_faces

        # Keep only valid edges
        self.edges = [e for e in self.edges if e.mask]

        # Update counts
        self.vertex_count = len(self.vertices)
        self.face_count = len(self.faces)
        self.edge_count = len(self.edges)

        print("Mesh finalized.")
        print(f"Vertices: {self.vertex_count}, Faces: {self.face_count}, Edges: {self.edge_count}")

    def export_obj(self, output_path: str):
        with open(output_path, 'w') as f:
            # Write vertices
            for v in self.vertices:
                x, y, z = v.position
                f.write(f"v {x} {y} {z}\n")
            
            # Write faces (1-based indexing for .obj format)
            for face in self.faces:
                idxs = [v.index + 1 for v in face.vertices]
                f.write(f"f {idxs[0]} {idxs[1]} {idxs[2]}\n")

        print(f"Mesh exported to {output_path}")