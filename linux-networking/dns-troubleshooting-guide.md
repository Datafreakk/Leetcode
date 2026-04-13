# DNS Troubleshooting: Real Scenarios with Command Outputs & Guidance

> Complete guide with actual command outputs, expected responses, and step-by-step diagnostic methods for TSE interviews.

---

## Scenario 1: "I Can't Reach example.com"

### Customer Report
```
"When I try to visit example.com, I get 'Name or service not known' error.
Website is down or DNS is broken?"
```

---

### STEP 1: Can you resolve the domain?

**Command:**
```bash
$ nslookup example.com
```

**Expected Output A (WORKS):**
```
Name:      example.com
Address:   93.184.216.34
```
✅ **DNS resolution successful!** The domain exists and maps to IP 93.184.216.34

**Expected Output B (FAILS):**
```
** server can't find example.com: NXDOMAIN
```
❌ **DNS failed!** Domain doesn't exist or is misspelled. This IS a DNS issue.

---

### STEP 2: Assuming DNS works (Output A), can you reach that IP?

**Command:**
```bash
$ ping 93.184.216.34
```

**Expected Output A (NETWORK WORKS):**
```
PING 93.184.216.34 (93.184.216.34): 56 data bytes
64 bytes from 93.184.216.34: icmp_seq=0 ttl=54 time=23.456 ms
64 bytes from 93.184.216.34: icmp_seq=1 ttl=54 time=24.123 ms
64 bytes from 93.184.216.34: icmp_seq=2 ttl=54 time=23.789 ms

--- 93.184.216.34 statistics ---
3 packets transmitted, 3 packets received, 0.0% packet loss
min/avg/max/stddev = 23.456/23.789/24.123/0.270 ms
```
✅ **Network is working!** Can reach the IP. This is NOT a network issue.

**Expected Output B (NETWORK FAILS):**
```
PING 93.184.216.34 (93.184.216.34): 56 data bytes
Request timeout
Request timeout
Request timeout

--- 93.184.216.34 statistics ---
3 packets transmitted, 0 packets received, 100.0% packet loss
```
❌ **Network broken!** Can't reach the IP. This is a network/firewall/routing issue, NOT DNS.

---

### STEP 3: Assuming network works, test the actual HTTP service

**Command:**
```bash
$ curl -v http://example.com
```

**Expected Output A (SERVICE WORKS):**
```
*   Trying 93.184.216.34:80...
* Connected to example.com (93.184.216.34) port 80 (#0)
> GET / HTTP/1.1
> Host: example.com
> User-Agent: curl/7.64.1
> Accept: */*

< HTTP/1.1 200 OK
< Content-Type: text/html; charset=UTF-8
< Content-Length: 1256
< Connection: keep-alive

<!doctype html>
<html>
<head>
    <title>Example Domain</title>
</head>
<body>
<h1>Example Domain</h1>
[...HTML content...]
</body>
</html>
```
✅ **Website is working!** Got HTTP 200. Everything is fine!

**Expected Output B (SERVICE NOT RESPONDING):**
```
*   Trying 93.184.216.34:80...
* Connection refused
curl: (7) Failed to connect to example.com port 80: Connection refused
```
❌ **Service is down!** Port 80 not listening. This is an application/service issue, NOT DNS.

---

### ROOT CAUSE DETERMINATION

If you got:
- ✅ DNS resolves → ✅ Network works → ✅ HTTP 200 → **Everything fine!**
- ✅ DNS resolves → ✅ Network works → ❌ Connection refused → **Service/app issue**
- ✅ DNS resolves → ❌ Network timeout → ... → **Firewall/routing issue**
- ❌ DNS fails (NXDOMAIN) → ... → **DNS issue**

**Interview Answer:**
"I'd test DNS resolution first with `nslookup`. If it returns NXDOMAIN or times out, it's a DNS issue. If DNS works, I'd test network with `ping`. If that fails, it's a firewall/routing issue. If both work, I'd test the service with `curl`. By isolating each layer, I know exactly what to escalate."

---

## Scenario 2: "DNS Resolves But Returns Wrong IP (Stale Cache)"

### Customer Report
```
"We migrated our API from 10.0.1.50 to 10.0.2.100 yesterday.
Some requests work, some fail. DNS seems broken."
```

---

### STEP 1: Query the resolver

**Command:**
```bash
$ dig api.myapp.com @8.8.8.8
```

**Output:**
```
; <<>> DiG 9.10.6 <<>> api.myapp.com @8.8.8.8
; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 55961
;; flags: qr rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 1

;; QUESTION SECTION:
;api.myapp.com.			IN	A

;; ANSWER SECTION:
api.myapp.com.		1234	IN	A	10.0.1.50

;; Query time: 8 msec
;; SERVER: 8.8.8.8#53(8.8.8.8)
;; WHEN: Mon Apr 13 14:33:40 IST 2026
;; MSG SIZE  rcvd: 54
```

