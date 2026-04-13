# Linux Memory Management & CPU Troubleshooting

> **Context:** Days 3–4 of TSE prep. Goal: diagnose customer memory/CPU problems using the right tools and explain findings clearly. Not kernel internals — diagnostic depth only.

---

## Part 1: Virtual vs Physical Memory — What You Need to Know

> **Virtual Memory** Virtual memory is a memory management technique used by operating systems to give the appearance of a large, continuous block of memory to applications, even if the physical memory (RAM) is limited and not necessarily allocated in contiguous manner. The main idea is to divide the process in pages, use disk space to move out the pages if space in main memory is required and bring back the pages when needed.

The OS breaks process memory into small chunks (pages), moves unused ones to disk when RAM is full, and pulls them back when needed — that's paging, and when it happens excessively it's called thrashing

> **Physical Memory** is the actual RAM installed on the machine. It's finite, shared across all processes, and is what truly runs out when you hit memory pressure.

> **Paging** is how the OS moves data between RAM and disk in fixed-size chunks (pages, typically 4 KB). When RAM is full, the OS pages out inactive data to disk (swap) to free up room — and pages it back in when needed. Active paging to/from disk is slow and is what causes performance degradation.

### Why VSZ ≠ RSS

Every process gets its own **virtual address space** — it *thinks* it has a huge private chunk of memory. But only the parts it actually uses get backed by real **physical RAM**.

| Metric | What it means | Analogy |
|--------|--------------|---------|
| **VSZ** (Virtual Size) | Total virtual address space claimed | Reserving 10 hotel rooms |
| **RSS** (Resident Set Size) | Physical RAM actually being used right now | Actually sleeping in 2 rooms |

**TSE Interview question:** *"A customer says their Java app is using 10 GB of memory. Is it a leak?"*
→ First ask: 10 GB of what? VSZ or RSS? If VSZ is 10 GB but RSS is 2 GB, the JVM just reserved a big heap. Totally normal. If RSS is 10 GB and growing, *that's* a potential leak.

### Why This Matters for Troubleshooting

- A process can *allocate* lots of virtual memory but only *use* a fraction of physical RAM. **This is normal.**
- Linux is lazy — it doesn't give a process real RAM until it actually writes to memory. This is why VSZ is always larger than RSS.
- When physical RAM fills up and there's nothing left to reclaim → **OOM Killer** wakes up (covered in Part 4).

---

## Part 2: Buffers, Cache, and Why "Free" Memory is Misleading

> **Cache (Page Cache)** is RAM that the OS uses to keep recently-read file contents in memory so the next read is fast (RAM speed instead of disk speed). It's reclaimable — if a process needs memory, the OS drops the cache instantly.

> **Buffers** are RAM used for in-flight disk I/O — data that's been written by a process but not yet flushed to the physical disk. Like cache, this memory can be reclaimed when needed.

Buffers are RAM holding data that's been written by a process but not yet flushed to disk. It's how Linux avoids making processes wait for slow disk I/O — and it's reclaimable, so it doesn't reduce available memory

### Reading `free -h` Correctly

```bash
$ free -h
              total    used    free    shared  buff/cache   available
Mem:          16Gi     6Gi     1Gi     256Mi   9Gi          9Gi
Swap:         4Gi      0Bi     4Gi
```

**The trap:** A customer says *"My server only has 1 GB free! We need more RAM!"*

**The truth:** They have **9 GB available**. Here's why:

| Column | What it really means |
|--------|---------------------|
| **free** | Completely unused RAM. Kernel tries to keep this LOW (unused RAM is wasted RAM) |
| **buff/cache** | RAM used for disk I/O buffers and file cache — **reclaimable on demand** |
| **available** | Free + reclaimable cache = what's actually available for new processes. **This is the number that matters.** |

### Buffers vs Cache — What's the Difference?

