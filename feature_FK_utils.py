import maya.cmds as cmds
from dataclasses import dataclass
import autorig.control_rig.module.create_node as create_node
import autorig.control_rig.module.query as module_query

@dataclass
class FKLinkData:
    module_name: str
    link_name: str
    guide_locator: str
    FK_control: str
    bind_joint: str
    driver_joint: str
    FK_joint: str

    #optional for chains
    aim_primary_locator: str|None = None
    aim_secondary_locator: str|None = None
    aim_matrix: str|None = None
    aim_inverse_matrix: str|None = None
    parent_offset_mult_matrix: str|None = None
    world_mult_matrix: str|None = None

def create_FK_aim_data(data_cls: FKLinkData) -> FKLinkData:
    aim_matrix = create_node.create_module_node('aimMatrix', 
                                    f"{data_cls.link_name}_FK_ctrl_aimM", 
                                    {'moduleParent': data_cls.module_name,
                                    'featureType': 'FK_aim_matrix'})

    aim_inverse_matrix = create_node.create_module_node('inverseMatrix', 
                                            f"{data_cls.link_name}_FK_ctrl_aimM_inverse",
                                            {'moduleParent': data_cls.module_name,
                                            'featureType': 'FK_aim_inverse_matrix'})

    aim_primary_locator = create_node.create_module_locator(f"{data_cls.link_name}_FK_primary_aim", {'moduleParent': data_cls.module_name,
                                              'featureType':"FK_primaryAim"})
    
    aim_secondary_locator = create_node.create_module_locator(f"{data_cls.link_name}_FK_secondary_aim", {'moduleParent': data_cls.module_name,
                                              'featureType':"FK_secondaryAim"})
    
    parent_offset_mult_matrix = create_node.create_module_node("multMatrix", 
                                                   f"{data_cls.link_name}_FK_ctrl_POM",
                                                   {'moduleParent': data_cls.module_name,
                                                    'featureType': 'FK_POM_mult_matrix'})

    world_mult_matrix = create_node.create_module_node("multMatrix", 
                                           f"{data_cls.link_name}_FK_ctrl_WM",
                                           {'moduleParent': data_cls.module_name,
                                            'featureType': 'FK_WM_mult_matrix'})

    data_cls.aim_primary_locator = aim_primary_locator
    data_cls.aim_secondary_locator = aim_secondary_locator
    data_cls.aim_matrix = aim_matrix
    data_cls.aim_inverse_matrix = aim_inverse_matrix
    data_cls.parent_offset_mult_matrix = parent_offset_mult_matrix
    data_cls.world_mult_matrix = world_mult_matrix

    return data_cls

def create_FK_link_data(link_name: str, module_name: str) -> FKLinkData:
    bind_joint = module_query.find_single_node({"jointID": link_name,
                                                "featureType": 'bind_joint'})

    driver_joint = module_query.find_single_node({"jointID": link_name,
                                                  "featureType": 'driver_joint'})
    
    if not bind_joint:
        cmds.error(f"No bind joint ID in scene matches {link_name}.")
    if not driver_joint:
        cmds.error(f"No driver joint ID in scene matches {link_name}.")

       
    
    guide_locator = create_node.create_module_locator(f"{link_name}_FK_guide", {'moduleParent': module_name,
                                              'featureType':"FK_guide"})
    
    

    FK_control = create_node.create_placeholder_curve(f"{link_name}_FK_ctrl", {'moduleParent': module_name,
                                              'featureType':"FK_control",
                                              'controlID': link_name})
    
    FK_joint = create_node.create_module_node('joint', f"{link_name}_FK_joint", {'moduleParent': module_name,
                                              'featureType':"FK_joint",
                                              'jointID': link_name})

    return FKLinkData(
        module_name = module_name,
        link_name = link_name,
        guide_locator = guide_locator,
        FK_control = FK_control,
        bind_joint = bind_joint,
        driver_joint = driver_joint,
        FK_joint = FK_joint
    )

def create_FK_link(link_name: str, module_name: str,match_bind: bool =False) -> str:
    link_data = create_FK_link_data(link_name,module_name)

    if match_bind:
        cmds.matchTransform(link_data.guide_locator, link_data.bind_joint)
    else:
        cmds.matchTransform(link_data.guide_locator, link_data.bind_joint, pos=True)

    cmds.setAttr(f"{link_data.guide_locator}.visibility", 0)
    cmds.setAttr(f"{link_data.guide_locator}.visibility", keyable=False, channelBox=False)
    
    cmds.setAttr(f"{link_data.FK_control}.visibility", keyable=False, channelBox=False)

    cmds.delete(constructionHistory=True)
    cmds.select(clear=True)

    

    cmds.connectAttr(f"{link_data.guide_locator}.worldMatrix[0]", f"{link_data.FK_control}.offsetParentMatrix")

    cmds.connectAttr(f"{link_data.FK_control}.worldMatrix[0]", f"{link_data.FK_joint}.offsetParentMatrix")
    
    
    

    cmds.setAttr(f"{link_data.FK_joint}.visibility", 0)
    cmds.setAttr(f"{link_data.driver_joint}.visibility", 0)

    cmds.setAttr(f"{link_data.FK_joint}.visibility", keyable=False, channelBox=False)

    return link_data

