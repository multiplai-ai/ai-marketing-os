---
name: jira-marketing
description: Coordinate marketing launch visibility through weekly triage, launch tickets, and category-management review rituals.
---

Resolve `{jira_project_key}`, `{jira_dashboard_url}`, `{launch_epic_template_url}`
and required approvers/watchers from current consumer configuration. Verify the
project, template and workflow statuses before making authorized changes. Never
reuse another team's issue key or infer a recipient from a template.

# Launch Visibility SOP — Category Management Team

## Purpose
Ensure no Product launches that need Category Mgmt support are surprises. This SOP covers the weekly triage ritual, ticket creation process, and team rituals.

---

## Weekly Rituals Overview

| Ritual | When | Duration | Owner |
|--------|------|----------|-------|
| Launch Triage | Monday AM | 15 min | owner (or delegate) |
| Readiness Check | Thursday AM | 10 min | owner (or delegate) |
| Monthly Retro | First Monday of month | 30 min | Team |

---

## Ritual 1: Monday Launch Triage

**When:** Monday, first thing (before standup)
**Duration:** 15 minutes
**Owner:** owner (can delegate to team member)

### Step-by-Step

1. **Open the Dashboard**
   - Go to: `Category Management — Launch Visibility` dashboard
   - Or direct link: {jira_dashboard_url} (create dashboard with filters below)

2. **Review "Product Epics — In Progress"**

   For each item, ask:
   - [ ] Does this need training/enablement?
   - [ ] Does this need measurement setup?
   - [ ] Does this need email/marketing support?
   - [ ] Does this need post-launch analysis?

   **If any answer is YES:**
   → Create Launch Support ticket (see process below)

   **If all answers are NO:**
   → Add "CM-Watching" label to the Product ticket (optional, for tracking)
   → Skip to next item

3. **Review "Product Work — Recently Updated"**

   Quick scan for anything that:
   - Looks like a launch but wasn't in the first filter
   - Is moving fast and might need support soon
   - Was relabeled or changed scope recently

4. **Review "Launch Support — Active"**

   Quick check:
   - Any blocked tickets?
   - Any launch dates that moved?
   - Surface blockers for team sync

5. **Done**
   - Note any items needing discussion in team sync
   - Close dashboard

---

## Ritual 2: Thursday Readiness Check

**When:** Thursday morning
**Duration:** 10 minutes
**Owner:** owner (or delegate)

### Step-by-Step

1. **Open Launch Support — Active filter**

2. **Filter to launches in next 2 weeks**
   - Add quick filter: `duedate <= 14d`

3. **For each launch:**
   - [ ] Are all subtasks on track?
   - [ ] Is marketing support ready (if needed)?
   - [ ] Any blockers to escalate?

4. **Escalate anything red**
   - Ping owner in Slack
   - Add to Friday standup if needed

---

## Creating a Launch Support Ticket

### When to Create
- Triage identified a Product launch needing CM support
- Product PM requested support directly
- Any launch that needs training, measurement, marketing, or analysis

### Step-by-Step

1. **Clone the Template Epic**
   - Open template: the consumer-configured `{launch_epic_template_url}`
   - Click **Actions → Clone** (or create new Epic manually)
   - Rename: `Launch Support: [Product Feature Name]`
   - Example: `Launch Support: Video Series Autoplay`

2. **Fill Required Fields**

   | Field | Value |
   |-------|-------|
   | Summary | `Launch Support: [Feature Name]` |
   | Assignee | Category Manager who will own this (Driver) |
   | Due Date | Product's target launch date |
   | Labels | `launch-support` |

3. **Link to Product's Epic**
   - Click "Link" → "is blocked by" or "relates to"
   - Search for Product's epic/ticket
   - This creates bi-directional visibility

4. **Add Standard Subtasks**

   Create these subtasks under the epic:

   | Subtask | Assignee | Due Date Offset |
   |---------|----------|-----------------|
   | Pre-launch training/enablement | TBD | Launch - 1 week |
   | Measurement setup | TBD | Launch - 1 week |
   | Email/marketing support | TBD | Launch - 2 weeks |
   | Post-launch tracking | TBD | Launch + 1 week |
   | Rollout/expansion planning | TBD | Launch + 2 weeks |

   Note: Remove subtasks that don't apply to this launch.

5. **Add Watchers**
   - Add owner (Approver)
   - Add Product PM (Informed)
   - Add the configured executive watcher for major launches, if the consumer's policy requires it

6. **Transition to "In Prep"**
   - Move epic from Triaged → In Prep

### Timeline-Based Scope

**4+ weeks out:**
- All subtasks feasible
- Standard process

**2-4 weeks out + needs marketing:**
- Add comment: "Compressed timeline — [X] may not be feasible"
- Discuss scope with Product PM
- Document agreed scope in epic description

**<2 weeks out:**
- Add comment: "Emergency timeline — limited support possible"
- Sync with Product PM same day
- Only commit to what's realistic
- Document tradeoffs explicitly

---

## Workflow States

```
Triaged → In Prep → Ready for Launch → Post-Launch → Done
```

| State | Meaning | Entry Criteria |
|-------|---------|----------------|
| Triaged | Ticket created, not yet started | Just created from triage |
| In Prep | Actively working on pre-launch items | Subtasks assigned, work in progress |
| Ready for Launch | Pre-launch work complete | All pre-launch subtasks done |
| Post-Launch | Launch happened, doing post-work | Launch date passed |
| Done | All work complete | All subtasks done, retro complete |

---

## Triage Criteria Reference

**Does this need CM support?** Yes if ANY of these apply:

| Criterion | Examples |
|-----------|----------|
| Training/enablement | New feature physicians need to learn; workflow change |
| Measurement setup | New metrics to track; dashboard updates needed |
| Marketing support | Launch email; in-app announcement; specialty targeting |
| Post-launch analysis | Success metrics review; iteration planning |

**When in doubt:** Create the ticket. Easier to close than to catch up.

---

## Monthly Retro Agenda

**When:** First Monday of month, 30 min
**Attendees:** CM team

### Questions to Answer

1. **False negatives:** Were there any surprise launches we should have caught?
   - If yes → What JQL change would have caught it?
   - Update `Projects/jira-boards-and-jql.md`

2. **False positives:** Did we create tickets for things that didn't need support?
   - If yes → Should we adjust triage criteria?
   - Update this SOP

3. **Process friction:** What's annoying or slow about the current process?
   - Identify improvements
   - Assign owner to implement

4. **Capacity check:** Are we able to support the launch volume?
   - If no → Escalate to owner
   - Consider timeline triage adjustments

---

## Quick Reference Card

### Monday Triage (15 min)
1. Open dashboard
2. Review Product launches → Create tickets for items needing support
3. Review recently updated → Catch unlabeled work
4. Review team work → Note blockers

### Creating Launch Support Ticket
1. Epic in `{jira_project_key}`: `Launch Support: [Name]`
2. Link to Product's epic
3. Add 5 standard subtasks
4. Add watchers (owner, PM)
5. Transition to In Prep

### Compressed Timeline?
- 4+ weeks = full support
- 2-4 weeks = discuss scope
- <2 weeks = emergency mode

---

## References

- JQL queries: `Projects/jira-boards-and-jql.md`
- Design rationale: `Projects/jira-design-rationale.md`