| | Buffers | Cache (Page Cache) |
|--|---------|-------------------|
| **What** | Metadata and raw block device I/O | File contents read from disk |
| **Example** | Directory entries, inode info | The actual bytes of `/var/log/syslog` you just read |
| **When used** | Writing to disk, filesystem journal | Reading files, memory-mapped files |
| **Reclaimable?** | Yes (dirty buffers flushed first) | Yes (clean cache dropped instantly) |

**TSE takeaway:** High buff/cache is GOOD. It means the OS is using idle RAM to speed up disk access. It will be released when a real process needs it.

### `/proc/meminfo` — When You Need More Detail Than `free -h`

```bash
# The key lines to look at:
grep -E 'MemTotal|MemAvailable|MemFree|Buffers|^Cached|SwapTotal|SwapFree|Dirty' /proc/meminfo
```

| Field | What it tells you |
|-------|-------------------|
| **MemAvailable** | The real available memory (free + reclaimable). **This is the number that matters.** |
| **MemFree** | Completely unused RAM. Low is FINE — the kernel uses idle RAM for cache. |
| **Buffers + Cached** | RAM used for disk speedup. Reclaimable when processes need it. |
| **Dirty** | Data waiting to be written to disk. Large = might stall if disk is slow. |
| **SwapFree** | How much swap space is left. If shrinking, system is under pressure. |

---

## Part 3: Swap — The Safety Net That Can Become a Trap

> **Swap** is a dedicated area on disk (a partition or file) that acts as overflow for RAM. When physical memory is full, the OS moves inactive pages from RAM to swap to make room. Reading from swap is orders of magnitude slower than RAM, so heavy swap usage = severe performance hit.

> **Thrashing** is when the system spends more time moving pages between RAM and swap than doing actual work. It's the worst-case memory scenario — the server becomes effectively unresponsive.

### What Swap Is

Swap is disk space used as overflow when physical RAM is full. The kernel moves inactive pages from RAM to swap (called **swapping out** or **paging out**) to make room.

```
                When RAM is full:
┌─────────┐     ┌───────────────┐     ┌──────────┐
│ Process  │ ──→ │ Physical RAM  │ ──→ │ Swap     │
│ needs    │     │ (full)        │     │ (on disk)│
│ memory   │     │ Inactive page │ ──→ │ Page     │
│          │     │ evicted       │     │ stored   │
└─────────┘     └───────────────┘     └──────────┘
```

### When Swap Helps vs. Hurts

| Scenario | Swap behavior | Impact |
|----------|--------------|--------|
| Occasional spike | Rarely-used pages swapped out | ✅ System survives the spike |
| Steady state | Small amount of swap used, stable | ✅ Fine — inactive stuff is on disk |
| Thrashing | Pages constantly swapped in/out | ❌ System grinds to a halt |

### Detecting Swap Problems

```bash
# Quick check: is swap being used?
free -h
# Look at Swap row. If used > 0 and growing, investigate.

# Real-time monitoring: are we actively swapping?
vmstat 1 5
#   si = swap in (pages read FROM disk back to RAM)
#   so = swap out (pages written FROM RAM to disk)
# If si/so are consistently non-zero → active swapping → performance problem

#  Memory problem (thrashing):
#  r  b  swpd    free  buff  cache  si    so   ...  id  wa
#  5  8  4096000 50000 1000  100000 5000  8000 ...   5  60
#                 ↑ free very low   ↑ active swapping  ↑ I/O wait high

# # CPU problem:
#  r  b  ...  us  sy  id  wa
# 12  0  ...  85  10   5   0    ← r=12 means 12 processes queued, us=85%

# # I/O problem:
#  r  b  ...  us  sy  id  wa
#  2  8  ...   5   2  20  73   ← b=8 blocked on I/O, wa=73%
# Which processes are using swap? (check top sorted by memory)
top  # then press 'M' to sort by memory — heaviest users are likely swapping
```

### The Swappiness Knob

