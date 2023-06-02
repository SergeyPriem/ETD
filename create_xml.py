# -*- coding: utf-8 -*-

def add_main_bus(txt, distr_bus_len, distr_bus_x, distr_bus_y, distr_bus_id, distr_bus_iid):
    new_comp = f"""<BUS Len_D2D="{distr_bus_len}" LocX_D2D="{distr_bus_x}" LocY_D2D="{distr_bus_y}" 
    ID="{distr_bus_id}" IID="{distr_bus_iid}" InService="true" InServiceState="As-Built" NominalkV="0.4"/>
    </COMPONENTS>"""
    txt = txt.replace("</COMPONENTS>", new_comp)
    return txt


def add_cb(txt, cb_x, cb_y, cb_from_elem, cb_id, cb_iid, cb_to_elem):
    new_comp = f"""<LVCB LocX_D2D="{cb_x}" LocY_D2D="{cb_y}" FromElement="{cb_from_elem}" 
    ID="{cb_id}" IID="{cb_iid}" InService="true" InServiceState="As-Built" ToElement="{cb_to_elem}"/>
    </COMPONENTS>"""
    txt = txt.replace("</COMPONENTS>", new_comp)
    return txt


def add_cable(txt, cb_x, cb_y, cb_from_elem, cab_id, cab_iid, cab_len, cab_to_bus):
    new_comp = f"""
    <CABLE LocX_D2D="{cb_x}" LocY_D2D="{cb_y + 1500}" ServiceState="1" FromBus="{cb_from_elem}" ID="{cab_id}"
    IID="{cab_iid}" LengthValue="{cab_len}" ToBus="{cab_to_bus}"/>
    </COMPONENTS>"""
    txt = txt.replace("</COMPONENTS>", new_comp)
    return txt


def add_load_bus(txt, cb_x, cb_y, load_bus_id, load_bus_iid):
    new_comp = f"""<BUS Len_D2D="100" Len="1" Node="1" LocX_D2D="{cb_x}" LocY_D2D="{cb_y + 3000}" ServiceState="1" 
    ID="{load_bus_id}" IID="{load_bus_iid}" InService="true" InServiceState="As-Built" NominalkV="0.4"/>
    </COMPONENTS>"""
    txt = txt.replace("</COMPONENTS>", new_comp)
    return txt


def add_motor(txt, cb_x, cb_y, load_bus_tag, motor_power, cos_f, motor_id, motor_iid):
    new_comp = f"""<INDMOTOR PhaseTypeString="3-Phase" LocX_D2D="{cb_x}" LocY_D2D="{cb_y + 4000}" Bus="{load_bus_tag}" 
    HP="{motor_power}" HP_KW="1" ID="{motor_id}" IID="{motor_iid}" KV="0.4" PF100="{cos_f}"></INDMOTOR>
    </COMPONENTS>"""
    txt = txt.replace("</COMPONENTS>", new_comp)
    return txt


def add_stat_load(txt, cb_x, cb_y, load_bus_tag, stat_load_kw, stat_load_kvar, stat_load_id, stat_load_iid):
    new_comp = f"""<STLOAD PhaseTypeString="3-Phase" LocX_D2D="{cb_x}" LocY_D2D="{cb_y + 4000}"
    ServiceState="1" Bus="{load_bus_tag}" ID="{stat_load_id}" IID="{stat_load_iid}" InService="true" KV="0.4" 
    KVAButton="1" Kvar="{stat_load_kvar}" KW="{stat_load_kw}"/>
    </COMPONENTS>"""
    txt = txt.replace("</COMPONENTS>", new_comp)
    return txt


def add_connect(txt, from_elem, from_id, from_iid, from_pin, to_elem, to_id, to_iid, to_pin):
    new_comp = f"""<CONNECT FromElement="{from_elem}" FromID="{from_id}" FromIID="{from_iid}" FromPin="{from_pin}" 
    ToElement="{to_elem}" ToID="{to_id}" ToIID="{to_iid}" ToPin="{to_pin}"/>
    </CONNECTIONS>"""
    txt = txt.replace("</CONNECTIONS>", new_comp)
    return txt