def create_FK_chain(link_names: list[str], aim_direction: float, module_name: str, keep_end_control: bool = True):
    
    #create all nodes and assign them to FKLinkData dataclass
    root_locator = create_node.create_module_locator(f"{link_names[0]}_FK_root", {'moduleParent': module_name,
                                              'featureType':"FK_root"})
    
    driver_joint = module_query.find_single_node({"jointID": link_names[0],
                                                  "featureType": 'driver_joint'})
    
    module_locator = module_query.find_single_node({"moduleParent": module_name,
                                                           "featureType": "module_root"})
                                                          
    
    cmds.connectAttr(f"{module_locator}.worldMatrix[0]", f"{root_locator}.offsetParentMatrix")
    cmds.matchTransform(root_locator,driver_joint, position=True)

    link_data = []
    for i,link in enumerate(link_names):
        link_data_cls = create_FK_link(link, module_name)
        link_data_cls = create_FK_aim_data(link_data_cls)

        cmds.setAttr(f"{link_data_cls.aim_primary_locator}.visibility", 0)
        cmds.setAttr(f"{link_data_cls.aim_secondary_locator}.visibility", 0)

        cmds.connectAttr(f"{root_locator}.worldMatrix[0]", f"{link_data_cls.aim_primary_locator}.offsetParentMatrix")
        cmds.connectAttr(f"{root_locator}.worldMatrix[0]", f"{link_data_cls.aim_secondary_locator}.offsetParentMatrix")

        cmds.matchTransform(link_data_cls.aim_primary_locator, link_data_cls.driver_joint)
        cmds.xform(link_data_cls.aim_secondary_locator, r=True, os=True, t=(1,0,0))

        
        
        cmds.matchTransform(link_data_cls.aim_secondary_locator, link_data_cls.driver_joint)
        cmds.xform(link_data_cls.aim_secondary_locator, r=True, os=True, t=(0,1,0))
        link_data.append(link_data_cls)

    for last, current, next in zip([None] + link_data[:-1], link_data, link_data[1:] + [None]):
        cmds.connectAttr(f"{root_locator}.worldMatrix[0]", f"{current.guide_locator}.offsetParentMatrix")
        cmds.matchTransform(current.guide_locator, current.driver_joint)
        cmds.connectAttr(
            f"{current.guide_locator}.worldMatrix[0]",
            f"{current.aim_matrix}.inputMatrix"
        )

        cmds.setAttr(f"{current.aim_matrix}.primaryInputAxisX", aim_direction)
        cmds.setAttr(f"{current.aim_matrix}.secondaryInputAxisY", 1)
        cmds.setAttr(f"{current.aim_matrix}.secondaryMode", 1)

        cmds.connectAttr(
            f"{current.aim_matrix}.outputMatrix",
            f"{current.aim_inverse_matrix}.inputMatrix"
        )

        #cmds.connectAttr(f"{root_locator}.worldMatrix[0]", f"{current.aim_primary_locator}.offsetParentMatrix")

        cmds.connectAttr(
            f"{current.aim_primary_locator}.worldMatrix[0]",
            f"{current.aim_matrix}.primaryTargetMatrix"
        )

        #cmds.connectAttr(f"{root_locator}.worldMatrix[0]", f"{current.aim_secondary_locator}.offsetParentMatrix")

        cmds.connectAttr(
            f"{current.aim_secondary_locator}.worldMatrix[0]",
            f"{current.aim_matrix}.secondaryTargetMatrix"
        )

        cmds.connectAttr(
            f"{current.aim_matrix}.outputMatrix",
            f"{current.FK_control}.offsetParentMatrix",
            f=True
        )

        if last:
            cmds.connectAttr(f"{last.aim_inverse_matrix}.outputMatrix", f"{current.parent_offset_mult_matrix}.matrixIn[1]")
            cmds.connectAttr(f"{last.FK_control}.worldMatrix[0]", f"{current.world_mult_matrix}.matrixIn[1]")

        cmds.connectAttr(f"{current.aim_matrix}.outputMatrix", f"{current.parent_offset_mult_matrix}.matrixIn[0]")

        cmds.connectAttr(f"{current.parent_offset_mult_matrix}.matrixSum", f"{current.world_mult_matrix}.matrixIn[0]")
        

        cmds.connectAttr(f"{current.world_mult_matrix}.matrixSum", f"{current.FK_control}.offsetParentMatrix",f=True)

    if not keep_end_control:
        end_control_data = link_data[-1]

        link_data.pop(-1)

        cmds.delete(end_control_data.FK_control)
        cmds.delete(end_control_data.FK_joint)
        cmds.delete(end_control_data.guide_locator)
        cmds.delete(end_control_data.aim_primary_locator)
        cmds.delete(end_control_data.aim_secondary_locator)

    return root_locator,link_data

def parent_FK_nodes(root_locator,link_data):      
    for data in link_data:
        guide_node = module_query.find_single_node(attrs = {'featureType': 'guide_group',
                                        'moduleParent': data.module_name})
        cmds.parent(data.guide_locator,data.aim_primary_locator,data.aim_secondary_locator,root_locator,guide_node)
        
        joint_node = module_query.find_single_node(attrs = {'featureType': 'joint_group',
                                        'moduleParent': data.module_name})
        cmds.parent(data.FK_joint,joint_node)
        
        control_node = module_query.find_single_node(attrs = {'featureType': 'control_group',
                                        'moduleParent': data.module_name})
        cmds.parent(data.FK_control,control_node)