```bash
cat /proc/sys/vm/swappiness
# Default: 60 (range 0-100)
# 0  = Kernel avoids swapping as much as possible (prefers dropping cache)
# 60 = Default balance
# 100 = Kernel aggressively swaps

# For databases (Redis, MySQL): set to 1-10
# Reason: databases manage their own caching, swapping their data to disk defeats the purpose
sysctl vm.swappiness=10  # Temporary
```

**TSE Interview question:** *"Should we disable swap entirely?"*
→ Risky. Without swap, the only option when RAM is full is the OOM Killer immediately terminating processes. Swap gives you a buffer — a slow but survivable degradation instead of sudden process death. Exception: some container platforms (Kubernetes) require swap off for predictable scheduling.

---

## Part 4: The OOM Killer — Linux's Last Resort

> **OOM Killer (Out-Of-Memory Killer)** is a kernel mechanism that activates when the system has completely exhausted both RAM and swap. It picks a process to kill (using a scoring system based mainly on memory usage) and sends it SIGKILL to free up memory and keep the system alive. It's a last resort — if it fires, the system was already in serious trouble.

### When Does It Trigger?

```
Memory request → Check available RAM → Check swap → Both exhausted
                                                          ↓
                                                   OOM Killer activates
                                                          ↓
                                                   Picks a victim
                                                          ↓
                                                   Sends SIGKILL (9)
                                                          ↓
                                                   Process is dead
```

The OOM Killer fires when:
1. A process requests memory
2. Physical RAM is exhausted
3. Swap is exhausted (or swap is disabled)
4. No reclaimable cache is left

### How It Picks a Victim

The kernel assigns each process an **oom_score** (0–1000). The process with the **highest score gets killed**.

**What drives the score up:** uses a lot of memory (the biggest factor).
**What drives it down:** root-owned, or admin set `oom_score_adj` to a negative value.

```bash
# Check a process's OOM score
cat /proc/<pid>/oom_score        # Current score (0-1000)
cat /proc/<pid>/oom_score_adj    # Admin adjustment (-1000 to 1000)
```

### Protecting Critical Processes

```bash
# Make a process immune to OOM killer (use sparingly!)
echo -1000 > /proc/<pid>/oom_score_adj

# Make a process the FIRST to be killed
echo 1000 > /proc/<pid>/oom_score_adj

# Typical production strategy:
# - Protect: database, init system, SSH daemon
# - Sacrifice: worker processes, batch jobs, caches (they can restart)

# For systemd services, set it in the unit file:
# [Service]
# OOMScoreAdjust=-500
```

### Detecting OOM Kills

```bash
# Check kernel ring buffer (most reliable)
dmesg | grep -i "oom\|out of memory\|killed process"

# Example OOM output:
# [  123.456789] Out of memory: Killed process 5678 (java) total-vm:8192000kB,
#                anon-rss:4096000kB, file-rss:0kB, shmem-rss:0kB,
#                oom_score_adj:0

# Check system logs
journalctl -k | grep -i "oom\|killed"
grep -i "oom\|killed" /var/log/syslog /var/log/kern.log

# Check if a specific process was OOM-killed
journalctl -k --since "1 hour ago" | grep -i oom
```

### Reading an OOM Kill Log

```
Out of memory: Killed process 5678 (java)
  total-vm:8192000kB    ← Virtual memory (VSZ) — process had 8GB reserved
  anon-rss:4096000kB    ← Anonymous RSS — heap/stack actually in RAM (4GB)
  file-rss:0kB          ← File-backed pages in RAM
  oom_score_adj:0       ← No admin adjustment
```

**TSE Investigation flow after an OOM:**
1. **What was killed?** → Read the dmesg/journalctl output
2. **Why?** → Check what was consuming memory. Was it the killed process, or was it a *victim* while something else was the real hog?
3. **Pattern?** → Is this recurring? Check historical logs. Recurring OOMs = memory leak or undersized instance.
4. **Fix:** → Increase RAM, fix the leak, set memory limits (cgroups), or tune the application.

---

## Part 5: Memory Leaks vs. Healthy Memory Growth

