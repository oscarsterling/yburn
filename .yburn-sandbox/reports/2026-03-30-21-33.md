# Conversion Report

_Generated: 2026-03-30T21:33_

## AUDIT SUMMARY
- Total jobs: 130
- Mechanical: 85
- Reasoning: 14
- Unsure: 31
- Convertible pending: 25

## CONVERTED
- **OAuth Token Health Check**
  before: LLM cron
  after: `python3 /Users/oscarsterling/Projects/yburn/.yburn-sandbox/scripts/oauth-token-health-check.py`
  schedule: `0 6,18 * * * (America/New_York)` unchanged
- **Stuck Session Cleanup**
  before: LLM cron
  after: `python3 /Users/oscarsterling/Projects/yburn/.yburn-sandbox/scripts/stuck-session-cleanup.py`
  schedule: `0 */2 * * * (America/New_York)` unchanged
- **db-maintenance-weekly**
  before: LLM cron
  after: `python3 /Users/oscarsterling/Projects/yburn/.yburn-sandbox/scripts/db-maintenance-weekly.py`
  schedule: `0 3 * * 0 (America/New_York)` unchanged
- **DB Maintenance - Daily Full**
  before: LLM cron
  after: `python3 /Users/oscarsterling/Projects/yburn/.yburn-sandbox/scripts/db-maintenance---daily-full.py`
  schedule: `0 3 * * * (America/New_York)` unchanged
- **DB Maintenance - Midday Guard**
  before: LLM cron
  after: `python3 /Users/oscarsterling/Projects/yburn/.yburn-sandbox/scripts/db-maintenance---midday-guard.py`
  schedule: `0 15 * * * (America/New_York)` unchanged
- **GitHub PAT Expiry Reminder**
  before: LLM cron
  after: `python3 /Users/oscarsterling/Projects/yburn/.yburn-sandbox/scripts/github-pat-expiry-reminder.py`
  schedule: `0 2 1 * * (America/New_York)` unchanged
- **[yburn] Daily Cron Health Report**
  before: LLM cron
  after: `python3 /Users/oscarsterling/Projects/yburn/.yburn-sandbox/scripts/-yburn--daily-cron-health-report.py`
  schedule: `0 22 * * * (America/New_York)` unchanged
- **[yburn] Nightly Backup + Git Commit**
  before: LLM cron
  after: `python3 /Users/oscarsterling/Projects/yburn/.yburn-sandbox/scripts/-yburn--nightly-backup---git-commit.py`
  schedule: `45 22 * * * (America/New_York)` unchanged
- **[yburn] Nightly System Diagnostic**
  before: LLM cron
  after: `python3 /Users/oscarsterling/Projects/yburn/.yburn-sandbox/scripts/-yburn--nightly-system-diagnostic.py`
  schedule: `0 4 * * * (America/New_York)` unchanged
- **[yburn] Weekly Cron Health Audit**
  before: LLM cron
  after: `python3 /Users/oscarsterling/Projects/yburn/.yburn-sandbox/scripts/-yburn--weekly-cron-health-audit.py`
  schedule: `30 4 * * 0 (America/New_York)` unchanged

