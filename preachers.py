import bpy
import re

bl_info = {
    "name": "Preachers",
    "author": "kiku",
    "version": (2, 0),
    "blender": (3, 3, 0),
    "location": "3D view > right toolbar > Preachers",
    "description": "Preachers",
    "warning": "",
    "support": "TESTING",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Object"
}

from bpy.props import (
    FloatProperty,
    PointerProperty,
    EnumProperty,
    BoolProperty,
)

# 数字を含め自然にソートする
def _natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower() for text in re.split('(\d+)', s.name)]


def _convert_string(input_str, x):
    # 正規表現を使用して数字部分を抽出
    # マッチした数字の部分を取得
        match = re.match(r'^(\d+)_', input_str)
        if match:
            return re.sub(r'^(\d+)_', str(x) + '_', input_str)
        else:
            return input_str


# 変数を定義する
class PR_props_group(bpy.types.PropertyGroup):
    layer_offset: FloatProperty(
        name = "layer offset",
        description = "offset between each layers",
        default = 0.01,
        min = 0.0,
    ) # type: ignore

    image_size: EnumProperty(
        name = "image size",
        description = "image size",
        items = [
            ("1k", "1K(1024x1024)", ""),
            ("2k", "2K(2048x2048)", ""),
            ("4k", "4K(4096x4096)", ""),
        ]
    ) # type: ignore

    rotate_parts: BoolProperty(
        name = "rotate parts",
        description = "Rotate Parts",
        default = False,
    ) # type: ignore

    pack_margin: FloatProperty(
        name = "pack margin",
        description = "pack margin",
        default = 0.02,
        min = 0.0,
    ) # type: ignore


# Preachers用メニューパネル
class PR_PT_Panel(bpy.types.Panel):
    bl_label = "Preachers"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Tool"
    bl_context = "objectmode" # only in object mode

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        layout.operator("object.toggle_wire", text="Toggle Wireframe")
        layout.prop(context.scene.pr_props, "layer_offset")
        layout.operator("object.order_layer", text="Order Layer")
        layout.operator("object.rename_layer", text="Rename Layer")
        layout.prop(context.scene.pr_props, "image_size")
        layout.prop(context.scene.pr_props, "rotate_parts")
        layout.prop(context.scene.pr_props, "pack_margin")
        layout.operator("object.uv_square", text="Square UV Pack")
        layout.operator("object.bake_texture", text="Bake Texture")
        layout.operator("object.make_integrated_material", text="Set Material")
        layout.operator("object.create_vertex_group", text="Create Vertex Group")
        layout.operator("object.integrate_objects", text="Integrate Objects")


# ワイヤーフレーム表示/非表示を切り替える
class PR_OT_ToggleWireframe(bpy.types.Operator):
    bl_idname = "object.toggle_wire"
    bl_label = "Toggle Wireframe"
    bl_description = "Turns the wireframe display of selected objects on and off."

    def execute(self, context):
        selected_objects = context.selected_objects
        is_all_wireframe_off = True
        for obj in selected_objects:
            if obj.show_wire:
                is_all_wireframe_off = False
                break
        for obj in selected_objects:
            if is_all_wireframe_off:
                obj.show_wire = True
            else:
                obj.show_wire = False
        return {'FINISHED'}


# 選択したオブジェクトを上から順に位置を調整する
class PR_OT_OrderLayer(bpy.types.Operator):
    bl_idname = "object.order_layer"
    bl_label = "Order Layer"
    bl_description = "Place the selected object by shifting it by an offset."

    def execute(self, context):
        offset = context.scene.pr_props.layer_offset
        selected_objects = context.selected_objects
        count = len(selected_objects)
        center_index = round(count / 2) - 1
        sorted_objects = sorted(selected_objects, key=_natural_sort_key)
        for index, obj in enumerate(sorted_objects):
            obj.location.y = (center_index - index) * offset
        return {'FINISHED'}


# 選択したオブジェクトを、1から順にプレフィックスをつけてリネームする
class PR_OT_RenameLayer(bpy.types.Operator):
    bl_idname = "object.rename_layer"
    bl_label = "Rename Layer"
    bl_description = "Rename selected objects with a numeric prefix."

    def execute(self, context):
        selected_objects = context.selected_objects
        sorted_objects = sorted(selected_objects, key=_natural_sort_key)
        count = 1
        for obj in sorted_objects:
            obj.name = _convert_string(obj.name, count)
            obj.material_slots[0].material.name = obj.name
            count += 1
        return {'FINISHED'}


