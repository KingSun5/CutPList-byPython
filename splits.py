# -*- coding: utf-8 -*-
import json
import os
from PIL import Image
import shutil
import os,sys
from xml.etree import ElementTree

CURRENT_PATH = os.getcwd()
SPLIT_OUT_PATH = os.path.join(CURRENT_PATH, "cut1")


# 输出文件夹
if os.path.exists(SPLIT_OUT_PATH):
    shutil.rmtree(SPLIT_OUT_PATH)
os.mkdir(SPLIT_OUT_PATH)

# 获取所有.json文件
cur_all_files = os.listdir(CURRENT_PATH)
json_names = []
for cmp_name in cur_all_files:
    if os.path.isdir(os.path.join(CURRENT_PATH, cmp_name)):
        continue
    name, ext = os.path.splitext(cmp_name)
    if ext.lower() != ".plist":
        continue
    json_names += [name]


def generate_texture(src_img, src_rect, offset_size, dst_size, dst_path, rotated):
    # 裁切的位置
    src_rect_l = [src_rect["x"], src_rect["y"], src_rect["x"] + src_rect["w"], src_rect["y"] + src_rect["h"]]

    adjust_w = (dst_size["w"] - src_rect["w"])/2
    adjust_h = (dst_size["h"] - src_rect["h"])/2

    dst_x = adjust_w + offset_size["x"]
    dst_y = adjust_h - offset_size["y"] 

    dst_w = dst_x + src_rect["w"]
    dst_h = dst_y + src_rect["h"]
    # 从裁切位置复制的位置
    dst_rect_l = [dst_x,dst_y,dst_w,dst_h]

    if rotated:
        src_rect_l = [src_rect["x"], src_rect["y"], src_rect["x"] + src_rect["h"], src_rect["y"] + src_rect["w"]]

    src_crop = src_img.crop(src_rect_l)
    if rotated:
        src_crop = src_crop.rotate(90, expand = 1)

    dst_img = Image.new("RGBA", [dst_size["w"],dst_size["h"]])
   
    dst_img.paste(src_crop, dst_rect_l)
    dst_img.save(dst_path)


def tree_to_dict(tree):
    d = {}
    for index, item in enumerate(tree):
        if item.tag == 'key':
            if tree[index+1].tag == 'string':
                d[item.text] = tree[index + 1].text
            elif tree[index + 1].tag == 'true':
                d[item.text] = True
            elif tree[index + 1].tag == 'false':
                d[item.text] = False
            elif tree[index+1].tag == 'dict':
                d[item.text] = tree_to_dict(tree[index+1])
    return d

def split_json(json_name):
    plist_filename = os.path.join(CURRENT_PATH, json_name+".plist")
    root = ElementTree.fromstring(open(plist_filename, 'r').read())
    plist_dict = tree_to_dict(root[0])

    print(plist_dict)

    to_list = lambda x: x.replace('{','').replace('}','').split(',')
   

    image = Image.open(os.path.join(CURRENT_PATH, json_name+".png"))
    image = image.resize((image.width, image.height),Image.ANTIALIAS)

    if not image:
        return
    if os.path.exists(os.path.join(SPLIT_OUT_PATH, json_name)):
        shutil.rmtree(os.path.join(SPLIT_OUT_PATH, json_name))
    os.mkdir(os.path.join(SPLIT_OUT_PATH, json_name))


    for k,v in plist_dict['frames'].items():
        dst_path = os.path.join(SPLIT_OUT_PATH, json_name + "\\" + k)

        spriteFrameStr  = to_list(v['frame'])
        spriteOffsetStr = to_list(v['offset'])
        spriteSizeStr   = to_list(v['sourceSize'])
        spriteRotStr    = v['rotated']

        framePos = {"x":(int)(spriteFrameStr[0]),"y":(int)(spriteFrameStr[1]),"w":(int)(spriteFrameStr[2]),"h":(int)(spriteFrameStr[3])}
        offsetSize = {"x":(int)(spriteOffsetStr[0]),"y":(int)(spriteOffsetStr[1])}
        sourceSize = {"w":(int)(spriteSizeStr[0]),"h":(int)(spriteSizeStr[1])}

        generate_texture(image, framePos, offsetSize, sourceSize, dst_path, spriteRotStr)
    image.close()

        
for json_name in json_names:
    print("##############:cut the "+ json_name+":##############")
    with open(os.path.join(CURRENT_PATH, json_name+".plist"), "r") as json_file:
        if not os.path.exists(json_name+".png"):
            continue
        split_json(json_name)
