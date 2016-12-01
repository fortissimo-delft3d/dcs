
from xml.etree.ElementTree import Element, SubElement, tostring
import json
import logging
from logging.config import dictConfig

with open('logging.json') as jl:
    dictConfig(json.load(jl))


def build_template(uuid, machine_type="medium"):

    logging.info("Constructing xml for machine '%s'" % machine_type)
    
    # medium machine type; default
    n_cpus = "4"
    mem    = "8192"

    if machine_type == "extrasmall":
      n_cpus = 1
      mem    = 2048
    elif machine_type == "small":
      n_cpus = 2
      mem    = 4096
    if machine_type == "large":
      n_cpus = "8"
      mem    = "16384"
    elif machine_type == "extralarge":
      n_cpus = "16"
      mem    = 32768

    template = Element("template")

    # context
    context = SubElement(template, "CONTEXT")
    SubElement(context, "NETWORK")       .text = "YES"

    # NOTE: the ssh key is not necessary for the delft3d-user, becaus this
    # user's key has been setup in the users authorized keys.
    SubElement(context, "SSH_PUBLIC_KEY").text = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAAAgQDHbKtlGI/JsHMh7c0zwXK6IlPRcAxXurXL5QltOgAe7s6idaq2wFQnSvahKPrb5Dy4LQ5jCjJ5NmnaasIKxV5FN5alefm1AHtyR5Yhl2xw0J5cu0SA1aKONoOlvvT8E9jY8uneRLpLOCZv5zZAKwtNQpAfJRQLyIUfd7B0dAuRiw== Delft3d User"

    # CPU
    SubElement(template, "CPU")          .text = n_cpus

    # DISK
    disk = SubElement(template, "DISK")
    SubElement(disk, "IMAGE")            .text = "delft3d-worker-os-python-v6"


    # FEATURES
    features = SubElement(template, "FEATURES")
    SubElement(features, "ACPI")         .text = "yes"
    SubElement(features, "LOCALTIME")    .text = "no"

    # GRAPHICS
    graphics = SubElement(template, "GRAPHICS")
    SubElement(graphics, "LISTEN")       .text = "0.0.0.0"
    SubElement(graphics, "TYPE")         .text = "vnc"

    # MEMORY
    SubElement(template, "MEMORY")       .text = mem

    ## NIC (Network interfaces)
    nic = SubElement(template, "NIC")
    SubElement(nic, "NETWORK")           .text = "internet"
    SubElement(nic, "NETWORK_UNAME")     .text = "oneadmin"

    # VCPU
    SubElement(template, "VCPU")         .text = n_cpus

    SubElement(template, "MACHINE_ID")   .text = uuid

    return tostring(template)