def add_feeder(load_type, txt, cb_x=None, cb_y=None, cb_from_elem=None, cb_id=None, cb_iid=None, cb_to_elem=None,
             cab_id=None, cab_iid=None, cab_len=None, cab_to_bus=None, load_bus_id=None, load_bus_iid=None,
             load_bus_tag=None, motor_power=None, cos_f=None, motor_id=None, motor_iid=None, stat_load_id=None, stat_load_iid=None,
             stat_load_kw=None, stat_load_kvar=None, distr_bus_id=None, distr_bus_iid=None):
    txt = add_cb(txt, cb_x, cb_y, cb_from_elem, cb_id, cb_iid, cb_to_elem)

    txt = add_cable(txt, cb_x, cb_y, cb_from_elem, cab_id, cab_iid, cab_len, cab_to_bus)

    txt = add_load_bus(txt, cb_x, cb_y, load_bus_id, load_bus_iid)

    if load_type in ['MOTOR', 'motor', 'Motor']:
        txt = add_motor(txt, cb_x, cb_y, load_bus_tag, motor_power, cos_f, motor_id, motor_iid)

        # txt = add_connect(txt, "INDMOTOR", stat_load_id, stat_load_iid, 0, "BUS", load_bus_id, load_bus_iid, 1)
    else:
        txt = add_stat_load(txt, cb_x, cb_y, load_bus_tag, stat_load_kw, stat_load_kvar, stat_load_id, stat_load_iid)
        # txt = add_connect(txt, "STLOAD", stat_load_id, stat_load_iid, 0, "BUS", load_bus_id, load_bus_iid, 1)

    # txt = add_connect(txt, "LVCB", cb_id, cb_iid, 0, "BUS", distr_bus_id, distr_bus_iid, 0)

    # txt = add_connect(txt, "LVCB", cb_id, cb_iid, 1, "CABLE", cab_id, cab_iid, 0)

    # txt = add_connect(txt, "CABLE", cab_id, cab_iid, 1, "BUS", load_bus_id, load_bus_iid, 0)

    return txt


# feeder_qty = 25 # len(feed_df)
# HOR_STEP = 4000
#
# distr_bus_len = 4000 * (feeder_qty + 2)
# distr_bus_x = 20000
# distr_bus_y = 10000
# distr_bus_id = "MCC1A"
# distr_bus_iid = "ps1100"
#
# cb_x = 17000
# cb_y = 11000
# cb_from_elem = "MCC1A"
# cb_id = "QF1"
# cb_iid = "ps1101"
# cb_to_elem = "L-512-00"
#
# cab_id = 'L-512-00'
# cab_iid = 'ps1102'
# cab_len = 150
# cab_to_bus = 'bus301'
#
# load_bus_id = 'bus301'
# load_bus_iid = 'ps1103'
#
# load_bus_tag = load_bus_id
#
#
# motor_power = 37
# motor_id = '419-00-PH-M'
# motor_iid = "ps1104"
#
# stat_load_kw = 15
# stat_load_kvar = 8
# stat_load_id = '419-00-PH-M'
# stat_load_iid = "ps1104"
#
# load_type = 'INDMOTOR'  # "STLOAD"

# with open('/content/xml_template.xml', 'r') as xml_file:
#     txt = xml_file.read()

# print(txt)
#
# txt = add_main_bus(txt, distr_bus_len, distr_bus_x, distr_bus_y, distr_bus_id, distr_bus_iid)
#
# txt = add_feeder(load_type, txt, cb_x=None, cb_y=None, cb_from_elem=None, cb_id=None, cb_iid=None, cb_to_elem=None,
#              cab_id=None, cab_iid=None, cab_len=None, cab_to_bus=None, load_bus_id=None, load_bus_iid=None,
#              load_bus_tag=None, motor_power=None, cos_f=None, motor_id=None, motor_iid=None, stat_load_id=None, stat_load_iid=None,
#              stat_load_kw=None, stat_load_kvar=None, distr_bus_id=None, distr_bus_iid=None)
