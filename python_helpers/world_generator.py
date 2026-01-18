import os
import xacro
import subprocess
import xml.etree.ElementTree as ET
import yaml

def local(tag: str) -> str:
    # Strip namespace: "{ns}tag" -> "tag"
    return tag.split('}', 1)[1] if '}' in tag else tag

def print_xml(node: ET.Element, indent: int = 0):
    pad = "  " * indent
    attrs = " ".join(f'{k}="{v}"' for k, v in node.attrib.items())
    open_tag = f"<{local(node.tag)}{(' ' + attrs) if attrs else ''}>"
    text = (node.text or "").strip()

    if text:
        print(f"{pad}{open_tag} {text}")
    else:
        print(f"{pad}{open_tag}")

    for child in list(node):
        print_xml(child, indent + 1)

    print(f"{pad}</{local(node.tag)}>")

def modify_world_file(pkg_path, world_file, config_file):
    world_file_updated = "/tmp/temp.sdf"
    world_tree = ET.parse(world_file)
    world_root = world_tree.getroot()
    if config_file.get("environment_setup") is not None:
        for key in config_file["environment_setup"].keys():
            model_sdf_path = os.path.join(pkg_path,"description" ,"worlds" ,"component" ,config_file["environment_setup"][key]["model_file"])
            model_tree = ET.parse(model_sdf_path)
            model_root = model_tree.getroot()
            pose=config_file["environment_setup"][key]["pose"]
            # print_xml(model_root)
            model_root.find('pose').text = pose
            for uri in model_root.iter("uri"):
                if uri.text:  # make sure it has text
                    uri.text = os.path.join(pkg_path, uri.text)
            world_root.find('world').append(model_root)

    world_root.find('.//latitude_deg').text = str(config_file["world_setup"]["latitude_origin"])
    world_root.find('.//longitude_deg').text = str(config_file["world_setup"]["longitude_origin"])
    ET.indent(world_tree, space="  ", level=0)
    # Save merged SDF
    world_tree.write(world_file_updated, encoding='utf-8', xml_declaration=True)
    return world_file_updated
