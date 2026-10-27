Status: CURRENT AUTHORITATIVE

# Provisioning design 2026

## Transport

The provisioning transport is HTTPS polling.
This replaces the MQTT transport described in design-2025.

## Recovery

Root A/B recovery is rejected for the target image; snapshots are used instead.
