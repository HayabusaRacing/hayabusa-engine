from geometry.rayBundle import RayBundle
from geometry.geometryParams import GeometryParams
from foam.setupCase import setup_case
from foam.runner import OpenFOAMParallelRunner
from foam.extractCD import extract_latest_cd
from config import BASE_DIR, CASE_DIR, TMP_DIR, MESH_WIDTH, MESH_HEIGHT, MESH_DEPTH, MESH_DENSITY, MESH_CENTER, MESH_UNIT

import trimesh
from pathlib import Path

def evaluate(params: GeometryParams) -> float:
    setup_case(base_dir=BASE_DIR, case_dir=CASE_DIR)
    
    bundle = RayBundle(width=MESH_WIDTH, height=MESH_HEIGHT, depth=MESH_DEPTH, density=MESH_DENSITY, center=MESH_CENTER, unit=MESH_UNIT)
    bundle.set_ts(params.ts)
    bundle.export_stl(TMP_DIR / "wing.stl")
    mesh_wing = trimesh.load(TMP_DIR / "wing.stl")
    mesh_body = trimesh.load(BASE_DIR / "constant" / "triSurface" / "mainBodyNoWing.stl")
    combined = trimesh.util.concatenate([mesh_body, mesh_wing])
    combined.export(CASE_DIR / "constant" / "triSurface" / "mainBody.stl")
    
    runner = OpenFOAMParallelRunner(case_dir=CASE_DIR, n_proc=6)
    runner.run_all()
    
    result = extract_latest_cd()
    cd = result["Cd"]
    
    params.fitness = cd
    
    return cd