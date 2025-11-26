# Splunk Alert Action — LogicMonitor Update

This repository is a lightweight Splunk alert action app that updates custom properties on LogicMonitor devices when a Splunk alert fires. It adds a simple alert action UI and an executable helper which performs an HTTP PATCH against the LogicMonitor REST API.

## Key Features
- Provides a Splunk alert action named `LogicMonitor Update` that users can configure from the Alerts UI.
- UI fields for Device ID, Property Name, and Property Value so alerts can dynamically update LogicMonitor device properties.
- A small Python helper script (in `bin/`) that performs a PATCH request to the LogicMonitor API using a Bearer token.

## Repository layout

- `bin/logicmonitor_update.py` — Python executable that receives JSON input (from Splunk) and executes the PATCH request to update a custom property on a LogicMonitor device.
- `default/alert_actions.conf` — Splunk alert action configuration that defines the `logicmonitor_update` action used by alerts.
- `default/data/ui/alerts/logicmonitor_update.html` — UI form shown in Splunk's Alerts UI to collect `device_id`, `property_name`, and `property_value` from the user.
- `default/app.conf` and `local/app.conf` — app metadata and install/config state.
- `default/restmap.conf` — (optional) validation helpers for REST/action parameters.
- `README/` — additional configuration specification snippets.

## How it works (high-level)
1. A Splunk alert triggers and the `LogicMonitor Update` action is executed.
2. Splunk runs `bin/logicmonitor_update.py` and passes action configuration via JSON on stdin.
3. The script builds a JSON PATCH body and calls the LogicMonitor device PATCH endpoint to replace or set the specified custom property using a provided Bearer token.

## Configuration
Configure the alert action in Splunk (via the Alerts UI or `alert_actions.conf`). Example relevant lines in `default/alert_actions.conf`:

```
[logicmonitor_update]
is_custom = 1
label = LogicMonitor Property Update
description = HTTP PATCH to LogicMonitor API to update device properties
url = https://account.logicmonitor.com/santaba/rest/device/devices/
token = LM_Token
method = PATCH
payload_format = json
param.user_agent = Splunk/$server.guid$
```

## Local Config
Use `local/alert_actions` to set any local values that should be private and note overridden, such as `url` and `token`.

Required fields collected by the UI:
- Device ID — the LogicMonitor device identifier to target.
- Property to Update — the custom property name to set.
- Property Value — the new value for the property.

Script configuration (JSON passed to the script at runtime)
- `url` — full LogicMonitor API base URL (e.g. https://company.logicmonitor.com)
- `device_id` — numeric device id
- `property_name` — name of the custom property to add/update
- `property_value` — new property value
- `token` — Bearer token used for Authorization header
- `user_agent` — optional User-Agent header (defaults to `Splunk`)

The script expects to be called with the `--execute` flag and it reads JSON from stdin. On error it uses different exit codes:
- exit 1 — unsupported execution mode
- exit 2 — patch request failed
- exit 3 — unexpected error while processing

## Usage / Example
From Splunk this is triggered automatically by the configured alert action. If you want to invoke the script manually for testing, provide JSON to its stdin and include `--execute` on the command line. Example (POSIX / testing only):

```sh
echo '{"configuration":{"url":"https://acme.logicmonitor.com","device_id":"12345","property_name":"Env","property_value":"prod","token":"<BEARER_TOKEN>"}}' | python bin/logicmonitor_update.py --execute
```

Note: On Windows/PowerShell you may need to use appropriate quoting and piping.

## Troubleshooting
- Check Splunk's logs for action execution details.
- The script logs INFO/ERROR messages to stderr; ensure the token and URL are correct and reachable.

## Contributing
If you'd like to add features or fix issues, fork the repo and submit a pull request. Keep changes focused and add tests where appropriate.

