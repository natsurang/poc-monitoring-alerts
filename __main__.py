"""A Google Cloud Python Pulumi program"""

import pulumi

config = pulumi.Config()
gcp_config = pulumi.Config("gcp")

environment = config.require("environment")
system_name = config.require("system_name")
resource_data = config.require_object("resource")

if (
    "gke" in resource_data
    and "pool_name" in resource_data["gke"]
    and "namespace" in resource_data["gke"]
):
    from components.policies.gke import create_gke_alert

    gke_saturation_alert = create_gke_alert(
        prefix_name=environment,
        system_name=system_name,
        pool_name=resource_data["gke"]["pool_name"],
        namespace_name=resource_data["gke"]["namespace"],
    )

if "sql" in resource_data and "instance_id" in resource_data["sql"]:
    from components.policies.sql import create_sql_saturation_high_alert

    sql_saturation_alert = create_sql_saturation_high_alert(
        prefix_name=environment,
        project_id=gcp_config.require("project"),
        system_name=system_name,
        instance_id=resource_data["sql"]["instance_id"],
    )

if "run" in resource_data:
    from components.policies.run import create_run_saturation_high_alert

    run_saturation_alert = create_run_saturation_high_alert(
        prefix_name=environment,
    )
