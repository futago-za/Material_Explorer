bl_info = {
    "name": "Material Register",
    "author": "futagoza",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Sidebar",
    "description": "You can register materials and check them in 'Material Explorer'.",
    "warning": "",
    "doc_url": "",
    "category": "System",
}


import bpy
import math
import sqlite3
import pathlib
import os


APP_DATA_DIR = os.getenv('APPDATA')
APP_DIR = 'io.github.futagoza'
PACKAGE_NAME = 'material_explorer'
DB_FILE_NAME = 'material_explorer.db'
DB_TABLE_NAME = 'materials'
render_width = 1024
render_height = render_width

light_settings_type_1 = {'name': 'Light', 'location': (9.468799591064453, -9.112090110778809, 12.416399955749512), 'rotation': (1.1463932991027832, -0.4873465299606323, 0.5022865533828735), 'color': (1.0, 1.0, 1.0), 'energy': 5000.0, 'shape': 'DISK', 'size': 1, 'light_type' : 'AREA'},

light_settings_type_2 = [
    {'name': 'Key', 'location': (0.9657024145126343, 0.1987489014863968, 3.531301975250244), 'rotation': (0.7387110590934753, 0.13355399668216705, 1.265924334526062), 'color': (1.0, 1.0, 1.0), 'energy': 2.0, 'angle': 0.8447392582893372, 'light_type' : 'SUN'},
    {'name': 'Fill', 'location': (-0.18434572219848633, -1.599135398864746, 0.00036787986755371094), 'rotation': (1.1087428331375122, -1.19998037815094, 0.07287800312042236), 'color': (1.0, 0.8161362409591675, 0.6763365268707275), 'energy': 0.5, 'angle': 0.8726646304130554, 'light_type' : 'SUN'},
    {'name': 'Rim1', 'location': (-1.8414123058319092, 0.07446098327636719, 2.259891986846924), 'rotation': (3.0492851734161377, 1.1038767099380493, 5.421637058258057), 'color': (0.5765019655227661, 0.8108153343200684, 1.0), 'energy': 1.0, 'angle': 1.0629054307937622, 'light_type' : 'SUN'},
    {'name': 'Rim1.001', 'location': (-1.8414123058319092, 0.07446098327636719, 2.259891986846924), 'rotation': (1.085191011428833, 0.6000913977622986, 3.7065510749816895), 'color': (0.5765019655227661, 0.8108153343200684, 1.0), 'energy': 1.0, 'angle': 1.0629054307937622, 'light_type' : 'SUN'},
    {'name': 'Rim1.002', 'location': (-1.8414123058319092, 0.07446098327636719, 2.259891986846924), 'rotation': (1.552290678024292, 1.0451942682266235, 4.205862045288086), 'color': (0.5765019655227661, 0.8108153343200684, 1.0), 'energy': 1.0, 'angle': 1.0629054307937622, 'light_type' : 'SUN'},
    {'name': 'Key Sharp', 'location': (1.331888198852539, 0.036751747131347656, 3.3217601776123047), 'rotation': (0.7387110590934753, 0.13355399668216705, 1.265924334526062), 'color': (1.0, 1.0, 1.0), 'energy': 2.0, 'angle': 0.0872664600610733, 'light_type' : 'SUN'},
    {'name': 'Kick', 'location': (-0.18434572219848633, -1.599135398864746, 0.00036787986755371094), 'rotation': (4.107366561889648, -0.4839188754558563, -0.06675608456134796), 'color': (1.0, 0.8161362409591675, 0.6763365268707275), 'energy': 0.25, 'angle': 0.8726646304130554, 'light_type' : 'SUN'},
    {'name': 'Key Kick', 'location': (0.9657024145126343, 0.1987489014863968, 3.531301975250244), 'rotation': (0.7979456186294556, 0.9289038777351379, 2.002682685852051), 'color': (1.0, 1.0, 1.0), 'energy': 2.0, 'angle': 0.8447392582893372, 'light_type' : 'SUN'}
]


