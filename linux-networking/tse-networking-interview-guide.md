# TSE Networking & Infrastructure Interview Mastery
## Core Framework: Communication First, Troubleshooting Second

> **Goal:** Master the TSE mindset—diagnose networking issues methodically, communicate clearly, and support every claim with evidence.
>
> **Interview Success = Systematic Thinking + Communication Skills + Technical Depth**

---

## Part 1: Interview Communication Framework

The difference between passing and failing networking interviews isn't technical breadth—it's **how you think and talk about problems**.

### The TSE Diagnostic Mindset

When facing "the service is down," weak candidates panic. Strong candidates execute a **systematic, testable process**:

1. **Isolate the problem** — Don't assume. Test each layer independently.
2. **Gather evidence** — Show commands and output, not guesses.
3. **Explain your reasoning** — Why you suspect each issue, why you test that way.
4. **Propose solutions** — Explain both the fix and why it works.

### Good vs Weak Interview Answers

#### Weak Answer:
❌ *"DNS is probably broken. Let me restart the service."*
- No evidence
- Doesn't isolate the problem
- Treats symptoms, not cause

#### Strong Answer:
✅ *"Service unreachable could be 4 things: not listening, network blocked, DNS wrong, or application error. Let me check sequentially."*
1. `ss -tlnp | grep 8080` — Is it listening?
2. `ping 10.0.1.50` — Can I reach the host?
3. `dig api.example.com` — Does DNS resolve correctly?
4. `curl -v https://api.example.com` — What's the application returning?

**Why it's strong:**
- Identifies 4 independent test points
- Shows commands that verify each hypothesis
- Doesn't assume anything
- Gives interviewer confidence in your thinking

---

### Model Answer Phrases

#### When You're Uncertain:

✅ *"I'm not sure, so let me test it. I'd run `dig +trace` to see the full resolution chain."*

❌ *"I think DNS might be the problem."*

#### When You Find an Issue:

✅ *"Logs show 'connection timeout' at 30 seconds. That matches a network timeout, not a DNS issue. I'd confirm with `tcpdump` to see if packets reach the server."*

❌ *"The server's not responding."*

#### When You Need to Escalate:

✅ *"TCP connections are stuck in SYN_RECV state. This could be a syn-flood attack or misconfigitation. I'd check the load balancer logs and firewall rules. If clean, I'd suspect the backend service has a listening queue issue—we'd need to adjust the `somaxconn` kernel parameter."*

❌ *"Something's broken. Let me contact someone else."*

---

### The 4-Layer Troubleshooting Sequence

Master this sequence and you'll solve 95% of networking issues in interviews:

| Layer | Test Command | What Success Looks Like |
|-------|--------------|------------------------|
| **Service** | `ss -tlnp \| grep :8080` | Port 8080 LISTEN (your app PID) |
| **Network** | `ping <ip>` or `nc -zv <ip> 8080` | "connected" / success |
| **DNS** | `dig myapp.example.com` | Shows correct IP, TTL shown |
| **Application** | `curl -v https://myapp.com` | HTTP 200/301/etc (not 5xx) |

**Example troubleshooting flow:**

```
1. Service not listening?
   → Fix: Start the service, check configuration
   → Escalate: Service crashes on startup (logs show why)

2. Service listening but can't reach it?
   → Fix: Firewall rule blocks your IP
   → Escalate: Network path broken (routing issue)

3. Can reach service but DNS wrong?
   → Fix: Update DNS record at registrar
   → Escalate: DNS propagation—wait 15 minutes, then retry

4. DNS correct but app returns 500?
   → Fix: Application error (check app logs)
   → Escalate: Database unreachable (check DB connection)
```

Always test these 4 **independently**. Don't jump to conclusions.

---

### Interview Communication Checklist

Before answering any networking question, ask yourself:

- [ ] Do I understand what the problem statement is?
- [ ] Do I know what "success" looks like? (What should happen when it works?)
- [ ] Can I test this without making assumptions?
- [ ] Have I identified the most likely 3 causes?
- [ ] Can I explain why I'm testing each one?
- [ ] Do I know the commands and expected output?
- [ ] Can I explain the root cause (not just the symptom)?
- [ ] Do I have a fix that addresses the cause, not a workaround?