> **Memory Leak** is when a process allocates memory but never releases it, causing RSS to grow continuously over time until the system runs out of memory. Restarting the process temporarily fixes it (RSS resets), but it starts growing again — that pattern is the signature of a leak.

### How to Tell the Difference

```
Memory Leak:                    Healthy Growth / Cache:
     ↗                               ┌──────────────
    ↗                                │  levels off
   ↗                                ↗
  ↗                                ↗
 ↗  RSS grows forever            ↗  RSS grows then stabilizes
───────── time ─→               ───────── time ─→
```

| Signal | Memory Leak | Normal Behavior |
|--------|-------------|-----------------|
| RSS over time | Steadily increases, never drops | Grows then stabilizes, or drops during GC |
| After restart | Goes back to baseline, then grows again | Stable from the start |
| `free -h` available | Decreases over days/weeks | Stable (cache is reclaimable) |
| Swap usage | Grows as RAM fills up | Stays near zero |

### Investigating a Suspected Leak

```bash
# Watch RSS of a specific process over time
watch -n 5 "ps -o pid,rss,vsz,comm -p <pid>"

# Or use pidstat (from sysstat package)
pidstat -r -p <pid> 5
# Shows: minflt/s, majflt/s, VSZ, RSS, %MEM

# Top memory consumers right now
ps aux --sort=-%mem | head -20

# Simple long-term tracking: record RSS every minute
while true; do
  echo "$(date) $(ps -o rss= -p 1715)" >> /tmp/mem_track.log
  sleep 60
done
```

**TSE approach:** You don't need to profile the code. Your job is to prove *there is* a leak (RSS grows, never drops, restarts reset it) and hand that evidence to the development team.

---

## Part 6: CPU Troubleshooting — The Full Picture

> **Load Average** is the average number of processes that are either running on CPU or waiting to run (including processes stuck waiting for disk I/O). It's a count, not a percentage. A load of 4 on a 4-core machine means every core has exactly one process — fully utilized but not overloaded.

> **I/O Wait (`wa`)** is the percentage of time the CPU spent idle because it was waiting for a disk or network operation to complete. High I/O wait with low CPU usage means the bottleneck is the disk, not the processor.

### Load Average Explained Properly

```bash
$ uptime
 14:30:00 up 45 days, load average: 4.50, 3.20, 2.10
#                                    ↑     ↑     ↑
#                                  1min  5min  15min
```

**Load = number of processes in the run queue + processes in uninterruptible I/O wait (D state)**

It is NOT a percentage. It's a count.

```
4-core machine:
  Load 4.0  → Every core has exactly 1 process. Fully utilized. Fine.
  Load 8.0  → 4 processes running + 4 waiting. Double capacity. Slowdown.
  Load 1.0  → 25% utilized. Comfortable.

Trend matters:
  1min: 4.50  5min: 3.20  15min: 2.10  → Load INCREASING (problem developing NOW)
  1min: 2.10  5min: 3.20  15min: 4.50  → Load DECREASING (problem is resolving)
```

### The Four CPU Scenarios

```bash
$ vmstat 1 5
procs -----------memory---------- ---swap-- -----io---- -system-- ------cpu-----
 r  b   swpd   free   buff  cache   si   so    bi    bo   in   cs us sy id wa st
 2  0      0 512000  64000 4096000    0    0     5    10  200  500 45 10 45  0  0
```

| Scenario | us | sy | wa | id | What it means |
|----------|----|----|----|----|---------------|
| **CPU-bound** | High (80%+) | Low-Med | Low | Low | App is doing real work. Scale up or optimize code. |
| **I/O-bound** | Low | Low | High (20%+) | Medium | CPU is idle, waiting for disk/network. Fix the I/O bottleneck. |
| **Kernel-heavy** | Low | High (30%+) | Low | Medium | Too many system calls, context switches. Threading problem or bad driver. |
| **Healthy idle** | Low | Low | Low | High (70%+) | System is fine. |

### The Crucial Question: "Load is High but CPU is Low"

This is a **classic TSE interview question:**

