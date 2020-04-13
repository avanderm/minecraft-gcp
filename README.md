# Minecraft on GCP

Templates for running Minecraft on one VM instance on GC with a static IP, making backups every 4 hours to Cloud Storage. Adapted largely from https://cloud.google.com/solutions/gaming/minecraft-server.

To deploy, run:
```bash
gcloud deployment-manager deployments create minecraft --config config.yaml
```
