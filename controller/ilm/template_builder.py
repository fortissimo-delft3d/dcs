
from xml.etree.ElementTree import Element, SubElement, tostring

def build_template(uuid):

    template = Element("template")

    # context
    context = SubElement(template, "CONTEXT")
    SubElement(context, "NETWORK")       .text = "YES"
    SubElement(context, "SSH_PUBLIC_KEY").text = "root[SSH_PUBLIC_KEY]"

    # CPU
    SubElement(template, "CPU")          .text = "0.1"

    # DISK
    disk = SubElement(template, "DISK")
    SubElement(disk, "IMAGE")            .text = "ttylinux-delft3d"


    # FEATURES
    features = SubElement(template, "FEATURES")
    SubElement(features, "ACPI")         .text = "no"
    SubElement(features, "ACPI")         .text = "no"
    SubElement(features, "LOCALTIME")    .text = "no"

    # GRAPHICS
    graphics = SubElement(template, "GRAPHICS")
    SubElement(graphics, "LISTEN")       .text = "0.0.0.0"
    SubElement(graphics, "TYPE")         .text = "vnc"

    # MEMORY
    SubElement(template, "MEMORY")       .text = "128"

    ## NIC (Network interfaces)
    nic = SubElement(template, "NIC")
    SubElement(nic, "NETWORK")           .text = "cloud"
    SubElement(nic, "NETWORK_UNAME")     .text = "oneadmin"

    # VCPU
    SubElement(template, "VCPU")         .text = "1"

    SubElement(template, "MACHINE_ID")   .text = uuid

    return tostring(template)

