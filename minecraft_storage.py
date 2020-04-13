def GenerateConfig(context):
    resources = []
    outputs = []

    backup_bucket = "bucket-{deployment}".format(deployment=context.env["deployment"])

    bucket_properties = {
        "location": context.properties["location"],
        "kind": "storage#bucket",
        "storageClass": "STANDARD",
        "lifecycle": {
            "rule": [
                {
                    "action": {
                        "type": "Delete"
                    },
                    "condition": {
                        "age": 7
                    }
                }
            ]
        }
    }

    resources.append({
        "type": "storage.v1.bucket",
        "name": backup_bucket,
        "properties": bucket_properties
    })

    outputs.append({
        "name": "bucket",
        "value": "$(ref.{}.name)".format(backup_bucket)
    })

    return {
        "resources": resources,
        "outputs": outputs
    }