## SKIPPED
- **subagent-transcript-cleanup**: no template match, needs Phase 2 custom template
- **eod-summary**: no template match, needs Phase 2 custom template
- **OpenClaw Update Check**: no template match, needs Phase 2 custom template
- **Personal Daily Brief**: no template match, needs Phase 2 custom template
- **Work Daily Brief**: no template match, needs Phase 2 custom template
- **Weekly Config Backup**: no template match, needs Phase 2 custom template
- **Pam Kroger Verify + Notify (Job 3)**: no template match, needs Phase 2 custom template
- **Nightly Session Reset**: no template match, needs Phase 2 custom template
- **Board Meeting Debrief for Jason**: no template match, needs Phase 2 custom template
- **Board Meeting Prep**: no template match, needs Phase 2 custom template
- **Content Pipeline: Publish**: no template match, needs Phase 2 custom template
- **Action Item Safety Net**: no template match, needs Phase 2 custom template
- **Post-Board Meeting Follow-Up**: no template match, needs Phase 2 custom template
- **Pre-Dream Git Snapshot**: no template match, needs Phase 2 custom template
- **Dream Cycle**: no template match, needs Phase 2 custom template
- **Forge: Validate Dream Cycle Spec + Pre-Dream Flush**: no template match, needs Phase 2 custom template
- **Forge: Fix Dream metrics.json fields**: no template match, needs Phase 2 custom template
- **db-size-monitor-daily**: no template match, needs Phase 2 custom template
- **Forge: Completion Callback in Sub-Agent Prompts**: no template match, needs Phase 2 custom template
- **Health Report Reviewer (Oscar QA)**: no template match, needs Phase 2 custom template
- **System State Compiler**: no template match, needs Phase 2 custom template
- **Social Media - Set Opus Model**: no template match, needs Phase 2 custom template
- **Board Meeting Watchdog**: no template match, needs Phase 2 custom template
- **Oscar X Morning Session**: no template match, needs Phase 2 custom template
- **Oscar X Midday Session**: no template match, needs Phase 2 custom template
- **Oscar X Afternoon Session**: no template match, needs Phase 2 custom template
- **Radar Dream Cycle**: no template match, needs Phase 2 custom template
- **Guru Dream Cycle**: no template match, needs Phase 2 custom template
- **Ink Dream Cycle**: no template match, needs Phase 2 custom template
- **Lens Dream Cycle**: no template match, needs Phase 2 custom template
- **Forge Dream Cycle**: no template match, needs Phase 2 custom template
- **Shield Dream Cycle**: no template match, needs Phase 2 custom template
- **X Reply Monitor (Jason)**: no template match, needs Phase 2 custom template
- **Board Meeting Process Review with Jason**: no template match, needs Phase 2 custom template
- **Clelp Dead Link Sweep (Batch 500)**: no template match, needs Phase 2 custom template
- **GA4 Content Performance Feedback**: no template match, needs Phase 2 custom template
- **Session Model Overrides**: no template match, needs Phase 2 custom template
- **Build Archive INDEX.md**: no template match, needs Phase 2 custom template
- **YouTube Intelligence Scrape**: no template match, needs Phase 2 custom template
- **Weekly Stat Refresh**: no template match, needs Phase 2 custom template
- **Supermemory ASMR Release Watch**: no template match, needs Phase 2 custom template
- **Radar: Weekly Buzz Scout for Clelp**: no template match, needs Phase 2 custom template
- **Deep Memory Backup**: no template match, needs Phase 2 custom template
- **X-Eyed Weekly Optimize**: no template match, needs Phase 2 custom template
- **Session Journal (Raw Backup)**: no template match, needs Phase 2 custom template
- **Clelp Weekly URL Audit [ARCHIVED - replaced by Fire+Report split]**: no template match, needs Phase 2 custom template
- **YouTube Intel Router**: no template match, needs Phase 2 custom template
- **[yburn] Post-Dream Re-index + Rollback Guard**: no template match, needs Phase 2 custom template
- **Clelp URL Audit - Fire**: no template match, needs Phase 2 custom template
- **X-Eyed Monitor**: no template match, needs Phase 2 custom template

## AMBIGUOUS
- **heartbeat-review**
  signals: reasoning:review(+1), mechanical:heartbeat(+2)
  payload: `REMINDER: Monthly Heartbeat Review. It's been 30 days - time to review HEARTBEAT.md together. Questi`
- **credential-rotation-reminder**
  signals: mechanical:rotate(+2)
  payload: `REMINDER: 90-Day Credential Rotation. It's been 90 days since we set up your API keys. Time to rotat`
- **weekly-consolidation**
  signals: reasoning:brief(+1), reasoning:synthesize(+2), mechanical:memory(+1), mechanical:archive(+2), reasoning:insights(+2), mechanical:send(+1)
  payload: `WEEKLY CONSOLIDATION: Review the past week's memory files (memory/daily/2026-*.md), braindump items,`
- **Pam Kroger Receipts & Profile Update**
  signals: mechanical:execute(+1), mechanical:job(+1), reasoning:update(+1), heuristic:opus_model(+1)
  payload: `Read family/pam/kroger/README.md carefully. Then execute Job 1 exactly as specified, following the p`
- **Outlook Playbook Weekly Review**
  signals: reasoning:brief(+1), mechanical:memory(+1), mechanical:trigger(+1), reasoning:morning(+1), mechanical:send(+1), reasoning:weekly(+1)
  payload: `It's Saturday morning - time for the weekly Outlook Playbook review. Read memory/work/email-rules.md`