```
Scenario: Load average is 12 on a 4-core machine, but CPU usage shows only 20%.

Answer:
1. Load includes D-state (uninterruptible I/O) processes
2. These processes are WAITING — they're not using CPU, but they count as load
3. Check I/O wait: `vmstat 1 5` → look at 'wa' column
4. Check blocked processes: `vmstat` → 'b' column (processes in D-state)
5. Find the bottleneck: `iostat -x 1 5` → look at %util and await
6. Root cause: probably slow disk, NFS mount hanging, or database query waiting on storage
```

### Per-Core Analysis

```bash
# One core pegged at 100% while others are idle?
mpstat -P ALL 1 5
# This happens with single-threaded applications
# Total CPU looks fine (25% on a 4-core), but one core is maxed

# Find the process eating one core:
top  # then press '1' to show per-core, 'P' to sort by CPU
```

### Context Switching — When It's a Problem

```bash
# System-wide context switches
vmstat 1 5    # 'cs' column

# Per-process context switches
pidstat -w -p <pid> 1 5
# cswch/s = voluntary (process chose to wait — e.g., waiting for I/O)
# nvcswch/s = involuntary (kernel kicked it off CPU — too many threads competing)
```

**High involuntary context switches** = too many threads fighting for CPU time. This adds overhead and slows everything down. Common with over-threaded applications.

---

## Part 7: The Complete Troubleshooting Playbook

### "The Customer Says the Server is Slow" — Decision Tree

```
Step 1: What kind of slow?
├── Overall sluggish    → Check load average (uptime)
├── Specific process    → Check that process (top, pidstat)
└── Network/request     → Different problem (check networking guide)

Step 2: Is it CPU or Memory?
┌─────────────────────┐
│     uptime           │  Load high?
│     free -h          │  Available low?
│     vmstat 1 5       │  Swap active? I/O wait?
└─────────────────────┘
         │
    ┌────┴────┐
    ↓         ↓
  CPU         Memory

Step 3a: CPU Problem              Step 3b: Memory Problem
┌─────────────────┐              ┌─────────────────────┐
│ mpstat -P ALL   │              │ free -h              │
│   → per core    │              │   → available < 10%? │
│ top (press P)   │              │ vmstat 1 5           │
│   → top process │              │   → si/so non-zero?  │
│ pidstat -u 1 5  │              │ dmesg | grep oom     │
│   → per process │              │   → OOM kills?       │
│ iostat -x 1 5   │              │ ps aux --sort=-%mem  │
│   → I/O wait?   │              │   → memory hog?      │
└─────────────────┘              └─────────────────────┘
```

mstat 1 5   ← Run this, then check:

MEMORY PROBLEM?
  si/so > 0 consistently     → Active swapping (RAM pressure)
  swpd large and growing     → Swap filling up
  free very low              → Confirm with free -h "available"

I/O PROBLEM?
  wa > 20%                   → Disk is the bottleneck
  b > 0 consistently         → Processes stuck waiting for I/O
  bi/bo very high            → Heavy disk read/write

CPU PROBLEM?
  r > number of cores        → CPU overloaded
  us > 80%                   → App CPU-bound
  sy > 30%                   → Kernel overhead (threading/syscalls)
  st > 10%                   → VM being starved (noisy neighbor)

HEALTHY SYSTEM:
  r = 0-2, b = 0
  si = 0, so = 0
  wa < 5%, id > 70%
  st = 0
  

### Quick Reference: One-Liner Diagnostics