If you answer "no" to any of these, pause and clarify in the interview: *"Let me break this down systematically..."*

---

## Part 2: OSI Model — The Diagnostic Framework

TSE doesn't care about protocol internals. TSE cares about **which layer is broken**.

| Layer | Name | TSE Question | Diagnostic Tool |
|-------|------|-------------|-----------------|
| **Layer 3** | Network (IP) | Can this IP reach that IP? | `ping`, `route`, `traceroute` |
| **Layer 4** | Transport (TCP/UDP) | Can I reach this port? | `nc -zv`, `ss`, `netstat` |
| **Layer 7** | Application | Is the app responding correctly? | `curl -v`, logs, tcpdump |

**The TSE Rule:** When something is unreachable, troubleshoot **bottom-up through layers**:
- **Layer 3 broken?** → No ping ✗
- **Layer 4 broken?** → Ping works, but port refuses/times out ✗
- **Layer 7 broken?** → Port responds, but HTTP/DNS/app returns error ✗

```bash
# Example: Diagnosing "API server unreachable"

# Layer 3: Can I reach the IP?
$ ping 10.0.1.50
PING 10.0.1.50 (10.0.1.50): 56 data bytes
64 bytes from 10.0.1.50: icmp_seq=0 ttl=64 time=1.234 ms
✓ Layer 3 OK

# Layer 4: Can I reach the port?
$ nc -zv 10.0.1.50 8080
Connection to 10.0.1.50 port 8080 [tcp/*] succeeded!
✓ Layer 4 OK

# Layer 7: Is the app responding?
$ curl -v https://api.example.com
< HTTP/1.1 502 Bad Gateway
✗ Layer 7 broken (app or backend config issue)
```

---

## Part 3: DNS Resolution — Foundation & Troubleshooting

DNS is where 40% of networking "issues" actually live. Understand this completely.

### The Full Resolution Chain

When you run `dig google.com`, here's what happens:

```
Your machine (8.8.8.8 is default resolver)
   ↓
Google Public DNS (recursive resolver - does the work)
   ↓
Root server ("where's .com?")
   ↓
TLD server ("where's google.com?")
   ↓
Google's authoritative nameserver (source of truth: 8.8.8.8 A record)
   ↓
Back to Google Public DNS (caches it)
   ↓
Back to your machine (shows you + caches it)
```

**Critical fact:** TTL (Time To Live) controls how long each layer caches. Change DNS record? All layers keep returning **old value** for TTL seconds.

### DNS Query Debugging

#### Command: `dig` with layers exposed

```bash
# Step 1: What does my resolver think?
$ dig google.com @8.8.8.8
google.com.     299 IN  A   142.251.41.14
;; Query time: 45 msec
;; SERVER: 8.8.8.8#53 (8.8.8.8)  ← Who answered?
;; Authoritative answer: no         ← Cached, not from zone owner

# Step 2: What does the authoritative nameserver say?
$ dig google.com @ns1.google.com
google.com.     3600 IN  A   142.251.41.14
;; Authoritative answer: yes   ← From source of truth
;; Query time: 2 msec

# Authority [difference?]
# Resolver: 299 TTL (cached, expires soon)
# Authoritative: 3600 TTL (source of truth, newer answer)
# → Resolver's cache is stale. Wait 299 seconds or flush cache locally.
```

#### The TTL Problem (Real Scenario)

You migrate an API from 10.0.1.50 to 10.0.2.100.

```
Authoritative DNS: Updated immediately (10.0.2.100)
Team's resolver cache: Still returns 10.0.1.50 (TTL=3600, 58 min remaining)
Customer's machine cache: Still returns 10.0.1.50 (OS cache, even longer)
Result: API "unreachable" for customers for up to 1 hour
```

**Interview answer:** *"Before migrations, lower TTL to 300 seconds 1 day early. After migration succeeds, raise back to 3600. If we forget, stale caches cause 'DNS not updated' complaints. I'd confirm with `dig <domain> @<zone-owner-ns>` vs `dig <domain> @8.8.8.8` to see propagation delay."*

---

## Part 4: TCP/IP Fundamentals & Connection Issues