# UI
class MRPanel(bpy.types.Panel):
    bl_label = "Material Register"
    bl_idname = "OBJECT_PT_MR"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Material Register"

    def draw(self, context):
        layout = self.layout
        mytool = context.scene.my_tool
        row = layout.row()
        row.prop(mytool, "target_material")
        row = layout.row()
        row.prop(mytool, "light_type")
        row = layout.row()
        row.operator("object.mr_operator")
        

class MROperator(bpy.types.Operator):
    bl_idname = "object.mr_operator"
    bl_label = "Register"

    def execute(self, context):
        mytool = context.scene.my_tool
        my_material = mytool.target_material
        light_type = mytool.light_type
        if my_material == None:
            self.report({'ERROR'}, "Material is not set!! Please set the material you want to save.")
            return {'FINISHED'}
        
        if not bpy.data.filepath:
            self.report({'ERROR'}, "File not saved!! Please save .blend file.")
            return {'FINISHED'}
        
        db_file_path = os.path.join(APP_DATA_DIR, APP_DIR, PACKAGE_NAME, DB_FILE_NAME)
        if not os.path.isfile(db_file_path):
            with open(db_file_path, 'w'):
                pass
        
        thumbnail_path = os.path.join(pathlib.Path(bpy.data.filepath).parent, my_material.name + ".png")

        switch_all_objects_visible(False)
        switch_all_objects_render(False)
        collection = generate_objects(my_material.name, light_type)
        render(thumbnail_path)
        delete_objects(collection)
        switch_all_objects_visible(True)
        
        # thumbnail path
        print(thumbnail_path)
        # .blend file path
        print(bpy.data.filepath)
        # material name
        print(my_material.name)
        
        conn = sqlite3.connect(db_file_path)
        cur = conn.cursor()
        cur.execute(f'SELECT * FROM sqlite_master WHERE type="table" AND name="{DB_TABLE_NAME}"')
        if not cur.fetchone():
            cur.execute(f'CREATE TABLE {DB_TABLE_NAME}(id integer primary key autoincrement, thumbnail_path TEXT, blend_file_path TEXT, material_name TEXT)')
        cur.execute(f'INSERT INTO {DB_TABLE_NAME}(thumbnail_path, blend_file_path, material_name) VALUES("{thumbnail_path}", "{bpy.data.filepath}", "{my_material.name}")')
        conn.commit()
        conn.close()

        return{'FINISHED'}


class MRProperties(bpy.types.PropertyGroup):
    light_type : bpy.props.EnumProperty(
        name="Light Type",
        description='Change Light Postion',
        default='1',
        items=[
            ('1', 'Type 1', 'Number of lights is 1.'),
            ('2', 'Type 2', 'Number of ligths is 8.')
        ]
    )
    
    target_material : bpy.props.PointerProperty(name="Target Material", type=bpy.types.Material)
    
    
# Action
def switch_all_objects_visible(visible=False):
    for item in bpy.data.objects:
        item.hide_set(not visible)


def switch_all_objects_render(available=False):
    for item in bpy.data.objects:
        item.hide_render = not available
        

def generate_material():
    color = (255, 0, 0, 1)
    ma = bpy.data.materials.new("new_material")
    ma.use_nodes = True
    bsdf = ma.node_tree.nodes['Principled BSDF']
    bsdf.inputs[0].default_value = color
    bsdf.inputs[4].default_value = 1
    bsdf.inputs[6].default_value = 0.5
    bsdf.inputs[7].default_value = 1
    bsdf.inputs[9].default_value = 0
    bpy.context.object.data.materials.append(ma)
    ma.diffuse_color = color
    return ma