# 選択したオブジェクトを、正方形でUV展開し直す
class PR_OT_UV_Square(bpy.types.Operator):
    bl_idname = "object.uv_square"
    bl_label = "Square UV Pack"
    bl_description = "Add UVMap to selected object and expand square UV."

    def execute(self, context):
        # UV展開・ベイクする用の画像を作成
        tex_name = "tex_bake"
        sizes = {"1k": 1024, "2k": 2048, "4k": 4096}
        size = sizes[context.scene.pr_props.image_size]
        image = bpy.data.images.new(name=tex_name, width=size, height=size, alpha=True)
        pixels = [0.0] * size * size * 4
        image.pixels = pixels

        # UVエディタの画面を取得
        for area in bpy.context.screen.areas:
            if area.type == 'IMAGE_EDITOR':
                for space in area.spaces:
                    if space.type == 'IMAGE_EDITOR':
                        # UVエディタに画像を設定
                        space.image = image
                        break


        layer_name = "UVMap.square"
        # 選択中のオブジェクトを取得
        selected_objects = context.selected_objects
        for obj in selected_objects:
            # 1つずつ処理するためにいったんすべて選択を解除する
            obj.select_set(False)
        for obj in selected_objects:
            # 選択状態にする
            obj.select_set(True)
            # 統合用UVマップの作成・選択
            if not layer_name in obj.data.uv_layers:
                obj.data.uv_layers.new(name=layer_name)
            obj.data.uv_layers.active = obj.data.uv_layers[layer_name]
            # 選択状態を解除
            obj.select_set(False)
        
        # UV展開する
        for obj in selected_objects:
            obj.select_set(True)
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.select_all(action='SELECT')
        bpy.ops.uv.cube_project(correct_aspect=False, cube_size=1,)
        bpy.ops.uv.pack_islands(margin=context.scene.pr_props.pack_margin, rotate=context.scene.pr_props.rotate_parts)

        return {'FINISHED'}

# 選択したオブジェクトのテクスチャを、1つのテクスチャにベイクする
class PR_OT_Bake_Texture(bpy.types.Operator):
    bl_idname = "object.bake_texture"
    bl_label = "Bake Texture"
    bl_description = "Bake Texture."
    
    def execute(self, context):
        tex_name = "tex_bake"

        # マテリアルにテクスチャノードを作成
        selected_objects = bpy.context.selected_objects
        for obj in selected_objects:
            # マテリアルスロット1のマテリアルにテクスチャノードを追加する
            mat = obj.material_slots[0].material
            if mat.use_nodes:
                tree = mat.node_tree
                # テクスチャノードを作成し、tex_character.pngを割り当てる
                tex_node = tree.nodes.new('ShaderNodeTexImage')
                tex_node.image = bpy.data.images.get(tex_name)
                # 作成したテクスチャノードを選択状態にする
                tree.nodes.active = tex_node
        
        # ベイク設定
        bpy.context.scene.render.engine = 'CYCLES'
        bpy.context.scene.render.bake_margin = 0
        bpy.context.scene.render.use_bake_multires = False
        bpy.context.scene.render.bake.use_pass_direct = False
        bpy.context.scene.render.bake.use_pass_indirect = False
        bpy.ops.object.bake(type='DIFFUSE')

        # 画像を保存し、blenderにロードする
        image = bpy.data.images[tex_name]
        bpy.context.scene.render.image_settings.color_depth = '16'
        bpy.context.scene.render.image_settings.compression = 0
        bpy.context.scene.render.image_settings.linear_colorspace_settings.name = 'sRGB'
        output_path = bpy.path.abspath("//tex_material.png")
        bpy.data.images[tex_name].save_render(output_path, scene=None, )
        bpy.data.images.load(output_path)

        return {'FINISHED'}