- **Radar Morning Scout**
  signals: reasoning:prioritize(+1), mechanical:heartbeat(+2), reasoning:content(+1), mechanical:memory(+1), mechanical:status(+2), mechanical:execute(+1)
  payload: `You are Radar, Research Analyst for the Oscar Sterling Agency.

Read your files:
1. agents/radar/SOU`
- **Radar Afternoon Check (Mon/Wed/Fri)**
  signals: reasoning:brief(+1), mechanical:check(+2), mechanical:memory(+1), mechanical:execute(+1), reasoning:write(+2), reasoning:morning(+1)
  payload: `You are Radar, Research Analyst for the Oscar Sterling Agency.

Read your files:
1. agents/radar/SOU`
- **Radar Weekly Deep Dive**
  signals: reasoning:prioritize(+1), reasoning:weekly(+1), mechanical:memory(+1), reasoning:update(+1), mechanical:rotate(+2), reasoning:research(+2)
  payload: `You are Radar, Research Analyst for the Oscar Sterling Agency.

Read your files:
1. agents/radar/SOU`
- **Ink Self-Improvement**
  signals: mechanical:verify(+2), reasoning:learning(+1), reasoning:content(+1), mechanical:memory(+1), reasoning:trends(+1), mechanical:send(+1)
  payload: `You are Ink, Content Writer for the Oscar Sterling Agency.

Read agents/ink/SOUL.md and agents/ink/M`
- **Forge Self-Improvement**
  signals: reasoning:audit(+1), mechanical:verify(+2), reasoning:weekly(+1), reasoning:learning(+1), reasoning:content(+1), mechanical:memory(+1)
  payload: `You are Forge, Lead Engineer for the Oscar Sterling Agency.

Read agents/forge/SOUL.md and agents/fo`
- **Shield Mid-Week Vulnerability Check**
  signals: reasoning:brief(+1), reasoning:audit(+1), mechanical:check(+2), mechanical:memory(+1), reasoning:write(+2), mechanical:run(+1)
  payload: `You are Shield, Security Analyst for the Oscar Sterling Agency. Run a quick mid-week vulnerability c`
- **OSA Playbook Weekly Update**
  signals: reasoning:weekly(+1), reasoning:content(+1), mechanical:memory(+1), mechanical:process(+1), mechanical:copy(+1), reasoning:update(+1)
  payload: `You are Oscar, Chief of Staff. It's time for the weekly OSA Playbook update.

Read these files:
1. p`
- **Pam Kroger Coupon Clipping (Job 2)**
  signals: mechanical:execute(+1), mechanical:job(+1), heuristic:opus_model(+1)
  payload: `Read family/pam/kroger/README.md carefully. Then execute Job 2 exactly as specified, following the p`
- **GitHub PAT Rotation Reminder**
  signals: reasoning:update(+1)
  payload: `⚠️ REMINDER: Classic GitHub PAT (OscarSterling) expires May 25, 2026. You have about 2 weeks left. R`
- **Quarterly Key Rotation Audit**
  signals: reasoning:audit(+1), mechanical:check(+2), mechanical:rotate(+2), reasoning:review(+1)
  payload: `🔑 QUARTERLY KEY ROTATION AUDIT: Review all API keys in Keychain. Even if they don't expire, rotating`
- **Guru Sync Review**
  signals: mechanical:sync(+2), mechanical:flag(+1), mechanical:report(+1), reasoning:content(+1), mechanical:memory(+1), reasoning:summarize(+1)
  payload: `STEP 1 - STATE VALIDATION (DO THIS BEFORE GENERATING ANY OUTPUT):
Read memory/state/system-state.md.`
- **Content Pipeline: QA Review**
  signals: reasoning:publish(+1), reasoning:blog(+1), reasoning:draft(+2), reasoning:content(+1), mechanical:memory(+1), mechanical:send(+1)
  payload: `You are Oscar, Chief of Staff, doing QA review with Shield's perspective.

HONESTY PROTOCOL: You are`
- **LLM Fallback Security Review**
  signals: mechanical:send(+1), reasoning:review(+1)
  payload: `Reminder for Jason: Review the model fallback configuration. Current chain has gpt-4o as fallback #3`
- **Daily Clelp AI Raters**
  signals: mechanical:send(+1), reasoning:review(+1), reasoning:write(+2), mechanical:count(+1), reasoning:generate(+2), mechanical:check(+2)
  payload: `You are Oscar, Chief of Staff. Your job today: spin up 3-4 AI rating agents to leave genuine, honest`