def generate_objects(material_name, light_type):
  # Generate Collection 
  new_collection = bpy.data.collections.new("collection_for_material")
  scene_collection = bpy.context.scene.collection
  scene_collection.children.link(new_collection)
  layer_collection = bpy.context.view_layer.layer_collection.children[new_collection.name]
  bpy.context.view_layer.active_layer_collection = layer_collection
  
  # Generate Sphere
  bpy.ops.mesh.primitive_uv_sphere_add(
    segments=32,
    ring_count=16,
    radius=1.0,
    location=(0.0, 0.0, 0.0),
    rotation=(0.0, 0.0, 0.0)
  )
  obj = bpy.context.view_layer.objects.active
  obj.name = "sphere_for_material"
  obj.scale=(1, 1, 1)
  obj.select_set(False)
  # Set material
  my_material = bpy.data.materials[material_name]
  obj.data.materials.append(my_material)
  
  # Set modifier
  bpy.ops.object.modifier_add(type='SUBSURF')
  bpy.context.active_object.modifiers["Subdivision"].render_levels = 2
  for poly in obj.data.polygons:
      poly.use_smooth = True
      
  # Generate Light
  if light_type == '1':
    prop = light_settings_type_1[0]
    print(light_settings_type_1)
    print(prop['name'])
    print(prop['light_type'])
    light_data = bpy.data.lights.new(name=prop['name'], type=prop['light_type'])
    light_data.energy = prop['energy']
    light_data.shape = prop['shape']
    light_data.color = prop['color']
    light_data.size = prop['size']
    light_object = bpy.data.objects.new(prop['name'], light_data)
    light_object.location = prop['location']
    light_object.rotation_euler = prop['rotation']
    new_collection.objects.link(light_object)
  else:
      for prop in light_settings_type_2:
        light_data = bpy.data.lights.new(name=prop['name'], type=prop['light_type'])
        light_data.energy = prop['energy']
        light_data.angle = prop['angle']
        light_data.color = prop['color']
        light_object = bpy.data.objects.new(prop['name'], light_data)
        light_object.location = prop['location']
        light_object.rotation_euler = prop['rotation']
        new_collection.objects.link(light_object)

  # Generate Camera
  camera_data = bpy.data.cameras.new(name="camera_for_material")
  camera = bpy.data.objects.new("camera_for_material", camera_data)
  camera.location = (0, -3.5, 0)
  camera.rotation_euler = (math.radians(90), 0, 0)
  new_collection.objects.link(camera)
  bpy.context.scene.camera = camera
  return new_collection


def delete_objects(target_col):
    bpy.ops.object.select_all(action='DESELECT')
    if target_col != None: 
        for item in target_col.all_objects:
            target_obj = bpy.data.objects[item.name]
            if target_obj != None:
                target_obj.select_set(True)

        bpy.ops.object.delete()
        bpy.data.collections.remove(target_col)


def render(filepath):
    render = bpy.context.scene.render
    cycles = bpy.context.scene.cycles
    before_engine = render.engine
    before_render_x = render.resolution_x
    before_render_y = render.resolution_y
    before_resolution_percentage = render.resolution_percentage
    before_file_format = render.image_settings.file_format
    before_film_transparent = render.film_transparent
    if (before_engine == 'CYCLES'):
        before_device = cycles.device
        before_film_transparent_glass = cycles.film_transparent_glass
    
    bpy.ops.object.mode_set(mode = 'OBJECT')
    render.engine = 'CYCLES'
    cycles.device = 'GPU'
    render.resolution_x = render_width
    render.resolution_y = render_height
    render.resolution_percentage = 100
    render.film_transparent = True
    cycles.film_transparent_glass = True
    
    render.image_settings.file_format = 'PNG'
    bpy.ops.render.render()
    bpy.data.images['Render Result'].save_render(filepath)
    # print(bpy.context.scene.render.filepath)  ## /tmp
    
    render.engine = before_engine
    render.resolution_x = before_render_x
    render.resolution_y = before_render_y
    render.resolution_percentage = before_resolution_percentage
    render.image_settings.file_format = before_file_format
    render.film_transparent = before_film_transparent
    if (before_engine == 'CYCLES'):
        cycles.device = before_device
        cycles.film_transparent_glass = before_film_transparent_glass


classes = (
    MRPanel,
    MROperator,
    MRProperties
)


def register():
    for regist_cls in classes:
        bpy.utils.register_class(regist_cls)
    bpy.types.Scene.my_tool = bpy.props.PointerProperty(type=MRProperties)


def unregister():
    for regist_cls in classes:
        bpy.utils.unregister_class(regist_cls)
    del bpy.types.Scene.my_tool


if __name__ == "__main__":
    register()