# 選択したオブジェクトに、ベイクしたテクスチャによるマテリアルを適用する
class PR_OT_Make_Integrated_Material(bpy.types.Operator):
    bl_idname = "object.make_integrated_material"
    bl_label = "Set material"
    bl_description = "Apply a material with a baked texture to selected objects."

    def execute(self, context):
        # 統合用マテリアルの作成
        material_name = "character"
        character_material = bpy.data.materials.get(material_name)
        if not character_material:
            character_material = bpy.data.materials.new(name=material_name)
        character_material.use_nodes = True
        character_material.blend_method = 'BLEND'
        tree = character_material.node_tree
        bsdf_node = None
        tex_node = None
        for node in tree.nodes:
            if node.type == 'BSDF_PRINCIPLED':
                bsdf_node = node
            elif node.type == 'TEX_IMAGE':
                tex_node = node
        if tex_node is None:
            tex_node = tree.nodes.new('ShaderNodeTexImage')
            tex_name = "tex_material.png"
            tex = bpy.data.images.get(tex_name)
            tex_node.image = tex
            tree.links.new(tex_node.outputs['Color'], bsdf_node.inputs['Base Color'])
            tree.links.new(tex_node.outputs['Alpha'], bsdf_node.inputs['Alpha'])
        
        # 選択中のオブジェクトに対してマテリアルをセットする
        selected_objects = context.selected_objects
        for obj in selected_objects:
            obj_materials = [slot.material for slot in obj.material_slots]
            if character_material not in obj_materials:
                obj.data.materials.clear()
                obj.data.materials.append(character_material)
            # 既存のUVマップを削除する
            uv_name_layer_map = {}
            for uv_layer in obj.data.uv_layers:
                uv_name_layer_map[uv_layer.name] = uv_layer
            for name in uv_name_layer_map.keys():
                print(name)
                if name != "UVMap.square":
                    print("↑消す")
                    obj.data.uv_layers.remove(uv_name_layer_map[name])
        
        return {'FINISHED'}


# 頂点グループを作成する
class PR_OT_Create_Vertex_Group(bpy.types.Operator):
    bl_idname = "object.create_vertex_group"
    bl_label = "Create Vertex Group"
    bl_description = "Create vertex group by each selected object layers."

    def execute(self, context):
        selected_objects = context.selected_objects
        for obj in selected_objects:
            if obj.type == 'MESH':
                vertex_group = obj.vertex_groups.new(name=obj.name)
                vertex_indices = [v.index for v in obj.data.vertices]
                vertex_group.add(vertex_indices, 1.0, 'ADD')
        return {'FINISHED'}


# レイヤーを統合する
class PR_OT_Integrate_Objects(bpy.types.Operator):
    bl_idname = "object.integrate_objects"
    bl_label = "Integrate Objects"
    bl_description = "Integrate Objects"

    def execute(self, context):
        # 半透明のオブジェクトの重なりを処理するため、上のレイヤーのオブジェクトから結合していく必要がある
        selected_objects = context.selected_objects
        sorted_objects = sorted(selected_objects, key=_natural_sort_key)
        sorted_objects.reverse()
        
        for obj in sorted_objects:
            # いったんすべて選択を解除する
            obj.select_set(False)
        for i in range(len(sorted_objects) - 1):
            base_obj = sorted_objects[i]
            active_obj = sorted_objects[i + 1]
            base_obj.select_set(True)
            bpy.context.view_layer.objects.active = active_obj
            active_obj.select_set(True)
            print(base_obj.name)
            print(active_obj.name)
            bpy.ops.object.join()
            print("joined")
        

        return {'FINISHED'}
        # # 選択されたオブジェクトを統合する
        # bpy.ops.object.join()

        # # 統合されたオブジェクトを取得する
        # joined_object = bpy.context.object

        # # 統合された前のオブジェクトのレイヤーの表示順を保存する
        # original_layers_order = []
        # for obj in bpy.context.selected_objects:
        #     original_layers_order.append(obj.layers[:])

        # # 統合されたオブジェクトにレイヤーの表示順を適用する
        # for i, layer in enumerate(original_layers_order[0]):
        #     joined_object.layers[i] = layer

        # print("オブジェクトの統合が完了しました。")


classes = (
    PR_PT_Panel,
    PR_OT_ToggleWireframe,
    PR_OT_OrderLayer,
    PR_OT_RenameLayer,
    PR_OT_UV_Square,
    PR_OT_Bake_Texture,
    PR_OT_Make_Integrated_Material,
    PR_OT_Integrate_Objects,
    PR_OT_Create_Vertex_Group,
)


def register():
    bpy.utils.register_class(PR_props_group)
    bpy.types.Scene.pr_props = PointerProperty(type = PR_props_group)
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    bpy.utils.unregister_class(PR_props_group)
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()