### The 3-Way Handshake (Why Connections Fail)

TCP connections happen in **3 steps**:

```
Client              Server
  │                  │
  ├──SYN──────────→  │  (Client: "Can we connect?")
  │                  │
  │  ←──SYN-ACK──────┤  (Server: "Yes, I hear you")
  │                  │
  ├──ACK──────────→  │  (Client: "I hear you too, we're connected")
  │                  │
  ├──[DATA]─────────→│  (Now we can send data)
```

If **any step fails**, connection fails.

### Diagnosing Connection Failures

#### Symptom: "Connection Refused"

```bash
$ nc -zv 10.0.1.50 8080
nc: connect to 10.0.1.50 port 8080 (tcp) failed: Connection refused
```

**What it means:** Server responded with RST (reset). Something is actively rejecting the connection.

**Causes:**
1. Service not listening on that port
2. Firewall rule explicitly rejects (returns RST instead of dropping)
3. Service crashed

**Diagnosis:**
```bash
# Is the service listening?
$ ssh 10.0.1.50
$ ss -tlnp | grep 8080
tcp  LISTEN  0  128  *:8080  LISTEN  1234/myapp   ✓

# Can you reach it locally?
$ nc -zv localhost 8080    # If this works, firewall is the issue
```

**Interview answer:** *"Connection refused means the server is actively rejecting. First, I'd check if the service is listening locally on that port with `ss -tlnp`. If it's not listening, start it or check why it crashed (logs). If it is listening but remote connection refuses, it's a firewall rule—check `iptables -L -n` or cloud security groups for port 8080."*

---

## Part 5: Firewalls & Network Access Control

### iptables: The Linux Firewall

Firewalls operate at **Layer 3 (IP) and Layer 4 (Ports)**. They decide: Do I let this packet through?

#### Basic iptables Rules

```bash
# List all rules
$ sudo iptables -L -n

Chain INPUT (policy ACCEPT)
target   prot opt source        destination
ACCEPT   tcp  --  192.168.1.0/24  0.0.0.0/0  tcp dpt:22  ← SSH only from subnet
DROP     tcp  --  0.0.0.0/0       0.0.0.0/0  tcp dpt:80  ← Block HTTP
ACCEPT   tcp  --  0.0.0.0/0       0.0.0.0/0  tcp dpt:443 ← Allow HTTPS
```

#### Key Concepts

**Three targets:**
- `ACCEPT` — Let the packet through
- `DROP` — Silently discard (timeout on client)
- `REJECT` — Discard and send error (connection refused)

**Why it matters:**
- `DROP` → Client sees timeout (waits 30+ seconds)
- `REJECT` → Client sees connection refused (immediate)

---

## Part 6: HTTP/HTTPS & Application Layer Issues

### HTTP Status Codes Matter

| Code | Meaning | Server Problem? |
|------|---------|-----------------|
| **2xx** | Success | No |
| **5xx** | Server Error | **Yes** |

**502 Bad Gateway:** Load balancer can't reach backend  
**503 Service Unavailable:** All backends down/overloaded

---

## Part 7: Load Balancing & High Availability

### Health Checks: The Silent Failure

Health checks periodically query: *"Are you alive?"*

```bash
# If health check times out (backend is slow)
# Load balancer marks instance UNHEALTHY
# Removes from pool
# All traffic goes to remaining instances
# Result: 503 (no healthy backends)
```

**Fix:** Either speed up health check endpoint or increase timeout.

---

## Part 8: Timeout Issues — The Silent Killer

| Timeout Type | Default | Where |
|--------------|---------|-------|
| **Connection** | 30s | TCP handshake |
| **Read** | 60s | Server too slow |
| **Idle** | 300s | Keepalive timeout |
| **Health check** | 5s | Load balancer |

**Interview rule:** Distinguish between:
- **Timeout** → Silently dropped (no response)
- **Refused** → Active rejection (RST)

Different fixes for each.

---

## Part 9: Complete Troubleshooting Decision Tree