**What this tells you:**
- ✅ DNS resolves successfully (NOERROR)
- **IP returned: 10.0.1.50** (the OLD IP!)
- **TTL: 1234 seconds** (about 20 minutes left before cache expires)
- **Server: 8.8.8.8** (Google's resolver, which is caching)

---

### STEP 2: Query the authoritative server (source of truth)

**Command:**
```bash
$ dig api.myapp.com @ns1.myapp-dns.com
```

**Output:**
```
; <<>> DiG 9.10.6 <<>> api.myapp.com @ns1.myapp-dns.com
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 99999
;; flags: qr aa rd;   ← **aa = AUTHORITATIVE ANSWER**
;; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 1

;; QUESTION SECTION:
;api.myapp.com.			IN	A

;; ANSWER SECTION:
api.myapp.com.		3600	IN	A	10.0.2.100

;; Query time: 6 msec
;; SERVER: ns1.myapp-dns.com#53(ns1.myapp-dns.com)
;; WHEN: Mon Apr 13 14:33:40 IST 2026
;; MSG SIZE  rcvd: 54
```

**What this tells you:**
- ✅ Authoritative server says: **10.0.2.100** (NEW IP!)
- ✅ It has the **aa flag** (authoritative answer)
- **TTL: 3600 seconds** (1 hour)

---

### STEP 3: Compare the two answers

| Source | IP | TTL | Authoritative? |
|--------|----|----|---|
| Google (8.8.8.8) | 10.0.1.50 | 1234 sec | ❌ NO (cached) |
| **Authoritative (ns1)** | **10.0.2.100** | 3600 sec | ✅ **YES (truth)** |

**Root Cause:** Google's DNS is caching the OLD IP. TTL expires in 1234 seconds (~20 minutes).

---

### THE FIX (3 Options)

**Option A: Wait for TTL to expire** (simplest, automatic)
```
Wait ~20 minutes for Google's cache to expire.
Then it will query authoritative again and get 10.0.2.100.
```

**Option B: Reduce TTL before migrations** (best practice for future)
```bash
# 12 hours BEFORE migration:
# Change TTL from 3600 to 300 seconds in your DNS provider (Route53, Cloudflare, etc.)

# Make the IP change
# Now it propagates in 300 seconds (5 minutes) instead of 3600 seconds

# After migration succeeds and settles:
# Raise TTL back to 3600
```

**Option C: Flush the cache** (if you control the resolver)
```bash
# For your corporate resolver (e.g., running BIND):
$ sudo rndc flush

# For systemd-resolved:
$ sudo systemctl restart systemd-resolved
```

---

### VERIFICATION

**Monitor propagation across resolvers:**
```bash
# After waiting/fixing, test multiple resolvers:

$ dig api.myapp.com @8.8.8.8
api.myapp.com.		300	IN	A	10.0.2.100  ← ✅ UPDATED!

$ dig api.myapp.com @1.1.1.1
api.myapp.com.		300	IN	A	10.0.2.100  ← ✅ UPDATED!

$ dig api.myapp.com @8.8.4.4
api.myapp.com.		300	IN	A	10.0.2.100  ← ✅ UPDATED!
```

All resolvers now return the NEW IP. **FIXED!**

**Interview Answer:**
"DNS resolves but returns wrong IP = cache mismatch. I'd query the authoritative server directly to confirm the correct IP. Then wait for TTL to expire, or if it's urgent, reduce TTL before migrations. The problem isn't DNS—it's caching working as designed."

---

## Scenario 3: "DNS Queries Sometimes Timeout"

### Customer Report
```
"Sometimes nslookup api.company.com works, sometimes it hangs for 5 seconds then fails.
Happens randomly, about 10% of queries fail."
```

---

### STEP 1: Reproduce the issue

**Command:**
```bash
$ for i in {1..10}; do echo "Query $i:"; time nslookup api.company.com; done
```

**Output:**
```
Query 1:
Name:	api.company.com
Address: 10.1.1.100

real	0m0.045s

Query 2:
Name:	api.company.com
Address: 10.1.1.100

real	0m0.038s

Query 3:
;; connection timed out; no servers could be reached

real	0m5.012s

Query 4:
Name:	api.company.com
Address: 10.1.1.100

real	0m0.052s

Query 5:
;; connection timed out; no servers could be reached

real	0m5.008s
```

**What this tells you:**
- ✅ Some queries succeed (40ms)
- ❌ Some queries timeout (5 seconds)
- Pattern: **Intermittent failures** = likely resource contention or packet loss

---

### STEP 2: Measure query time with dig (shows more detail)

**Command:**
```bash
$ dig api.company.com @8.8.8.8 +stats
```

**Output (Success):**
```
; <<>> DiG 9.10.6 <<>> api.company.com @8.8.8.8 +stats
api.company.com.	1200	IN	A	10.1.1.100

;; Query time: 28 msec  ← FAST
;; SERVER: 8.8.8.8#53(8.8.8.8)
;; WHEN: Mon Apr 13 14:40:00 IST 2026
```

**Output (Slow/Timeout):**
```
; <<>> DiG 9.10.6 <<>> api.company.com @8.8.8.8 +stats
;; connection timed out; trying next server
;; connection timed out; trying next server
;; connection timed out; trying next server

;; Query time: 5000 msec  ← TIMEOUT! (5 seconds)
;; SERVER: 8.8.8.8#53(8.8.8.8)
```

---

### STEP 3: Query authoritative directly (to isolate the problem)

**Command:**
```bash
$ dig api.company.com @ns1.company-dns.com +stats
```

**Output:**
```
; <<>> DiG 9.10.6 <<>> api.company.com @ns1.company-dns.com +stats
api.company.com.	3600	IN	A	10.1.1.100

;; flags: qr aa rd;
;; Query time: 18 msec  ← FAST! Authoritative is fine.
;; SERVER: ns1.company-dns.com#53(ns1.company-dns.com)
```

**Analysis:**
- ✅ Authoritative responds **fast (18ms)**
- ❌ Google's resolver sometimes **slow/times out (5000ms)**
- **Conclusion:** Problem is NOT your authoritative server. Problem is Google's resolver or the path to it.

---

### STEP 4: Check packet loss on the path

**Command:**
```bash
$ mtr -c 100 8.8.8.8
```

**Output:**
```
                              My traceroute  [v0.93]
  localhost (0.0.0.0)                    0.0%
  1. 10.0.0.1                            0.0%
  2. isp-gateway1.isp.com                0.0%
  3. isp-backbone1.isp.com               0.5%
  4. google-peer.isp.com                 8.0%  ← Packet loss starts!
  5. 8.8.8.8                            13.0%  ← More loss!

Drop%: 13.0%
```

**What this tells you:**
- Hop 4 and 5 have **packet loss** (8-13%)
- This causes:
  - Some queries to succeed (lucky packets get through)
  - Some queries to timeout (packets lost, no response)

---

### ROOT CAUSE
**13% packet loss on the path to Google's resolver (8.8.8.8).**

---

### THE FIX (3 Options)

**Option A: Use a different resolver** (simplest for you)
```bash
# Edit /etc/resolv.conf:
nameserver 1.1.1.1         # Cloudflare
nameserver 8.8.4.4         # Google secondary

# Restart:
$ sudo systemctl restart systemd-resolved

# Test:
$ for i in {1..10}; do dig api.company.com @1.1.1.1; done
# All succeed! Different path, no packet loss.
```

**Option B: Use TCP mode** (more reliable on lossy networks)
```bash
# Edit /etc/resolv.conf:
options use-vc  # Use Virtual Circuit (TCP)

# TCP retransmits lost packets, UDP doesn't.
# More reliable but slightly slower.

$ sudo systemctl restart systemd-resolved
```

**Option C: Escalate to infrastructure team**
```
"13% packet loss on hop 4 (google-peer.isp.com).
Network team needs to investigate peer link quality."
```

---

### VERIFICATION (After switching to Cloudflare)

**Command:**
```bash
$ for i in {1..10}; do echo "Query $i:"; time dig api.company.com @1.1.1.1 +stats; done
```

**Output:**
```
Query 1:
api.company.com.	1200	IN	A	10.1.1.100
;; Query time: 23 msec

real	0m0.025s

Query 2:
api.company.com.	1200	IN	A	10.1.1.100
;; Query time: 18 msec

real	0m0.020s

Query 3:
api.company.com.	1200	IN	A	10.1.1.100
;; Query time: 21 msec

real	0m0.023s

Query 4:
api.company.com.	1200	IN	A	10.1.1.100
;; Query time: 19 msec

real	0m0.021s

Query 5:
api.company.com.	1200	IN	A	10.1.1.100
;; Query time: 22 msec

real	0m0.024s

[... all succeed, all fast ...]
```

**✅ FIXED!** Now all queries succeed and are consistently fast. No timeouts!

**Interview Answer:**
"Intermittent DNS timeouts usually mean packet loss on the path or resolver overload. I'd reproduce the issue with a loop, measure query times with `dig +stats`, then use `mtr` to check for packet loss. If authoritative responds fast but resolver is slow, it's a network issue. The solution is to switch resolvers or enable TCP mode (handles retransmits)."

---

## Scenario 4: "Domain Doesn't Exist (NXDOMAIN) But I Just Created It"

### Customer Report
```
"I created database.internal.company.com in Route53 5 minutes ago.
But it says NXDOMAIN: Name or service not known!"
```

---

### STEP 1: Try to resolve it

**Command:**
```bash
$ dig database.internal.company.com @8.8.8.8
```

**Output:**
```
; <<>> DiG 9.10.6 <<>> database.internal.company.com @8.8.8.8
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NXDOMAIN, id: 12345
;; flags: qr rd ra;
;; QUESTION SECTION:
;database.internal.company.com.		IN	A
;; AUTHORITY SECTION:
internal.company.com.		900	IN	SOA	ns1.internal.company.com. ...
;; Query time: 12 msec
;; SERVER: 8.8.8.8#53(8.8.8.8)
```

**Status: NXDOMAIN** = Domain doesn't exist (according to resolver)

---

### STEP 2: Query the authoritative server directly

**Command:**
```bash
$ dig database.internal.company.com @ns-1234.awsdns-56.com
```

**Output:**
```
; <<>> DiG 9.10.6 <<>> database.internal.company.com @ns-1234.awsdns-56.com
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 99999
;; flags: qr aa rd;   ← AUTHORITATIVE!
;; QUESTION SECTION:
;database.internal.company.com.		IN	A
;; ANSWER SECTION:
database.internal.company.com.	300	IN	A	10.1.2.100
;; Query time: 6 msec
;; SERVER: ns-1234.awsdns-56.com#53(ns-1234.awsdns-56.com)
```

**Status: NOERROR** = Domain DOES exist! (according to authoritative)

---

### ANALYSIS

| Resolver | Status | Answer |
|----------|--------|--------|
| Google (8.8.8.8) | NXDOMAIN | ❌ Doesn't exist |
| Authoritative (ns-1234) | NOERROR | ✅ **Exists!** (10.1.2.100) |

**Contradiction!** Authoritative says it exists, Google says it doesn't.

---

### ROOT CAUSE

**DNS propagation hasn't completed yet.**

Timeline:
- 14:30:00 → You created the record in Route53
- 14:35:00 → You try to resolve it (now)
- Route53 updated its nameservers (authoritative)
- But public resolvers cached the OLD answer (before your record existed)
- **NS record TTL: 48 hours** (172800 seconds)
- **Public resolvers won't update for up to 48 hours**

---

### THE FIX (3 Options)

**Option A: Query authoritative directly** (immediate proof)
```bash
$ dig database.internal.company.com @ns-1234.awsdns-56.com
# Works immediately! Proves record exists.
```

**Option B: Wait for caches to expire** (automatic, up to 48 hours)
```bash
# Nothing to do. After 48 hours, all caches refresh and find the record.
```

**Option C: Reduce NS TTL before creating records** (best practice)
```bash
# 12 hours BEFORE creating the record:
# In Route53, reduce NS record TTL from 172800 to 300 seconds

# Create the record

# Wait 5 minutes

# Verify globally:
$ dig database.internal.company.com @1.1.1.1
# Now it's found! Propagated in 5 minutes instead of 48 hours.

# Raise NS TTL back to 172800
```

---

### VERIFICATION (Monitoring propagation)

**Check multiple public resolvers:**
```bash
$ dig database.internal.company.com @8.8.8.8
;; status: NXDOMAIN  ← Still old

$ dig database.internal.company.com @1.1.1.1
;; status: NXDOMAIN  ← Still old

$ dig database.internal.company.com @8.8.4.4
;; status: NXDOMAIN  ← Still old

$ dig database.internal.company.com @ns-1234.awsdns-56.com
;; status: NOERROR   ← ✅ Authoritative has it!
database.internal.company.com.	300	IN	A	10.1.2.100
```

After 48 hours (or if you reduced NS TTL and waited 5 min):
```bash
$ dig database.internal.company.com @8.8.8.8
;; status: NOERROR   ← ✅ NOW UPDATED!
database.internal.company.com.	300	IN	A	10.1.2.100
```

**Interview Answer:**
"DNS doesn't exist immediately because authoritative records aren't public yet. I'd query the authoritative server with `@ns-xxx` to prove the record exists there. Then wait for public resolver caches (TTL) to expire, or reduce NS TTL before creating records (best practice for future)."

---

## Scenario 5: "SERVFAIL - Server Failed to Process"

### Customer Report
```
"Getting weird error: dig api.example.com → SERVFAIL
The domain exists but something's broken."
```

---

### STEP 1: Try the query

**Command:**
```bash
$ dig api.example.com @8.8.8.8
```

**Output:**
```
; <<>> DiG 9.10.6 <<>> api.example.com @8.8.8.8
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: SERVFAIL, id: 12345
;; flags: qr rd ra; QUERY: 1, ANSWER: 0, AUTHORITY: 0, ADDITIONAL: 0
;; QUESTION SECTION:
;api.example.com.		IN	A
;; Query time: 1234 msec
;; SERVER: 8.8.8.8#53(8.8.8.8)
```

**Status: SERVFAIL** = Server error (not just "not found", but server failed to process)

---

### STEP 2: Query the authoritative server directly

**Command:**
```bash
$ dig api.example.com @ns1.example.com
```

**Output:**
```
; <<>> DiG 9.10.6 <<>> api.example.com @ns1.example.com
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: SERVFAIL, id: 54321
;; flags: qr aa rd;
;; Query time: 2000 msec
```

**The authoritative server itself is returning SERVFAIL!** Not just the recursive resolver.

---

### STEP 3: Trace the full resolution path

**Command:**
```bash
$ dig +trace api.example.com
```

**Output:**
```
; <<>> DiG 9.10.6 <<>> +trace api.example.com

.			518400	IN	NS	a.root-servers.net.
;; Received 228 bytes from 192.168.1.1#53(192.168.1.1)
;; in 2 ms

com.			172800	IN	NS	a.gtld-servers.net.
;; Received 513 bytes from a.root-servers.net#53(a.root-servers.net)
;; in 23 ms

example.com.		172800	IN	NS	ns1.example.com.
;; Received 671 bytes from a.gtld-servers.net#53(a.gtld-servers.net)
;; in 12 ms

;; Query to for api.example.com at ns1.example.com
;; Got answer:
;; status: SERVFAIL  ← ✅ IDENTIFIED! Authoritative is broken
;; Received 5 bytes
```

**Root of the problem: ns1.example.com is returning SERVFAIL**

---

### STEP 4: SSH into the nameserver and check

**Command:**
```bash
$ ssh admin@ns1.example.com
```

Check if DNS daemon is running:
```bash
$ systemctl status named
● named.service - BIND DNS Server
   Loaded: loaded (/etc/systemd/system/named.service; enabled; vendor preset: enabled)
   Active: active (running) since Mon 2026-04-13 14:00:00 IST; 44 min ago
   PID: 1234
```

Check logs:
```bash
$ tail -50 /var/log/named/named.log
13-Apr-2026 14:00:15.123 [zone_loader/debug] Loading zone example.com from disk
13-Apr-2026 14:00:16.456 [resolver/error] **Zone example.com: DNSSEC validation failed**
13-Apr-2026 14:00:16.456 [zone_loader/error] **Zone example.com failed to load**
13-Apr-2026 14:00:17.789 [server/notice] No data source for zone example.com!
```

**ROOT CAUSE: DNSSEC validation failed!** The zone file has DNSSEC records but they're broken/expired.

---

### THE FIX (3 Options)

**Option A: Disable DNSSEC** (temporary, quick fix)
```bash
# Edit /etc/named.conf:
zone "example.com" {
    type master;
    file "/etc/named/zones/example.com.zone";
    dnssec-validation no;  ← Add this
};

# Reload:
$ sudo systemctl reload named

# Verify:
$ dig api.example.com @ns1.example.com
;; status: NOERROR  ✅
```

**Option B: Fix DNSSEC signing** (proper solution)
```bash
# Re-sign the zone with current keys:
$ sudo dnssec-signzone -o example.com /etc/named/zones/example.com.zone \
  /etc/named/keys/example.com.key

# Reload:
$ sudo systemctl reload named

# Verify:
$ dig api.example.com @ns1.example.com
;; status: NOERROR  ✅
```

**Option C: Use secondary nameserver**
```bash
# Query secondary instead:
$ dig api.example.com @ns2.example.com
api.example.com.	3600	IN	A	203.0.113.100
;; status: NOERROR  ← Secondary server didn't have DNSSEC issue!
```

---

### VERIFICATION (After fix)

**Command:**
```bash
$ dig api.example.com @ns1.example.com

; <<>> DiG 9.10.6 <<>> api.example.com @ns1.example.com
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 55555
;; flags: qr aa rd;
;; QUESTION SECTION:
;api.example.com.		IN	A
;; ANSWER SECTION:
api.example.com.	3600	IN	A	203.0.113.100
;; Query time: 6 msec
;; SERVER: ns1.example.com#53(ns1.example.com)
```

**Status: NOERROR** ✅ **FIXED!**

Also verify public resolvers updated:
```bash
$ dig api.example.com @8.8.8.8
;; status: NOERROR  ✅
api.example.com.	3600	IN	A	203.0.113.100
```

**Interview Answer:**
"SERVFAIL means the server had a problem processing the query. I'd query the authoritative directly to see if it's also failing. Then trace the full path with `dig +trace` to identify which server is failing. Finally, I'd check the nameserver logs (SSH in) to see what's wrong—usually DNSSEC validation, daemon not running, or zone not loaded."

---

## Quick Reference: Common DNS Errors

| Error | Meaning | Root Cause | Diagnosis | Fix |
|-------|---------|-----------|-----------|-----|
| **NXDOMAIN** | Domain doesn't exist | Record never created | `dig domain` → no answer | Create DNS record |
| **NOERROR + EMPTY** | Domain exists, no A record | Wrong record type | `dig domain` → NOERROR but 0 answers | Create A record |
| **SERVFAIL** | Server failed | Nameserver broken / DNSSEC issue | `dig +trace` shows which NS fails | SSH into NS, check logs, fix DNSSEC |
| **TIMEOUT** | No response | Resolver unreachable / network issue | `mtr` shows packet loss | Switch resolver or fix network |
| **Wrong IP** | Stale cached answer | TTL hasn't expired | `dig @authoritative` matches? | Wait for TTL / reduce TTL before migrations |
| **Intermittent** | Sometimes works, sometimes not | Packet loss / overloaded resolver | `mtr` shows % drop | Switch resolver / use TCP mode |

---

## How to Fix NXDOMAIN Error

### What is NXDOMAIN?

```
$ nslookup notexist.com
;; status: NXDOMAIN
** server can't find notexist.com: NXDOMAIN
```

**NXDOMAIN = "Non-Existent Domain"**
- The domain name doesn't exist
- The authoritative nameserver says: "I've never heard of this domain"
- This is a DNS problem, NOT a network problem

---

### Root Causes of NXDOMAIN

| Cause | How to Check |
|-------|---|
| **Domain never created** | Domain not registered or DNS record missing |
| **Typo in domain name** | You spelled it wrong (cubic3.com vs cubix3.com) |
| **Expired domain** | Domain registration expired |
| **Wrong TLD** | Trying .com instead of .org |
| **New domain, not propagated yet** | DNS propagation in progress (up to 48 hours) |
| **Delegated to wrong nameserver** | Nameserver address is incorrect |

---

### Fix 1: Verify Domain Exists (Step-by-Step)

**STEP 1: Is the domain registered?**

```bash
$ whois cubic3.com
```

**Output (domain registered):**
```
Domain Name: CUBIC3.COM
Registry Domain ID: D402887989-LROR
Registrar: NameCheap, Inc.
Registrar WHOIS Server: whois.namecheap.com
Registrar URL: http://www.namecheap.com
Updated Date: 2025-11-15
Creation Date: 2024-06-20
Registry Expiry Date: 2027-06-20  ← Domain is valid
Status: clientTransferProhibited
Registrant Organization: Cubic Inc
```

✅ **Domain is registered!** Check for NXDOMAIN reason.

**Output (domain NOT registered):**
```
No Found matching query.
```

❌ **Domain doesn't exist.** Must register it first.

---

**STEP 2: Are the nameservers registered?**

```bash
$ nslookup cubic3.com
```

**Output:**
```
Server:		8.8.8.8
Address:	8.8.8.8#53

** server can't find cubic3.com: NXDOMAIN
```

❌ **NXDOMAIN returned.** Nameservers not configured or broken.

**Check NS records at registrar:**
```bash
$ dig cubic3.com NS
```

**Output (NO NS records):**
```
; <<>> DiG 9.10.6 <<>> cubic3.com NS

; Got answer:
; status: NXDOMAIN
```

❌ **No nameservers configured!** Go to domain registrar and add nameservers.

**Output (NS records exist):**
```
cubic3.com.		172800	IN	NS	ns-130.awsdns-34.com.
cubic3.com.		172800	IN	NS	ns-1036.awsdns-01.com.
```

✅ **Nameservers exist.** Continue troubleshooting.

---

**STEP 3: Can you query the authoritative nameserver directly?**

```bash
$ dig cubic3.com @ns-130.awsdns-34.com
```

**Output (Authoritative HAS the record):**
```
; <<>> DiG 9.10.6 <<>> cubic3.com @ns-130.awsdns-34.com
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 55555
;; flags: qr aa rd;   ← AUTHORITATIVE!

cubic3.com.		3600	IN	A	35.189.126.202
```

✅ **DNS resolves at authoritative!** It's a **cache propagation issue** (fix: wait or reduce TTL).

**Output (Authoritative does NOT have record):**
```
; <<>> DiG 9.10.6 <<>> cubic3.com @ns-130.awsdns-34.com
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NXDOMAIN, id: 55555
;; flags: qr aa rd;
```

❌ **DNS record missing at authoritative!** Must create the DNS record.

---

### Fix 2: CREATE the DNS Record (If Missing)

**If authoritative returns NXDOMAIN, the DNS record doesn't exist.**

**For Route53 (AWS):**

1. Open AWS Route53 console
2. Find your hosted zone (cubic3.com)
3. Click "Create record"
4. Enter:
   - **Name:** cubic3.com (or subdomain)
   - **Type:** A
   - **Value:** Your app server IP (e.g., 35.189.126.202)
   - **TTL:** 300 (5 minutes for testing, 3600 for production)
5. Click "Create records"

**For GCP Cloud DNS:**

```bash
$ gcloud dns record-sets create cubic3.com \
    --rrdatas=35.189.126.202 \
    --ttl=300 \
    --type=A \
    --zone=cubic3-zone
```

**For Cloudflare:**

1. Go to DNS tab
2. Click "Add record"
3. Enter:
   - **Type:** A
   - **Name:** @ (or subdomain)
   - **IPv4 address:** 35.189.126.202
   - **TTL:** Auto (or 300)
4. Click "Save"

**For NameCheap/GoDaddy:**

1. Go to DNS management
2. Add/Edit A record
3. Enter IP address
4. Save changes

---

### Fix 3: VERIFY the Record Was Created

**STEP 1: Query authoritative immediately**

```bash
$ dig cubic3.com @ns-130.awsdns-34.com

cubic3.com.		300	IN	A	35.189.126.202
;; flags: qr aa rd;   ← AUTHORITATIVE!
```

✅ **Authoritative has it!** NXDOMAIN at public resolvers will expire soon.

---

**STEP 2: Wait for TTL to expire (automatic)**

If you set TTL=300 seconds, wait up to **5 minutes**. Then:

```bash
$ dig cubic3.com @8.8.8.8

cubic3.com.		300	IN	A	35.189.126.202
;; SERVER: 8.8.8.8#53(8.8.8.8)
```

✅ **Public resolver updated!** NXDOMAIN is gone.

---

**STEP 3: Verify across multiple resolvers**

```bash
$ dig cubic3.com @8.8.8.8
cubic3.com.		300	IN	A	35.189.126.202  ✅

$ dig cubic3.com @1.1.1.1
cubic3.com.		300	IN	A	35.189.126.202  ✅

$ dig cubic3.com @8.8.4.4
cubic3.com.		300	IN	A	35.189.126.202  ✅

$ nslookup cubic3.com
Name:	cubic3.com
Address: 35.189.126.202  ✅
```

**All resolvers now return the IP.** NXDOMAIN is **FIXED!** ✅

---

### Fix 4: NAMESERVERS are Wrong (Edge Case)

**If authoritative nameserver doesn't respond at all:**

```bash
$ dig cubic3.com @ns-130.awsdns-34.com

;; connection timed out
```

❌ **Nameserver is unreachable or doesn't exist.**

**Solution:**

1. Check nameserver IP is correct:
```bash
$ nslookup ns-130.awsdns-34.com
Name:	ns-130.awsdns-34.com
Address: 205.251.194.130
```

2. Verify it's in your registrar's nameserver list:
```bash
$ dig cubic3.com NS

cubic3.com.  NS  ns-130.awsdns-34.com.  ← Check if this matches registrar
cubic3.com.  NS  ns-1036.awsdns-01.com.
```

3. If nameservers are wrong, go to registrar and update them to the correct ones from Route53/GCP/Cloudflare.

---

### Fix 5: Check for Typos

**Did you spell it right?**

```bash
# Wrong (typo):
$ dig cubic3.com   ← Returns NXDOMAIN (doesn't exist)

# Check if domain exists with typos:
$ dig cubix3.com   ← Returns NXDOMAIN (doesn't exist)
$ dig cubic2.com   ← Returns NXDOMAIN (doesn't exist)

# Correct:
$ dig example.com  ← Returns IP (exists!)
```

**Always verify the domain name spelling!**

---

### Fix 6: Domain Recently Created (Propagation in Progress)

**Scenario:** Created domain 5 minutes ago, but getting NXDOMAIN

**Diagnosis:**

```bash
# Public resolver says it doesn't exist:
$ dig cubic3.com @8.8.8.8
;; status: NXDOMAIN

# But authoritative HAS it:
$ dig cubic3.com @ns-130.awsdns-34.com
;; status: NOERROR
cubic3.com.  A  35.189.126.202
```

**Root cause:** DNS propagation in progress (authoritative updated, but public caches haven't)

**Fix:** **Just wait!**

```
Timeline:
- 14:00:00 → Created domain in Route53
- 14:00:05 → Authoritative has it, public resolvers don't
- 14:05:00 → TTL expired (300 sec), public resolvers query again
- 14:05:10 → Public resolvers now cached it
```

**If you need it NOW:**

```bash
# Query authoritative directly (works immediately):
$ dig cubic3.com @ns-130.awsdns-34.com
cubic3.com.  A  35.189.126.202  ✅

# Or reduce TTL to 60 seconds BEFORE creating the record next time
```

---

### Interview-Ready NXDOMAIN Answer

> "NXDOMAIN means the domain doesn't exist at the authoritative nameserver. I'd first verify the domain is registered with `whois`. Then I'd check if nameservers are configured in the registrar settings. Next, I'd query the authoritative server directly with `dig @ns1` to see if it has the record. If it does, it's a cache propagation issue—just wait for the TTL to expire. If it doesn't, I need to create the DNS record in the DNS provider (Route53, Cloudflare, etc.). After creating, I'd verify with `dig @authoritative` first, then wait for public resolvers to update (up to the TTL value)."

---

### NXDOMAIN Troubleshooting Flowchart

```
Start: Getting NXDOMAIN error

├─ Is the domain registered?
│  ├─ NO → Register domain at registrar (NameCheap, GoDaddy, etc.)
│  └─ YES → Continue
│
├─ Are nameservers configured at registrar?
│  ├─ NO → Add nameservers (Route53, Cloudflare, etc.) to registrar
│  └─ YES → Continue
│
├─ Can you query authoritative directly?
│  $ dig domain.com @ns1.domain.com
│  ├─ Returns NXDOMAIN → DNS record missing, CREATE it
│  ├─ Returns NOERROR → Cache not updated yet, WAIT for TTL
│  └─ Times out → Nameserver unreachable, verify NS address
│
├─ Did you just create the record?
│  ├─ <5 minutes ago → WAIT (up to 5 minutes if TTL=300)
│  ├─ >1 hour ago → Something's wrong, redo above steps
│  └─ Verified at authoritative → WAIT more time
│
└─ ✅ NXDOMAIN should be GONE!
```

---

## TSE Diagnostic Checklist

```
ALWAYS follow this order (never skip steps):

1️⃣ RESOLVE DOMAIN
   $ nslookup domain.com
   → NXDOMAIN? DNS issue
   → Returns IP? Continue to next step

2️⃣ VERIFY WITH DIG (for more detail)
   $ dig domain.com @8.8.8.8 +stats
   → Status NOERROR? Good
   → Status SERVFAIL? Nameserver broken
   → Status NXDOMAIN? Domain doesn't exist
   → Slow query time (>500ms)? Resolver overloaded

3️⃣ QUERY AUTHORITATIVE (source of truth)
   $ dig domain.com @ns1.domain.com
   → Does it have 'aa' flag? Yes = authoritative
   → Same answer as public resolver? Yes = DNS is consistent
   → Different answer? = Cache mismatch, wait for TTL

4️⃣ REACH THE IP (network layer)
   $ ping <IP>
   → Timeout? Firewall/routing issue
   → Replies? Network working

5️⃣ REACH THE SERVICE (service layer)
   $ curl http://domain.com
   → HTTP 200? Service working
   → Connection refused? App not listening
   → Timeout? Network blocked

6️⃣ CHECK PROPAGATION (for global issues)
   $ dig domain.com @8.8.8.8
   $ dig domain.com @1.1.1.1
   $ dig domain.com @8.8.4.4
   → All same? Propagated globally
   → Different? Cache mismatch, wait or reduce TTL

7️⃣ IF SLOW/INTERMITTENT
   $ mtr -c 100 <resolver-ip>
   → Packet loss >5%? Network problem
   → <1%? Resolver overloaded → switch resolver

ESCALATE WITH EVIDENCE:
- DNS issue: "NXDOMAIN from 3 different resolvers, authoritative also doesn't have it"
- Cache issue: "Authoritative has 10.0.2.100, Google's resolver shows 10.0.1.50 (TTL expires in 1200 seconds)"
- Network issue: "Mtr shows 13% packet loss on hop 4 to resolver"
- Service issue: "DNS resolves, IP pings, but HTTP connection refused port 80"
```

---

## Interview-Ready Answers

### Answer Template 1: "Is this a DNS issue?"

> "I'd test DNS resolution with `nslookup` or `dig`. If the domain name doesn't translate to an IP (NXDOMAIN or timeout), it's a DNS issue. If DNS resolves successfully but the IP is unreachable or the service doesn't respond, then it's a network or application issue, not DNS.
>
> The key is to **isolate DNS separately** from network and application layers:
> 1. Does it resolve? (`nslookup`)
> 2. Is that IP reachable? (`ping`)
> 3. Does the service respond? (`curl`)
>
> Only step 1 is DNS. If step 1 fails, the problem is DNS. If it passes, DNS is working fine."

### Answer Template 2: "DNS works but returns wrong IP"

> "This is a cache mismatch. I'd query the authoritative server directly with `dig @ns1` to confirm the correct IP. If authoritative matches one resolver but not others, some caches are stale.
>
> The fix depends on urgency:
> - **Immediate:** Switch to a resolver that has the new record. Or query authoritative directly.
> - **Long-term:** Reduce TTL *before* migrations (from 3600 to 300 seconds), make the change, then raise TTL back. This makes future changes propagate in 5 minutes instead of an hour."

### Answer Template 3: "DNS sometimes times out"

> "Intermittent timeouts usually mean packet loss on the path or resolver overload. I'd:
> 1. Reproduce the issue with `dig` in a loop
> 2. Measure query times with `dig +stats`
> 3. Check packet loss with `mtr` on the resolver IP
> 4. Query authoritative directly to see if it's slow too
>
> If packet loss is >5%, it's a network issue (for infrastructure team). If authoritative is fast but resolver is slow, switch resolvers. If it's DNS server overload, increase capacity or distribute load."

---

## Summary: Your TSE Networking Superpower

You now know how to:
- ✅ Systematically test each DNS layer
- ✅ Read and interpret dig/nslookup output
- ✅ Isolate DNS from network and application issues
- ✅ Diagnose stale caches, packet loss, and server failures
- ✅ Escalate with **evidence**, not guesses

**Practice these scenarios until you can run the commands from memory. TSE interviews reward systematic thinking and evidence-based diagnosis.**



Here's your final DNS troubleshooting question list — trimmed, reshaped, and reordered by likely interview flow:

---

**Triage & methodology**

1. A user reports they can't reach a website. How do you determine if it's a DNS issue, and walk me through your triage steps?

2. Walk me through what happens when a browser resolves a domain name — from local cache all the way to an authoritative answer.

---

**Core concepts**

3. What's the difference between an authoritative DNS server and a recursive resolver? How does each behave during troubleshooting?

4. Explain the difference between A, CNAME, and NS records. Describe a troubleshooting scenario where confusing them caused a real problem.

5. What is negative caching (NXDOMAIN caching) and how can it cause issues after a misconfiguration is fixed?

---

**Operational troubleshooting**

6. A record was updated but users are still hitting the old IP. What are all the possible reasons — resolver TTL, CDN edge cache, OS cache — and how do you diagnose each?

7. A service is intermittently resolving to the wrong IP. What could cause this and how would you narrow it down?

8. How would you use `dig` or `nslookup` to verify a DNS record is propagating correctly? What flags and options matter most?

---

**Design tradeoffs**

9. How does TTL affect your troubleshooting strategy? What are the tradeoffs of setting it very low vs very high, and when would you change it proactively before an incident?

10. What is split-horizon DNS, how does it work, and describe a scenario where misconfiguring it causes a hard-to-diagnose issue?

---

That's 10 clean questions. Zone delegation is out. Split-horizon replaces it — it's a real operational concept that comes up in cloud environments and tests both conceptual and troubleshooting depth without being overly niche.

