COMPUTE_URL_BASE = "https://www.googleapis.com/compute/v1/"


def GlobalComputeUrl(project, collection, name):
    return "".join(
        [
            COMPUTE_URL_BASE,
            "projects/",
            project,
            "/global/",
            collection,
            "/",
            name
        ]
    )


def ZonalComputeUrl(project, zone, collection, name):
    return "".join(
        [
            COMPUTE_URL_BASE,
            "projects/",
            project,
            "/zones/",
            zone,
            "/",
            collection,
            "/",
            name,
        ]
    )


def GenerateConfig(context):
    resources = []

    datadisk = "datadisk-{deployment}".format(deployment=context.env["deployment"])
    disk_properties = {
        "zone": context.properties["zone"],
        "sizeGB": 50,
        "type": ZonalComputeUrl(
            context.env["project"],
            context.properties["zone"],
            "diskTypes",
            "pd-ssd"
        )
    }

    instanceip = "address-{deployment}".format(deployment=context.env["deployment"])
    ip_properties = {
        "region": context.properties["region"]
    }

    instance_properties = {
        "zone": context.properties["zone"],
        "machineType": ZonalComputeUrl(
            context.env["project"],
            context.properties["zone"],
            "machineTypes",
            context.properties["machine-type"]
        ),
        "disks": [
            {
                "deviceName": "boot",
                "type": "PERSISTENT",
                "boot": True,
                "autoDelete": True,
                "initializeParams": {
                    "diskName": "disk-" + context.env["deployment"],
                    "sourceImage": GlobalComputeUrl(
                        "debian-cloud",
                        "images",
                        "family/debian-9"
                    )
                }
            },
            {
                "deviceName": "minecraft-disk",
                "type": "PERSISTENT",
                "source": "$(ref.{}.selfLink)".format(datadisk),
                "autoDelete": True
            }
        ],
        "networkInterfaces": [
            {
                "accessConfigs": [
                    {
                        "name": "external-nat",
                        "type": "ONE_TO_ONE_NAT",
                        "natIP": "$(ref.{}.address)".format(instanceip)
                    }
                ],
                "network": GlobalComputeUrl(
                    context.env["project"],
                    "networks",
                    "default"
                )
            }
        ],
        "serviceAccounts": [
            {
                "email": "default",
                "scopes": [
                    "https://www.googleapis.com/auth/logging.write",
                    "https://www.googleapis.com/auth/monitoring.write",
                    "https://www.googleapis.com/auth/devstorage.read_write",
                    "https://www.googleapis.com/auth/trace.append"
                ]
            }
        ],
        "tags": {
            "items": [
                "minecraft-server"
            ]
        },
        "metadata": {
            "items": [
                {
                    "key": "startup-script",
                    "value": context.properties["startup-script"]
                }
            ]
        }
    }

    firewall_properties = {
        "network": "global/networks/default",
        "sourceRanges": ["0.0.0.0/0"],
        "allowed": [
            {
                "IPProtocol": "TCP", "ports": [25565]
            }
        ],
        "targetTags": ["minecraft-server"]
    }


    resources.append({
        "type": "compute.v1.disk",
        "name": datadisk,
        "properties": disk_properties
    })

    resources.append({
        "type": "compute.v1.address",
        "name": instanceip,
        "properties": ip_properties
    })

    resources.append({
        "type": "compute.v1.instance",
        "name": "vm-{deployment}".format(deployment=context.env["deployment"]),
        "properties": instance_properties
    })

    resources.append({
        "type": "compute.v1.firewall",
        "name": "firewall-{deployment}".format(deployment=context.env["deployment"]),
        "properties": firewall_properties
    })

    return {
        "resources": resources
    }