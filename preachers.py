import bpy
import re


def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower() for text in re.split('(\d+)', s.name)]


def convert_string(input_str, x):
    # 正規表現を使用して数字部分を抽出
    # マッチした数字の部分を取得
        match = re.match(r'^(\d+)_', input_str)
        if match:
            return re.sub(r'^(\d+)_', str(x) + '_', input_str)
        else:
            return input_str

bl_info = {
    "name": "Preachers",
    "author": "kiku",
    "version": (1, 0),
    "blender": (3, 3, 0),
    "location": "",
    "description": "Preachers",
    "warning": "",
    "support": "TESTING",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Object"
}


# カスタムのNキーパネル用のパネルクラスを定義する
class PPEACHERS_PT_Panel(bpy.types.Panel):
    bl_label = "Preachers"
    bl_idname = "PPEACHERS_PT_Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Tool"

    def draw(self, context):
        layout = self.layout
        # パネルにツールを追加する
        layout.operator("object.toggle_wire", text="Toggle Wireframe")
        layout.prop(context.scene, "layer_offset")
        layout.operator("object.order_layer", text="Order Layer")
        layout.operator("object.rename_layer", text="Rename Layer")


# ワイヤーフレーム表示/非表示を切り替える
class OBJECT_OT_ToggleWireframe(bpy.types.Operator):
    bl_idname = "object.toggle_wire"
    bl_label = "Toggle Wireframe"

    def execute(self, context):
        selected_objects = bpy.context.selected_objects
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
class OBJECT_OT_OrderLayer(bpy.types.Operator):
    bl_idname = "object.order_layer"
    bl_label = "Order Layer"

    def execute(self, context):
        offset = context.scene.layer_offset
        selected_objects = bpy.context.selected_objects
        count = len(selected_objects)
        center_index = round(count / 2) - 1
        sorted_objects = sorted(selected_objects, key=natural_sort_key)
        for index, obj in enumerate(sorted_objects):
            obj.location.y = (center_index - index) * offset
        return {'FINISHED'}


class OBJECT_OT_RenameLayer(bpy.types.Operator):
    bl_idname = "object.rename_layer"
    bl_label = "Rename Layer"

    def execute(self, context):
        selected_objects = bpy.context.selected_objects
        sorted_objects = sorted(selected_objects, key=natural_sort_key)
        count = 1
        for obj in sorted_objects:
            obj.name = convert_string(obj.name, count)
            obj.material_slots[0].material.name = obj.name
            count += 1
        return {'FINISHED'}


# アドオンの登録
def register():
    bpy.utils.register_class(PPEACHERS_PT_Panel)
    bpy.utils.register_class(OBJECT_OT_ToggleWireframe)
    bpy.types.Scene.layer_offset = bpy.props.FloatProperty(name="Layer Offset", default=0.01)
    bpy.utils.register_class(OBJECT_OT_OrderLayer)
    bpy.utils.register_class(OBJECT_OT_RenameLayer)



def unregister():
    bpy.utils.unregister_class(PPEACHERS_PT_Panel)
    bpy.utils.unregister_class(OBJECT_OT_ToggleWireframe)
    bpy.utils.unregister_class(OBJECT_OT_OrderLayer)
    bpy.utils.unregister_class(OBJECT_OT_RenameLayer)
    del bpy.types.Scene.layer_offset


# スクリプトが単体で実行される場合、アドオンを自動で登録する
if __name__ == "__main__":
    register()