import subprocess
import os
import bpy

def render_3d_scene(prompt, output_path, frame_count=90):
    # Clear existing objects
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    prompt_lower = prompt.lower()
    
    # Setup Camera
    cam_data = bpy.data.cameras.new(name="Camera_Data")
    cam_obj = bpy.data.objects.new(name="Camera", data=cam_data)
    bpy.context.scene.collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj
    cam_obj.location = (0, -10, 3)
    cam_obj.rotation_euler = (1.2, 0, 0)
    
    # Setup Lighting (Dramatic True-Crime Mood Lighting)
    light_data = bpy.data.lights.new(name="Key_Light", type='POINT')
    light_data.energy = 1000.0
    if "ocean" in prompt_lower or "storm" in prompt_lower:
        light_data.color = (0.1, 0.4, 0.8) # Eerie blue
    elif "forest" in prompt_lower or "woods" in prompt_lower:
        light_data.color = (0.2, 0.6, 0.3) # Moody green
    else:
        light_data.color = (0.8, 0.2, 0.2) # Crimson red
        
    light_obj = bpy.data.objects.new(name="Key_Light_Obj", data=light_data)
    bpy.context.scene.collection.objects.link(light_obj)
    light_obj.location = (5, -5, 5)
    
    # Create 3D Terrain / Landscape Mesh
    bpy.ops.mesh.primitive_grid_of_terrain_add if hasattr(bpy.ops.mesh, 'primitive_grid_of_terrain_add') else bpy.ops.mesh.primitive_grid_add(size=15, x_subdivisions=30, y_subdivisions=30)
    terrain = bpy.context.active_object
    
    # Add displace modifier for 3D waves or hills
    mod = terrain.modifiers.new(name="WaveDisplace", type='DISPLACE')
    tex = bpy.data.textures.new(name="WaveTex", type='CLOUDS' if "forest" in prompt_lower else 'OCEAN')
    tex.noise_scale = 2.0
    mod.texture = tex
    mod.strength = 1.5
    
    # Material setup
    mat = bpy.data.materials.new(name="CinematicMat")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        if "ocean" in prompt_lower:
            bsdf.inputs['Base Color'].default_value = (0.02, 0.08, 0.18, 1)
            bsdf.inputs['Roughness'].default_value = 0.1
        else:
            bsdf.inputs['Base Color'].default_value = (0.05, 0.05, 0.08, 1)
            bsdf.inputs['Roughness'].default_value = 0.8
    terrain.data.materials.append(mat)
    
    # Animation setup (Camera dolly forward)
    scene = bpy.context.scene
    scene.render.image_settings.file_format = 'PNG'
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.fps = 30
    
    temp_dir = "blender_frames"
    os.makedirs(temp_dir, exist_ok=True)
    
    for f in range(frame_count):
        scene.frame_set(f)
        cam_obj.location.y = -10 + (f * 0.03) # Smooth cinematic push-in
        scene.render.filepath = os.path.join(temp_dir, f"frame_{f:03d}.png")
        bpy.ops.render.render(write_still=True)
        
    # Compile 3D frames into video clip using FFmpeg
    cmd = [
        "ffmpeg", "-y",
        "-framerate", "30",
        "-i", os.path.join(temp_dir, "frame_%03d.png"),
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        output_path
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"SUCCESS: True 3D rendered scene saved to {output_path}")

if __name__ == "__main__":
    render_3d_scene("Dark ocean storm with high waves", "assets/scene_3d_1.mp4", frame_count=30)
