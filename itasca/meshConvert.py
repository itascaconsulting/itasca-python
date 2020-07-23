import itasca as it
gmsh_template = r"""$MeshFormat
2.2 0 8
$EndMeshFormat
$Nodes
{}
{}$EndNodes
$Elements
{}
{}$EndElements
"""
flac3d_brick_to_gmsh = [2,4,7,5,0,1,6,3]
flac3d_wedge_to_gmsh = [5,2,4,3,0,1]
flac3d_tet_to_gmsh = [0,2,3,1]
flac3d_pyramid_to_gmsh = [2,0,1,4,3]


def FLAC3D_to_gmsh(filename="tmp.gmsh"):
    """
    Convert the current FLAC3D model in to the Gmsh format. Returns a mesh filename.
    """

    gp_id_to_index = { gp.id() : i+1 for i,gp in enumerate(it.gridpoint.list())}

    gp_data = ""
    for i,gp in enumerate(it.gridpoint.list()):
        gp_data +="{} {} {} {}\n".format(i+1, *gp.pos())

    element_data = ""
    for i,z in enumerate(it.zone.list()):
        element_type = None
        gp_list = [gp_id_to_index[gp.id()] for gp in z.gridpoints()]

        if z.type() == "brick":
            element_type = 5
            gp_list = [gp_list[j] for j in flac3d_brick_to_gmsh]
        elif z.type() == "wedge":
            element_type = 6
            gp_list = [gp_list[j] for j in flac3d_wedge_to_gmsh]
        elif z.type() == "pyramid":
            gp_list = [gp_list[j] for j in flac3d_pyramid_to_gmsh]
            element_type = 7
        elif z.type() == "tetra":
            element_type = 4
            gp_list = [gp_list[j] for j in flac3d_tet_to_gmsh]
        elif z.type() == "dbrick":
            raise ValueError("Degenerate bricks are not supported.")

        element_data += "{} {} 2 99 2 {}\n".format(i+1, element_type, " ".join(map(str,gp_list)))

    with open(filename, "w") as f:
        print(gmsh_template.format(it.gridpoint.count(), gp_data, it.zone.count(), element_data), file=f)
    return filename