```
SERVICE UNREACHABLE
│
├─ Can I ping the IP? YES/NO
│
├─ Can I reach the port? YES/NO
│  ├─ Connection refused? → Service not listening
│  └─ Timeout? → Firewall silently drops
│
├─ Does DNS resolve? YES/NO
│  ├─ NXDOMAIN? → DNS record missing
│  ├─ SERVFAIL? → Nameserver broken
│  └─ Timeout? → Network path to NS broken
│
└─ What does app return?
   ├─ 2xx/3xx? → Working
   ├─ 4xx? → Your request wrong
   ├─ 5xx? → Server error
   │  ├─ 502? → Backend unreachable
   │  └─ 503? → All backends down
```

---

## Part 10: Network Tools Mastery

```bash
# DNS
dig domain.com                    # Query DNS
dig +trace domain.com              # Show full chain
dig domain.com @nameserver         # Query specific NS

# Connectivity
ping 10.0.1.50                    # Is IP reachable?
nc -zv 10.0.1.50 8080             # Is port reachable?
curl -v https://api.example.com    # App response

# Lists
ss -tlnp                          # Listening ports + PID
ss -tnp                           # All TCP connections
lsof -i :8080                     # What's on this port?

# Routing
ip route                          # Show routing table
traceroute 8.8.8.8                # Show packet path
mtr -c 100 8.8.8.8                 # Measure packet loss

# Firewall
sudo iptables -L -n               # Show firewall rules
sudo tcpdump -i eth0              # Capture packets
```

---

## Part 11: Real Interview Scenarios

### Scenario 1: Intermittent DNS (Every 5 Minutes)

**Problem:** API sometimes unreachable, mysteriously recovers.

**Root cause:** Database connection pool exhaustion every 5 minutes, slow query blocks all connections, health checks fail, backend marked unhealthy, traffic times out.

**Fix:** Optimize slow query + increase pool size.

---

### Scenario 2: DNS Works Locally, Wrong IP for Customers

**Problem:** You migrated DNS record. Customers still see old IP.

**Root cause:** Didn't lower TTL before migration. Resolver cached old IP for 3600 seconds.

**Fix:** Next time: lower TTL 1 day before migration (to 300s), migrate, raise TTL back after.

---

## Part 12: Common Mistakes

❌ Restart service before checking if it's actually broken  
❌ Assume DNS without testing  
❌ Change multiple things at once  
❌ Blame network without checking app logs  
❌ Not distinguish timeout from refused connection  
❌ Not verify fixes actually work  

---

## Part 13: Quick Reference Cheat Sheet

```bash
# 4-layer test sequence
dig api.example.com &&           # DNS works?
ping 10.0.1.50 &&                # Network works?
nc -zv 10.0.1.50 8080 &&        # Port works?
curl -v https://api.example.com  # App works?

# Key diagnostics
ss -tlnp | grep 8080                    # Is service listening?
sudo iptables -L -n | grep 8080         # Firewall allow port?
mtr -c 10 10.0.1.50                     # Packet loss?
lsof -i :8080                           # What's on port?
curl -w "HTTP %{http_code}" -o /dev/null -s <url>  # Status code
```

---

## Part 14: The TSE Mindset

**Strong candidate:**
- Tests systematically ✅
- Isolates problems ✅
- Supports claims with evidence ✅
- Explains reasoning ✅
- Proposes solutions based on root cause ✅

**Weak candidate:**
- Makes assumptions ❌
- No isolation ❌
- No evidence ❌
- No reasoning ❌
- Treats symptoms ❌

**Final principle:**

*"When someone describes a problem, I immediately think: What does working look like? Then I test each layer independently until I find the broken one. I show evidence and explain my thinking."*

Master this mindset, and you'll pass.

---

**Pre-interview checklist:**
- [ ] Can I explain `dig +trace` step by step?
- [ ] Can I read `ss -tnp` output and spot issues?
- [ ] Can I distinguish timeout from refused connection?
- [ ] Can I diagnose stale DNS cache vs NXDOMAIN?
- [ ] Can I explain 3-way TCP handshake?
- [ ] Can I read iptables rules and add one?
- [ ] Can I diagnose 502 vs 503?
- [ ] Can I fix and measure timeout issues?
- [ ] Can I run the 4-layer troubleshooting sequence?
- [ ] Can I communicate like a strong candidate?

You've got this. Good luck.
