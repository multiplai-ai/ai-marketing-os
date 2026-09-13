# Legacy Slack Front-Door Reference

Use this reference only when the consumer's verified runtime supports these
legacy commands. Resolve `{profile_id}`, `{profile_root}`, `{hermes_binary}`,
`{service_name}`, `{slack_app_name}` and `{slack_app_description}` from the
approved consumer configuration. Verify the installed CLI and service names;
never execute unresolved placeholders. No connection or profile is presumed live.

## Operator is rejected or ignored

Inspect only non-secret configuration keys and scoped service/log evidence:

```bash
PROFILE="{profile_id}"
HOME_DIR="{profile_root}"

grep -E '^(SLACK_ALLOWED_USERS|SLACK_HOME_CHANNEL|SLACK_FREE_RESPONSE_CHANNELS|SLACK_REQUIRE_MENTION)=' "$HOME_DIR/.env"
systemctl status "{service_name}" --no-pager -l | sed -n '1,25p'
grep -E 'Unauthorized user|inbound message|response ready' "$HOME_DIR/logs/gateway.log" | tail -40
```

Do not copy the output into a durable receipt until user IDs, channel IDs, and
message text are minimized or redacted. A changed `.env` does not affect an
already-running gateway. Request approval before changing the allowlist or
restarting the scoped service.

After an approved change, ask the authorized operator to send one short test in
the configured home/free-response channel or mention the bot in another allowed
channel. Private-channel discovery may also require `groups:read`,
`groups:history`, and the `message.groups` event on the Slack app.

## Slack reports `account_inactive` or the app disappeared

1. Inspect the scoped profile without printing token values:

   ```bash
   PROFILE="{profile_id}"
   HOME_DIR="{profile_root}"

   grep -E '^(SLACK_ALLOWED_USERS|SLACK_HOME_CHANNEL|SLACK_FREE_RESPONSE_CHANNELS|SLACK_REQUIRE_MENTION)=' "$HOME_DIR/.env"
   systemctl status "{service_name}" --no-pager -l | sed -n '1,25p'
   grep -E 'account_inactive|Authenticated as|Slack gateway started|failed to list Slack channels' "$HOME_DIR/logs/gateway.log" | tail -60
   ```

2. If approved, generate a profile-specific Slack manifest from the live Hermes
   install. Use the affected profile and approved display metadata; do not reuse
   another profile's manifest.

   ```bash
   {hermes_binary} -p {profile_id} slack manifest \
     --name "{slack_app_name}" \
     --description "{slack_app_description}" \
     --write {profile_root}/slack-manifest.json
   ```

3. Slack app manifest changes and app installation/reinstallation are external
   access-control actions. Obtain explicit approval before saving or installing.
   A bot OAuth token and an app-level Socket Mode token are different credential
   classes; replace only the invalid class.

4. Before an approved credential edit, create the approved scoped backup. Edit
   only the named token aliases, then restart only the affected service.

5. Verify that the bot authentication check succeeds and that sanitized logs
   show authentication, Socket Mode connection, and channel-directory creation.
   Run one explicitly approved Slack smoke test and record its receipt without
   message content.

## Receipt

Record:

- timestamp and operator
- profile and scoped service
- symptom and sanitized evidence category
- approvals received
- files, aliases, Slack settings, or services changed
- backup and rollback location by alias, never secret value
- authentication, Socket Mode, channel, allowlist, and smoke-test result
- confirmation that other profiles and external actions were unchanged