```bash
# === MEMORY ===

# "Is memory actually a problem?"
free -h          # Look at "available" column

# "What's eating memory?"
ps aux --sort=-%mem | head -10

# "Is the OOM killer firing?"
dmesg -T | grep -i "oom\|killed process" | tail -5

# "Is swap being actively used (thrashing)?"
vmstat 1 5       # Look at si/so columns — non-zero = swapping

# === CPU ===

# "Is the system overloaded?"
uptime           # Check load average vs number of cores

# "What's the CPU breakdown?"
vmstat 1 5       # us/sy/wa/id columns

# "Which process is eating CPU?"
ps aux --sort=-%cpu | head -10

# "Is one core pegged?"
mpstat -P ALL 1 3

# "Is it I/O wait, not real CPU work?"
iostat -x 1 5    # %util and await columns
# Device r/s w/s rkB/s wkB/s await %util
# sda 1.2 842.0 4.8 210000 124ms 99%
# "sda is saturated and the pattern is write-heavy. This isn't the app reading data — something is writing massively to disk. I need to find the process."
# -o = only show processes doing I/O
iotop -o

# What files is that PID writing to?
lsof -p 14821
# TID PRIO USER DISK READ DISK WRITE COMMAND
# 14821 be/4 root 0.00 B/s 198.7 M/s rsync
# rsync 14821 root 26w REG 8,1 /var/backups/db_backup_20240411.tar.gz
# Correlation found: An rsync backup job started 32 minutes ago (matches when slowness began) and is writing a 198MB/s stream to /var/backups. This is saturating sda and causing 124ms I/O wait for all other processes including the Java app.

# === COMBINED: Full picture in one shot ===
echo "=== LOAD ===" && uptime && echo "=== MEMORY ===" && free -h && echo "=== SWAP ===" && vmstat 1 3 && echo "=== TOP PROCESSES ===" && ps aux --sort=-%mem | head -5
```

---

## Part 8: Container Memory — The TSE Angle

In containers, the process has a **memory limit** set by the runtime (Docker/Kubernetes). When the process exceeds that limit, the container is killed — this looks like an OOM but happens at the container level, not the whole system.

### Key Gotcha: `free -h` Lies Inside Containers
`free -h` inside a container shows **host** memory, not the container's limit. Don't trust it.

### Detecting Container OOM Kills

```bash
# Docker: was the container OOM-killed?
docker inspect <container> | grep -i oom
# "OOMKilled": true  ← there's your answer

# Kubernetes: check pod events
kubectl describe pod <pod-name> | grep -i oom
# Reason: OOMKilled, Exit Code: 137 (128 + SIGKILL signal 9)

# On the HOST: check dmesg for OOM messages referencing the container's PID
dmesg -T | grep -i oom
```

**TSE scenario:** *"Customer's container keeps restarting."*
→ Check if it's hitting the memory limit. Exit code 137 = OOM killed. The fix is either increase the memory limit or fix the application's memory usage.

---

## Part 9: Key Interview Q&A (TSE Depth)

**Q: "Is high cache a problem?"**
A: No. Cache means the OS is efficiently using idle RAM. It's reclaimable. Only worry about `available`, not `free`.

**Q: "Should we add more RAM or more swap?"**
A: RAM. Swap is a safety net, not a solution. If the system is actively swapping, it's already in trouble. Swap prevents OOM kills but at massive performance cost.

**Q: "How do you tell the difference between a memory leak and normal memory usage?"**
A: Track RSS over time. A leak shows RSS monotonically increasing, never decreasing, eventually leading to OOM. Normal usage stabilizes. Restart the process — if RSS resets then climbs again, it's a leak.

**Q: "Load is 20 on a 4-core machine. What do you do?"**
A: First, check `vmstat` — is it CPU-bound (high `us`/`sy`) or I/O-bound (high `wa`)? If I/O-bound, CPU isn't the problem — check disk with `iostat -x`. If CPU-bound, find the offending process with `top` sorted by CPU.

**Q: "A process is in D state and can't be killed. What's happening?"**
A: D state = uninterruptible sleep, usually waiting for I/O (disk, NFS). Even `kill -9` won't work because the kernel won't interrupt the I/O operation. Fix the underlying I/O problem (hung NFS mount, failing disk). Last resort: reboot.

**Q: "The OOM killer killed the wrong process. How do you prevent this?"**
A: Use `oom_score_adj` to protect critical processes (set to -1000 for immunity). Better yet: set proper memory limits with cgroups so the memory hog is contained before the whole system is under pressure.