- **Forge: Dream Briefing Overdue Items**
  signals: mechanical:memory(+1), mechanical:status(+2), reasoning:write(+2), reasoning:update(+1)
  payload: `You are Forge. Read projects/memory-redesign/dream-cycle-spec.md Step 6. Add a new section to the se`
- **Muse Self-Improvement (Part 2 - Memory Update)**
  signals: mechanical:verify(+2), reasoning:learning(+1), reasoning:content(+1), mechanical:memory(+1), mechanical:send(+1), reasoning:update(+1)
  payload: `You are Muse. Consolidate your latest research into agents/muse/MEMORY.md.

## CIRCUIT BREAKER RULES`
- **Weekly X Profile Check**
  signals: mechanical:check(+2), reasoning:tweet(+1), reasoning:engagement(+1), mechanical:send(+1), reasoning:weekly(+1), reasoning:reflect(+2)
  payload: `Send Jason a quick reminder via Telegram (target: 8302078563, channel: telegram):

'Weekly X profile`
- **Muse Dream Cycle**
  signals: mechanical:archive(+2), reasoning:strategy(+2), mechanical:count(+1), reasoning:creative(+2), reasoning:content(+1), mechanical:memory(+1)
  payload: `You are running a Dream Cycle for Muse (Creative Strategist).

STEP 1: Read agents/muse/MEMORY.md to`
- **Oscar Self-Audit - Pattern Mining**
  signals: reasoning:audit(+1), mechanical:count(+1), mechanical:flag(+1), mechanical:memory(+1), mechanical:send(+1), mechanical:job(+1)
  payload: `You are Oscar's Self-Audit system (Layer 2: Corrections Pattern Mining).

Your job: find CLUSTERS of`
- **Oscar Self-Audit - External Mirror**
  signals: reasoning:audit(+1), reasoning:propose(+2), mechanical:push(+1), mechanical:script(+2), mechanical:report(+1), mechanical:memory(+1)
  payload: `Run the self-audit external mirror script. Execute: python3 scripts/self-audit-mirror.py --days 7

A`
- **Reminder: Clelp Role Landing Pages**
  signals: mechanical:memory(+1), mechanical:copy(+1)
  payload: `⏰ REMINDER: Clelp role landing pages (/for/developer, /for/data-scientist, etc.) were deferred on Ma`
- **Reminder: TAAFT Free Submission Thread**
  signals: mechanical:check(+2), reasoning:decide(+2), mechanical:list(+1)
  payload: `Reminder: Check TAAFT's monthly free submission thread on X (@theresanaiforit). They pick one tool p`
- **Reminder: Jason Personal X Origin Story Post**
  signals: mechanical:check(+2)
  payload: `REMINDER: Revisit Jason's personal X origin story post - 10+ years on Twitter with <300 followers, n`
- **Reminder: Deep Memory assessment with Jason**
  signals: reasoning:evaluate(+2), mechanical:check(+2), mechanical:memory(+1), reasoning:decide(+2), mechanical:count(+1), mechanical:run(+1)
  payload: `Reminder: Deep Memory assessment with Jason. It's been ~2 weeks since ingestion was enabled (Mar 26)`
- **Newsletter Cron Review - How'd it go?**
  signals: mechanical:report(+1), mechanical:validate(+2), reasoning:draft(+2), mechanical:memory(+1), reasoning:debrief(+1), reasoning:newsletter(+1)
  payload: `The new model-bounced newsletter cron fired at 3 AM this morning. Jason wants a full debrief. Check:`
- **Reasoning Loop Writeup Reminder**
  signals: mechanical:memory(+1), reasoning:review(+1), reasoning:draft(+2)
  payload: `⏰ REMINDER: Jason wants to work on the Reasoning Loop writeup tomorrow (Thursday). The Muse draft is`

## KEPT
- Guru Daily Research
- Radar Self-Improvement
- Muse Self-Improvement (Part 1 - Research)
- Lens Self-Improvement
- Oscar Self-Improvement
- Oscar + Guru Daily Sync
- Content Pipeline: Radar Research
- Content Pipeline: Muse Strategy
- Content Pipeline: Ink Draft
- Oscar X Post Draft
- Pattern Review + Ratchet
- Weekly Newsletter Reminder
- Reminder: ASMR Blog Post for Next Tuesday
- Reminder: ASMR Blog for Next Tuesday

## TOKEN SAVINGS ESTIMATE
- Sessions eliminated per day: 19.32
- Sessions eliminated per week: 135.23
- Sessions eliminated per month: 579.57
- Speed improvement: about 30s -> <1s per converted run