---

## Cheat Sheet: Commands by Scenario

| I want to... | Command |
|---|---|
| Quick memory check | `free -h` (look at "available") |
| Find memory hogs | `ps aux --sort=-%mem \| head` |
| Check for OOM kills | `dmesg -T \| grep -i oom` |
| Monitor swap activity | `vmstat 1 5` (si/so columns) |
| Check load average | `uptime` |
| CPU breakdown (us/sy/wa/id) | `vmstat 1 5` or `mpstat -P ALL 1 5` |
| Find CPU hogs | `top` then press P, or `pidstat -u 1 5` |
| Check I/O wait | `iostat -x 1 5` (%util, await) |
| Track process memory over time | `pidstat -r -p <pid> 5` |
| Check if container was OOM-killed | `docker inspect <id> \| grep -i oom` |
| Check K8s pod OOM | `kubectl describe pod <name> \| grep -i oom` |


# Step 1 — confirm RSS is growing ps -o pid,rss,vsz,comm -p $(pgrep java) # Step 2 — watch it trend every 60s while true; do echo "$(date +%H:%M) RSS=$(ps -o rss= -p $(pgrep java))kB" sleep 60 done # Step 3 — where is the memory? smaps breakdown cat /proc/$(pgrep java)/smaps | awk '/^Rss/{sum+=$2} END{print sum"kB RSS total"}' # Step 4 — is any in swap? grep VmSwap /proc/$(pgrep java)/status # Step 5 — pidstat to confirm it's not CPU thrashing pidstat -p $(pgrep java) 5 12
Say out loud
"I'm using ps and /proc to track memory because pidstat's -r flag only shows minflt/majflt — it doesn't give me absolute RSS in a readable trend. I want a number I can plot. Once I've confirmed the leak I'll use pidstat to check whether the process is also CPU-bound or purely memory."
The one-line decision rule
Use pidstat when you want to watch a process behave over time — CPU, I/O, threads, context switches.
Use /proc + ps + smem when you want to understand memory anatomy — how much, where, is it growing, is it swapped.


Inteview questions 
1
cpu
<!-- If CPU is maxed at 85%, the application is CPU-bound. I'd first identify which process (it's almost always the main app). Then:

If it's a web app or stateless service, I scale horizontally — add more instances behind a load balancer. If it's a database or single-threaded app, I either optimize the code (work with dev team) or upgrade to a larger instance. I'd also set up monitoring/alerting so we catch 70% CPU before it becomes a problem, and configure auto-scaling if the platform supports it." -->

High Load + Low CPU% (I/O problem)

<!-- "If load is high but CPU is low, I'm seeing I/O wait. I'd run vmstat to confirm wa% is high, then iostat -x to find which disk is saturated. Using iotop or lsof, I'd identify what's doing the I/O.

Common fixes: if it's a backup, reschedule it. If it's slow storage, migrate to SSD or add a cache layer (Redis). If it's a database, work with the dev team to optimize queries — usually it's N+1 queries or missing indexes.

For immediate relief, I'd redirect heavy I/O jobs to off-peak hours. Long-term, I'd upgrade the storage or add caching. -->

# You see this:
$ uptime
load average: 15.2, 12.8, 10.5

# You run vmstat and see:
$ vmstat 1 3
 r  b  us sy id wa
15  6   4  1 20 75
↑  ↑        ↑  ↑
queue blocked CPU is waiting on disk

# Your diagnosis in 10 seconds:
"The system is CPU-bound? NO. I/O-bound? YES. Here's why:
 • Load 15.2 (overloaded) ✓
 • but us% is only 4% (app barely running)
 • and wa% is 75% (CPU idle waiting on disk)
 • and b=6 (6 processes blocked, waiting for disk)
 
The disk is the problem, not the CPU. I need to check iostat to see
which disk is saturated, then iotop/lsof to find the culprit."

memory
<!-- f memory is low, I first identify the memory hog with ps aux --sort=%mem. Then I determine if it's a leak or legitimate usage:

If it's a leak (RSS grows monotonically and restarting resets it), I'd restart the service immediately to reduce pressure, then work with the dev team to profile and fix the leak using memory profilers.

If it's legitimate — the app just needs that much RAM — I scale up: add more RAM if it's a single instance, or add more instances if it's a service. For containerized apps, I set proper memory limits so one bloated container doesn't take down the whole system.

To prevent this, I set monitoring alerts at 70% utilization so we scale before hitting crisis." -->

----------------------Full flow---------------------

Customer says "service is slow, keeps restarting"

# 1. Memory actually low?
$ free -h
              total    used    free    shared buff/cache available
Mem:           16Gi    12Gi    1.2Gi   256Mi   2.8Gi      2Gi
              ↑ available is only 2Gi (12.5%) → YES, memory is tight

# 2. Which process?
$ ps aux --sort=-%mem | head -5
USER    PID  %MEM   VSZ      RSS      COMMAND
root   1234  45.0%  8388608  7340032  java  ← 7GB RSS, that's our suspect
root   5678   8.0%  2097152  1310720  mysql
...

# 3. Is it swapping?
$ vmstat 1 3
 r  b  swpd     free  si     so    ...  wa
 8  3  2097152  50000 500   1200   ...  82
 ↑  ↑  ↑        ↑     ↑     ↑         ↑
 Yes! swapd is 2GB, si/so are high, wa=82% means disk I/O hell

# 4. PROOF: Track RSS every minute for 10 minutes
$ for i in {1..10}; do
    echo "$(date +%H:%M) RSS=$(ps -o rss= -p 1234)kB"
    sleep 60
  done

14:00 RSS=6291456kB   ← 6GB
14:01 RSS=6350000kB   ← growing
14:02 RSS=6400000kB   ← growing
14:03 RSS=6450000kB   ← growing
14:04 RSS=6500000kB   ← growing
14:05 RSS=6550000kB   ← still growing, never drops
14:06 RSS=6600000kB   ← definitely a leak
...

# Pattern: RSS grew 300MB in 6 minutes at DAY 14
# If this continues: (300MB/6min) × (60min/hour) × (24hr/day) × 14 days = ~20GB
# This matches "service slow after 2 weeks"

# 5. Is the memory in swap or RAM?
$ grep VmSwap /proc/1234/status
VmSwap:            0 kB  ← All 7GB is in real RAM, none in swap yet

# 6. Where in the memory?
$ cat /proc/1234/smaps | awk '/^[^ ]/{region=$0} /^Rss/{rss+=$2; print region, $2"kB"} END{print "Total:", rss"kB"}'
# Shows heap, libraries, stacks — usually heap is growing (app leak)

# 7. DIAGNOSIS you tell the dev team:
"The Java process has a memory leak:
 • RSS: 6.5GB (45% of system RAM)
 • Growth rate: ~50MB/minute
 • Pattern: Climbs for 14 days, then crashing
 • Restart resets RSS to baseline, then climbs again
 • Heap analysis shows accumulating objects in {specific class}
 
 → FIX: Profile with JProfiler or YourKit, find the class that's never freed."

----------------------Full flow---------------------

swappine

<!-- "Active swapping is a crisis — the system is spending more time moving pages than doing work. It's slow and getting worse.

My immediate action: restart the bloated service to free memory, then investigate. If it's a memory leak, I identify it with profiling tools and fix the code. If it's just high legitimate usage, I add more RAM.

Long-term: I set vm.swappiness=10 so the kernel avoids swapping, use monitoring to catch high memory before thrashing happens, and set per-process memory limits so one bad process doesn't drag down the -->

The Decision Point: When to Act
State	Action	Timeline
High memory but normal swap	Monitor, investigate	Can wait 1-2 hours
Swapping starting (si/so > 50)	Consider restart	Within 30 minutes
Thrashing (si/so > 5000, wa > 70%)	Restart immediately	Now, not later
