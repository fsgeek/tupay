//! fexp: explicit-state explorer for the reference model of replay/spec-F.md.
//! Validation tool for the replay inputs; not an experimental artifact.
//! derives: J1.1, J1.3, J1.4, G1.1, G1.2, G1.3, G1.4
//!
//! Same transition system as ../tla/F.tla (read that file for the commented model); this is a
//! faster engine for it. Exhaustive DFS over the bounded space with a shared lock-free
//! fingerprint table, parallel with work donation. Every new state is checked:
//! a behaviour that has taken every step (Done) and carries a violation flag => FAIL.

use std::collections::hash_map::DefaultHasher;
use std::hash::{Hash, Hasher};
use std::sync::atomic::{AtomicBool, AtomicU64, AtomicUsize, Ordering};
use std::sync::{Arc, Mutex};
use std::time::{Duration, Instant};

const N: usize = 5;
const NONE: u8 = 255;
const MAXJ_CAP: usize = 8;
const SEL_COORD: u8 = 10;
const SEL_FOLL: u8 = 11;
const SEL_CRASHED: u8 = 12;

// roles
const F: u8 = 0;
const L: u8 = 1;
const C: u8 = 2;
// change op / phase
const OP_NONE: u8 = 0;
const OP_ADD: u8 = 1;
const OP_REMOVE: u8 = 2;
const PH_NONE: u8 = 0;
const PH_CATCH: u8 = 1;
const PH_WAIT: u8 = 2;
const PH_COMMIT: u8 = 3;
// actions
const A_NONE: u8 = 0;
const A_ADD: u8 = 1;
const A_REMOVE: u8 = 2;
const A_COMMAND: u8 = 3;
const A_CRASH: u8 = 4;
const A_RESTART: u8 = 5;
const A_CUT: u8 = 6;
const A_DROP: u8 = 7;
const A_HEAL: u8 = 8;
// reply status
const ST_OK: u8 = 1;
const ST_TIMEOUT: u8 = 2;
const ST_NOTCOORD: u8 = 3;
const ST_BUSY: u8 = 4;
const ST_INVALID: u8 = 5;

// ------------------------------------------------------------------ entries and journals
// entry: bits 8.. epoch, bit 7 isc, bits 0..6 payload (config mask or command id; 0 = noop)
#[inline]
fn e_ep(e: u16) -> u8 {
    (e >> 8) as u8
}
#[inline]
fn e_isc(e: u16) -> bool {
    e & 0x80 != 0
}
#[inline]
fn e_pay(e: u16) -> u8 {
    (e & 0x7f) as u8
}
fn cmd_e(ep: u8, c: u8) -> u16 {
    ((ep as u16) << 8) | (c as u16)
}
fn cfg_e(ep: u8, mask: u8) -> u16 {
    ((ep as u16) << 8) | 0x80 | (mask as u16)
}

#[derive(Clone, Copy, PartialEq, Eq, Hash, PartialOrd, Ord, Debug, Default)]
struct Jr {
    len: u8,
    e: [u16; MAXJ_CAP],
}
impl Jr {
    fn get(&self, k: usize) -> u16 {
        self.e[k - 1]
    } // 1-based
    fn push(&mut self, x: u16) {
        self.e[self.len as usize] = x;
        self.len += 1;
    }
    fn last_ep(&self) -> u8 {
        if self.len == 0 { 0 } else { e_ep(self.e[self.len as usize - 1]) }
    }
    fn cfg_idx(&self) -> usize {
        for k in (1..=self.len as usize).rev() {
            if e_isc(self.e[k - 1]) {
                return k;
            }
        }
        0
    }
    fn cfg_of(&self, init: u8) -> u8 {
        let k = self.cfg_idx();
        if k == 0 { init } else { e_pay(self.e[k - 1]) }
    }
    fn prefix(&self, n: usize) -> Jr {
        let mut j = Jr::default();
        for k in 0..n {
            j.e[k] = self.e[k];
        }
        j.len = n as u8;
        j
    }
    fn slice(&self, from1: usize, to1: usize) -> Jr {
        // entries from1..=to1 (1-based), empty if from1 > to1
        let mut j = Jr::default();
        if from1 >= 1 {
            let mut k = from1;
            while k <= to1 {
                j.push(self.e[k - 1]);
                k += 1;
            }
        }
        j
    }
}
fn cp(a: &Jr, b: &Jr) -> usize {
    let m = a.len.min(b.len) as usize;
    let mut k = 0;
    while k < m && a.e[k] == b.e[k] {
        k += 1;
    }
    k
}
#[inline]
fn pc(x: u8) -> u32 {
    x.count_ones()
}
#[inline]
fn maj(s: u8, c: u8) -> bool {
    2 * pc(s & c) > pc(c)
}
fn uptodate(lidx: u8, lep: u8, j: &Jr) -> bool {
    lep > j.last_ep() || (lep == j.last_ep() && lidx >= j.len)
}
fn j13ok(k: &Jr, init: u8) -> bool {
    for i in 1..=k.len as usize {
        let x = k.get(i);
        if e_isc(x) {
            let p = k.prefix(i - 1).cfg_of(init);
            if pc(p ^ e_pay(x)) != 1 {
                return false;
            }
        }
    }
    true
}

// ------------------------------------------------------------------ state
#[derive(Clone, Copy, PartialEq, Eq, Hash, Debug)]
struct Ch {
    op: u8,
    t: u8,
    ph: u8,
    idx: u8,
}
const NOCH: Ch = Ch { op: OP_NONE, t: NONE, ph: PH_NONE, idx: 0 };

#[derive(Clone, Copy, PartialEq, Eq, Hash, Debug)]
struct Mem {
    up: bool,
    ep: u8,
    vf: u8,
    jr: Jr,
    role: u8,
    ci: u8,
    votes: u8,
    ni: [u8; N],
    mi: [u8; N],
    ch: Ch,
}

#[derive(Clone, Copy, PartialEq, Eq, Hash, PartialOrd, Ord, Debug)]
struct Msg {
    ty: u8, // 0 RV, 1 AE
    src: u8,
    dst: u8,
    ep: u8,
    a: u8,
    b: u8,
    ents: Jr,
    ci: u8,
}

#[derive(Clone, Copy, PartialEq, Eq, Hash, Debug)]
struct Act {
    op: u8,
    t: u8,
    at: u8,
    cmd: u8,
    links: u32,
}
const NOACT: Act = Act { op: A_NONE, t: NONE, at: NONE, cmd: 0, links: 0 };

#[derive(Clone, PartialEq, Eq, Hash, Debug)]
struct State {
    st: [Mem; N],
    msgs: Vec<Msg>,
    down: u32,
    elec: Vec<(u8, u8, Jr)>,
    comm: Vec<(u8, u16, u8)>, // (idx, entry, epoch of committing coordinator)
    bad13: bool,
    bad14b: bool,
    lost: u8, // bound counter: replies lost although deliverable
    bad14k: bool, // diagnostic J1.4(b'): removal of an entry at or below the remover's own commitIndex
    tmo: u8,
    stp: u8,
    pend: Act,
    last_e: u8,
    last_c: u8,
    settle: u16,
}

#[inline]
fn link(s: u8, d: u8) -> u32 {
    1u32 << (s as u32 * 5 + d as u32)
}

// ------------------------------------------------------------------ events and scenario
#[derive(Clone, Copy, PartialEq, Eq, Debug)]
enum EvK {
    Start,
    Elected,
    Appended,
    Truncated,
    Committed,
    ConfigInEffect,
    ChangeRequested,
    ChangeReplied,
}
#[derive(Clone, Copy, Debug)]
struct Ev {
    k: EvK,
    member: u8,
    index: u8,
    epoch: u8,
    kind: u8, // 0 command 1 config
    op: u8,
    target: u8,
    status: u8,
    config: u8,
    from: u8,
}
fn ev(k: EvK, member: u8) -> Ev {
    Ev { k, member, index: 0, epoch: 0, kind: 0, op: 0, target: NONE, status: 0, config: 0, from: 0 }
}
// trigger filter fields
#[derive(Clone, Copy, Debug)]
enum Fld {
    Member,
    Index,
    Epoch,
    Kind,
    Op,
    Target,
    Status,
    From,
}
fn has_field(k: EvK, f: Fld) -> bool {
    use EvK::*;
    use Fld::*;
    match (k, f) {
        (_, Member) => true,
        (Elected, Epoch) => true,
        (Appended, Index) | (Appended, Epoch) | (Appended, Kind) => true,
        (Truncated, From) => true,
        (Committed, Index) | (Committed, Epoch) => true,
        (ConfigInEffect, Index) => true,
        (ChangeRequested, Op) | (ChangeRequested, Target) => true,
        (ChangeReplied, Op) | (ChangeReplied, Target) | (ChangeReplied, Status) => true,
        _ => false,
    }
}
fn field(e: &Ev, f: Fld) -> u8 {
    match f {
        Fld::Member => e.member,
        Fld::Index => e.index,
        Fld::Epoch => e.epoch,
        Fld::Kind => e.kind,
        Fld::Op => e.op,
        Fld::Target => e.target,
        Fld::Status => e.status,
        Fld::From => e.from,
    }
}
#[derive(Clone, Debug)]
struct Trig {
    k: EvK,
    f: Vec<(Fld, u8)>,
}
fn matches(t: &Trig, e: &Ev) -> bool {
    t.k == e.k && t.f.iter().all(|&(f, v)| has_field(e.k, f) && field(e, f) == v)
}
#[derive(Clone, Debug)]
struct ActSpec {
    op: u8,
    t: u8,
    at: u8,
    cmd: u8,
    links: Vec<(u8, u8)>,
}

struct Model {
    init: u8,
    gated: bool,
    maxe: u8,
    maxt: u8,
    maxj: u8,
    settle: u16,
    steps: Vec<(Trig, ActSpec)>,
    cmd_names: Vec<String>,
    fail_on: [bool; 5],
    prune: bool,
    maxlost: u8,
    maxt_pre: u8,
}

// ------------------------------------------------------------------ model
fn zero_mem() -> Mem {
    Mem { up: true, ep: 0, vf: NONE, jr: Jr::default(), role: F, ci: 0, votes: 0, ni: [0; N], mi: [0; N], ch: NOCH }
}

impl Model {
    fn ns(&self) -> u8 {
        self.steps.len() as u8
    }
    fn cfg(&self, r: &Mem) -> u8 {
        r.jr.cfg_of(self.init)
    }
    fn rv_of(&self, i: usize, r: &Mem, j: usize) -> Msg {
        Msg { ty: 0, src: i as u8, dst: j as u8, ep: r.ep, a: r.jr.len, b: r.jr.last_ep(), ents: Jr::default(), ci: 0 }
    }
    fn targets(&self, r: &Mem) -> u8 {
        let mut t = self.cfg(r);
        if r.ch.op == OP_ADD && r.ch.ph == PH_CATCH {
            t |= 1 << r.ch.t;
        }
        t
    }
    fn ae_of(&self, i: usize, r: &Mem, j: usize) -> Msg {
        let p = r.ni[j] as usize - 1;
        Msg {
            ty: 1,
            src: i as u8,
            dst: j as u8,
            ep: r.ep,
            a: p as u8,
            b: if p == 0 { 0 } else { e_ep(r.jr.get(p)) },
            ents: r.jr.slice(p + 1, r.jr.len as usize),
            ci: r.ci,
        }
    }
    fn bcast(&self, i: usize, r: &Mem, out: &mut Vec<Msg>) {
        if r.up && r.role == C {
            let t = self.targets(r);
            for j in 0..N {
                if j != i && t >> j & 1 == 1 {
                    out.push(self.ae_of(i, r, j));
                }
            }
        }
    }
    fn dead(&self, m: &Msg, s: &[Mem; N]) -> bool {
        let j = &s[m.dst as usize];
        let c = &s[m.src as usize];
        if m.ep < j.ep && c.ep >= j.ep {
            return true;
        }
        if m.ty == 0 {
            m.ep == j.ep
                && (!(c.ep == m.ep && c.role == L)
                    || (j.vf != NONE && (j.vf != m.src || c.votes >> m.dst & 1 == 1)))
        } else {
            let last = m.a as usize + m.ents.len as usize;
            if !(m.ep == j.ep && j.up) {
                return false;
            }
            if !(m.a == 0 || (m.a <= j.jr.len && e_ep(j.jr.get(m.a as usize)) == m.b)) {
                return false;
            }
            if last > j.jr.len as usize {
                return false;
            }
            for k in 1..=m.ents.len as usize {
                if j.jr.get(m.a as usize + k) != m.ents.get(k) {
                    return false;
                }
            }
            if (j.ci as usize) < (m.ci as usize).min(last) {
                return false;
            }
            !(c.ep == m.ep && c.role == C) || (c.mi[m.dst as usize] as usize >= last && c.ni[m.dst as usize] as usize >= last + 1)
        }
    }
    /// msgs' = {m in old ∪ add, sendable : not Dead(m, st')}
    fn set_msgs(&self, s: &mut State, add: &[Msg]) {
        let mut v: Vec<Msg> = Vec::with_capacity(s.msgs.len() + add.len());
        for m in s.msgs.iter() {
            if !self.dead(m, &s.st) {
                v.push(*m);
            }
        }
        for m in add {
            if s.down & link(m.src, m.dst) == 0 && !self.dead(m, &s.st) {
                v.push(*m);
            }
        }
        v.sort_unstable();
        v.dedup();
        s.msgs = v;
    }
    fn bump(&self, mut r: Mem, e: u8) -> Mem {
        if e > r.ep {
            r.ep = e;
            r.vf = NONE;
            r.role = F;
            r.votes = 0;
            r.ni = [0; N];
            r.mi = [0; N];
            r.ch = NOCH;
        }
        r
    }
    fn commit(&self, i: usize, mut r: Mem) -> Mem {
        let c = self.cfg(&r);
        let mut n = r.ci as usize;
        let len = r.jr.len as usize;
        let mut k = len;
        while k > r.ci as usize {
            if e_ep(r.jr.get(k)) == r.ep {
                let mut s: u8 = 1 << i;
                for j in 0..N {
                    if j != i && r.mi[j] as usize >= k {
                        s |= 1 << j;
                    }
                }
                if maj(s, c) {
                    n = k;
                    break;
                }
            }
            k -= 1;
        }
        r.ci = n as u8;
        if r.ch.ph == PH_COMMIT && r.ci >= r.ch.idx {
            if r.ch.op == OP_REMOVE && r.ch.t as usize == i {
                r.ch = NOCH;
                r.role = F;
                r.ni = [0; N];
                r.mi = [0; N];
            } else {
                r.ch = NOCH;
            }
        }
        r
    }
    fn become_coord(&self, i: usize, mut r: Mem) -> Mem {
        let l = r.jr.len;
        r.role = C;
        r.votes = 0;
        r.ni = [l + 1; N];
        r.mi = [0; N];
        r.ch = NOCH;
        if self.gated {
            let e = cmd_e(r.ep, 0);
            r.jr.push(e);
        }
        self.commit(i, r)
    }
    fn merge(&self, j: &Jr, p: usize, e: &Jr) -> Jr {
        let jl = j.len as usize;
        let el = e.len as usize;
        for k in 1..=el {
            if p + k <= jl && e_ep(j.get(p + k)) != e_ep(e.get(k)) {
                let mut out = j.prefix(p + k - 1);
                for x in k..=el {
                    out.push(e.get(x));
                }
                return out;
            }
        }
        if p + el > jl {
            let mut out = *j;
            for x in (jl - p + 1)..=el {
                out.push(e.get(x));
            }
            out
        } else {
            *j
        }
    }
    /// receiver side: (new record, reply (ep or -1, ok, a))
    fn recv(&self, s: &State, m: &Msg) -> (Mem, (i16, bool, u8)) {
        let r = self.bump(s.st[m.dst as usize], m.ep);
        if m.ty == 0 {
            let grant = m.ep == r.ep && (r.vf == NONE || r.vf == m.src) && uptodate(m.a, m.b, &r.jr);
            let mut r2 = r;
            if grant {
                r2.vf = m.src;
            }
            (r2, (r.ep as i16, grant, 0))
        } else {
            let mut r1 = r;
            r1.role = F;
            r1.votes = 0;
            let ok = m.a == 0 || (m.a <= r1.jr.len && e_ep(r1.jr.get(m.a as usize)) == m.b);
            let last = m.a + m.ents.len;
            if m.ep < r.ep {
                (r, (r.ep as i16, false, 0))
            } else if r.role == C {
                (r, (-1, false, 0))
            } else if !ok {
                (r1, (r1.ep as i16, false, 0))
            } else {
                let mut r2 = r1;
                r2.jr = self.merge(&r1.jr, m.a as usize, &m.ents);
                if m.ci > r1.ci {
                    r2.ci = r1.ci.max(m.ci.min(last));
                }
                (r2, (r1.ep as i16, true, last))
            }
        }
    }
    fn on_reply(&self, s: &State, m: &Msg, rep: (i16, bool, u8)) -> Mem {
        let si = m.src as usize;
        let j = m.dst as usize;
        let r = self.bump(s.st[si], rep.0 as u8);
        if m.ep != r.ep || rep.0 != r.ep as i16 {
            return r;
        }
        if m.ty == 0 {
            if r.role == L && rep.1 {
                let mut r2 = r;
                r2.votes |= 1 << j;
                if maj(r2.votes, self.cfg(&r)) {
                    self.become_coord(si, r2)
                } else {
                    r2
                }
            } else {
                r
            }
        } else if r.role == C {
            let mut r2 = r;
            if rep.1 {
                r2.mi[j] = r2.mi[j].max(rep.2);
                r2.ni[j] = r2.ni[j].max(rep.2 + 1);
                self.commit(si, r2)
            } else {
                r2.ni[j] = 1.max(r2.ni[j] as i16 - 1) as u8;
                r2
            }
        } else {
            r
        }
    }

    // -------------------------------------------------------------- events of one member's change
    fn diff_ev(&self, i: usize, a: &Mem, b: &Mem, out: &mut Vec<Ev>) {
        let (j, k) = (&a.jr, &b.jr);
        let c = cp(j, k);
        if a.role != C && b.role == C {
            let mut e = ev(EvK::Elected, i as u8);
            e.epoch = b.ep;
            e.config = j.cfg_of(self.init);
            out.push(e);
        }
        if c < j.len as usize {
            let mut e = ev(EvK::Truncated, i as u8);
            e.from = (c + 1) as u8;
            out.push(e);
        }
        for x in (c + 1)..=k.len as usize {
            let mut e = ev(EvK::Appended, i as u8);
            e.index = x as u8;
            e.epoch = e_ep(k.get(x));
            e.kind = if e_isc(k.get(x)) { 1 } else { 0 };
            out.push(e);
        }
        if j.cfg_idx() != k.cfg_idx() || (k.cfg_idx() > 0 && k.cfg_idx() > c) {
            let mut e = ev(EvK::ConfigInEffect, i as u8);
            e.config = k.cfg_of(self.init);
            e.index = k.cfg_idx() as u8;
            out.push(e);
        }
        if b.ci > a.ci {
            for x in (a.ci + 1)..=b.ci {
                let mut e = ev(EvK::Committed, i as u8);
                e.index = x;
                e.epoch = e_ep(k.get(x as usize));
                out.push(e);
            }
        }
        if a.ch.ph == PH_COMMIT && b.ch.op == OP_NONE && b.up && b.ci >= a.ch.idx {
            let mut e = ev(EvK::ChangeReplied, i as u8);
            e.op = a.ch.op;
            e.target = a.ch.t;
            e.status = ST_OK;
            out.push(e);
        }
    }

    fn resolve(&self, sp: &ActSpec, le: u8, lc: u8, st: &[Mem; N]) -> Vec<Act> {
        let mut names = vec![sp.t, sp.at];
        for &(a, b) in &sp.links {
            names.push(a);
            names.push(b);
        }
        if names.contains(&SEL_COORD) && le == NONE {
            eprintln!("scenario rejected: coordinator before any Elected");
            std::process::exit(3);
        }
        if names.contains(&SEL_CRASHED) && lc == NONE {
            eprintln!("scenario rejected: crashed before any crash");
            std::process::exit(3);
        }
        let fs: Vec<u8> = if names.contains(&SEL_FOLL) {
            (0..N as u8).filter(|&f| st[f as usize].up && f != le).collect()
        } else {
            vec![NONE]
        };
        let r = |x: u8, f: u8| -> u8 {
            match x {
                SEL_COORD => le,
                SEL_CRASHED => lc,
                SEL_FOLL => f,
                _ => x,
            }
        };
        fs.iter()
            .map(|&f| {
                let mut links = 0u32;
                for &(a, b) in &sp.links {
                    let (x, y) = (r(a, f), r(b, f));
                    if x != y {
                        links |= link(x, y);
                    }
                }
                Act { op: sp.op, t: r(sp.t, f), at: r(sp.at, f), cmd: sp.cmd, links }
            })
            .collect()
    }

    /// ghosts, then the scenario driver; pushes 0 or more successors
    fn post(&self, old: &State, mut nw: State, l: &[usize], is_env: bool, xev: Vec<Ev>, out: &mut Vec<State>, info: &mut Option<Vec<(State, Vec<Ev>, String)>>) {
        for &i in l {
            if nw.st[i].jr.len > self.maxj {
                return;
            }
        }
        // ghosts
        for &i in l {
            let (a, b) = (&old.st[i], &nw.st[i]);
            if a.role != C && b.role == C {
                let rec = (b.ep, i as u8, a.jr);
                if !nw.elec.contains(&rec) {
                    nw.elec.push(rec);
                    nw.elec.sort_unstable();
                }
            }
        }
        let mut newc: Vec<(u8, u16, u8)> = Vec::new();
        for &i in l {
            let (a, b) = (&old.st[i], &nw.st[i]);
            if b.ci > a.ci && (b.role == C || (a.role == C && a.ep == b.ep)) {
                for k in 1..=b.ci as usize {
                    newc.push((k as u8, b.jr.get(k), b.ep));
                }
            }
        }
        for c in newc {
            if !old.comm.iter().any(|d| d.0 == c.0 && d.1 == c.1 && d.2 <= c.2) && !nw.comm.contains(&c) {
                nw.comm.push(c);
            }
        }
        nw.comm.sort_unstable();
        for &i in l {
            if !j13ok(&nw.st[i].jr, self.init) {
                nw.bad13 = true;
            }
            let j = &old.st[i].jr;
            let c = cp(j, &nw.st[i].jr);
            for k in (c + 1)..=j.len as usize {
                let e = j.get(k);
                if nw.comm.iter().any(|d| d.0 as usize == k && d.1 == e) {
                    nw.bad14b = true;
                }
                if k <= old.st[i].ci as usize {
                    nw.bad14k = true;
                }
            }
        }
        // events
        let mut evs = xev;
        let mut seen = 0u8;
        for &i in l {
            if seen >> i & 1 == 1 {
                continue;
            }
            seen |= 1 << i;
            self.diff_ev(i, &old.st[i], &nw.st[i], &mut evs);
        }
        // scenario
        let ns = self.ns();
        let armed = if is_env { old.stp + 1 } else { old.stp };
        let can = armed <= ns && (is_env || old.pend.op == A_NONE);
        let mut kfire: Option<usize> = None;
        if can {
            let t = &self.steps[armed as usize - 1].0;
            for (k, e) in evs.iter().enumerate() {
                if matches(t, e) {
                    kfire = Some(k);
                    break;
                }
            }
        }
        let le_upto = |k: usize| -> u8 {
            let mut le = old.last_e;
            for e in evs.iter().take(k + 1) {
                if e.k == EvK::Elected {
                    le = e.member;
                }
            }
            le
        };
        let lc = if is_env && old.pend.op == A_CRASH { old.pend.t } else { old.last_c };
        nw.stp = armed;
        nw.last_e = if evs.is_empty() { old.last_e } else { le_upto(evs.len() - 1) };
        nw.last_c = lc;
        nw.settle = if armed > ns { if is_env { 0 } else { old.settle + evs.len() as u16 } } else { 0 };
        if nw.settle > self.settle {
            return;
        }
        match kfire {
            Some(k) => {
                let r = self.resolve(&self.steps[armed as usize - 1].1, le_upto(k), lc, &nw.st);
                if r.is_empty() {
                    nw.pend = NOACT;
                    push(out, info, nw, &evs);
                } else {
                    for a in r {
                        let mut s2 = nw.clone();
                        s2.pend = a;
                        push(out, info, s2, &evs);
                    }
                }
            }
            None => {
                nw.pend = if is_env { NOACT } else { old.pend };
                push(out, info, nw, &evs);
            }
        }
    }

    // -------------------------------------------------------------- successors
    fn succs(&self, s: &State, out: &mut Vec<State>, info: &mut Option<Vec<(State, Vec<Ev>, String)>>) {
        let mut add: Vec<Msg> = Vec::with_capacity(8);
        for i in 0..N {
            let r = s.st[i];
            // Timeout
            if r.up && r.role != C && r.ep + 1 <= self.maxe && s.tmo < self.maxt && (s.stp > self.ns() || s.tmo < self.maxt_pre) {
                set_label(info.is_some(), || format!("{} times out", mname(i as u8)));
                let mut r1 = r;
                r1.ep = r.ep + 1;
                r1.vf = i as u8;
                r1.role = L;
                r1.votes = 1 << i;
                r1.ni = [0; N];
                r1.mi = [0; N];
                r1.ch = NOCH;
                let c = self.cfg(&r);
                let r2 = if maj(1 << i, c) { self.become_coord(i, r1) } else { r1 };
                let mut nw = s.clone();
                nw.st[i] = r2;
                nw.tmo += 1;
                add.clear();
                for j in 0..N {
                    if j != i && c >> j & 1 == 1 {
                        add.push(self.rv_of(i, &r1, j));
                    }
                }
                self.bcast(i, &r2, &mut add);
                self.set_msgs(&mut nw, &add);
                self.post(s, nw, &[i], false, vec![], out, info);
            }
            // Proceed
            if r.up && r.role == C {
                set_label(info.is_some(), || format!("{} proceeds with its change", mname(i as u8)));
                if r.ch.ph == PH_CATCH && r.mi[r.ch.t as usize] >= r.jr.len {
                    let mut nw = s.clone();
                    nw.st[i].ch.ph = PH_WAIT;
                    self.post(s, nw, &[i], false, vec![], out, info);
                }
                if r.ch.ph == PH_WAIT
                    && r.jr.cfg_idx() <= r.ci as usize
                    && (!self.gated || (1..=r.ci as usize).any(|k| e_ep(r.jr.get(k)) == r.ep))
                {
                    let c = self.cfg(&r);
                    let t = r.ch.t;
                    let newc = if r.ch.op == OP_ADD { c | (1 << t) } else { c & !(1 << t) };
                    let mut r2 = r;
                    if (r2.jr.len as usize) < MAXJ_CAP {
                        r2.jr.push(cfg_e(r.ep, newc));
                        r2.ch.ph = PH_COMMIT;
                        r2.ch.idx = r2.jr.len;
                        let r2 = self.commit(i, r2);
                        let mut nw = s.clone();
                        nw.st[i] = r2;
                        add.clear();
                        self.bcast(i, &r2, &mut add);
                        self.set_msgs(&mut nw, &add);
                        self.post(s, nw, &[i], false, vec![], out, info);
                    }
                }
                // CatchTimeout
                if r.ch.ph == PH_CATCH {
                    set_label(info.is_some(), || format!("{} catch-up times out", mname(i as u8)));
                    let mut nw = s.clone();
                    nw.st[i].ch = NOCH;
                    self.set_msgs(&mut nw, &[]);
                    let mut e = ev(EvK::ChangeReplied, i as u8);
                    e.op = r.ch.op;
                    e.target = r.ch.t;
                    e.status = ST_TIMEOUT;
                    self.post(s, nw, &[i], false, vec![e], out, info);
                }
            }
            // retries
            for j in 0..N {
                if j == i || s.down & link(i as u8, j as u8) != 0 || !r.up {
                    continue;
                }
                let m = if r.role == L && self.cfg(&r) >> j & 1 == 1 {
                    Some(self.rv_of(i, &r, j))
                } else if r.role == C && self.targets(&r) >> j & 1 == 1 {
                    Some(self.ae_of(i, &r, j))
                } else {
                    None
                };
                if let Some(m) = m {
                    if s.msgs.binary_search(&m).is_err() && !self.dead(&m, &s.st) {
                        let mut nw = s.clone();
                        let pos = nw.msgs.binary_search(&m).unwrap_err();
                        nw.msgs.insert(pos, m);
                        set_label(info.is_some(), || format!("retry {}", msg_s(self, &m)));
                        push(out, info, nw, &[]);
                    }
                }
            }
        }
        // Deliver
        for m in s.msgs.iter() {
            let d = m.dst as usize;
            let si = m.src as usize;
            if !s.st[d].up || s.down & link(m.src, m.dst) != 0 {
                continue;
            }
            let (rr, rep) = self.recv(s, m);
            let can_reply = rep.0 >= 0 && s.st[si].up && s.down & link(m.dst, m.src) == 0;
            for wr in [false, true] {
                if wr && !can_reply {
                    continue;
                }
                // a deliverable reply that is lost uses the loss budget
                if !wr && can_reply && s.lost >= self.maxlost {
                    continue;
                }
                let rs = if wr { self.on_reply(s, m, rep) } else { s.st[si] };
                set_label(info.is_some(), || format!("deliver {}{}", msg_s(self, m), if wr { " (+reply)" } else { " (reply lost)" }));
                let mut nw = s.clone();
                nw.st[d] = rr;
                nw.st[si] = rs;
                if !wr && can_reply && self.maxlost != 255 {
                    nw.lost += 1;
                }
                add.clear();
                self.bcast(si, &rs, &mut add);
                self.set_msgs(&mut nw, &add);
                self.post(s, nw, &[d, si], false, vec![], out, info);
            }
        }
        // Environment
        let p = s.pend;
        if p.op != A_NONE {
            set_label(info.is_some(), || format!("STEP {} ACTION: {}", s.stp, act_s(&p, self)));
            match p.op {
                A_ADD | A_REMOVE => {
                    let a = p.at as usize;
                    let r = s.st[a];
                    let mut rq = ev(EvK::ChangeRequested, p.at);
                    rq.op = if p.op == A_ADD { OP_ADD } else { OP_REMOVE };
                    rq.target = p.t;
                    let rep = |st: u8| {
                        let mut e = ev(EvK::ChangeReplied, p.at);
                        e.op = rq.op;
                        e.target = p.t;
                        e.status = st;
                        e
                    };
                    let c = self.cfg(&r);
                    if !r.up {
                        self.post(s, s.clone(), &[a], true, vec![], out, info);
                    } else if r.role != C {
                        self.post(s, s.clone(), &[a], true, vec![rq, rep(ST_NOTCOORD)], out, info);
                    } else if r.ch.op != OP_NONE {
                        self.post(s, s.clone(), &[a], true, vec![rq, rep(ST_BUSY)], out, info);
                    } else if (p.op == A_ADD) == (c >> p.t & 1 == 1) {
                        self.post(s, s.clone(), &[a], true, vec![rq, rep(ST_INVALID)], out, info);
                    } else {
                        let mut r2 = r;
                        r2.ch = Ch {
                            op: rq.op,
                            t: p.t,
                            idx: 0,
                            ph: if p.op == A_ADD && s.st[p.t as usize].jr != r.jr { PH_CATCH } else { PH_WAIT },
                        };
                        let mut nw = s.clone();
                        nw.st[a] = r2;
                        add.clear();
                        self.bcast(a, &r2, &mut add);
                        self.set_msgs(&mut nw, &add);
                        self.post(s, nw, &[a], true, vec![rq], out, info);
                    }
                }
                A_COMMAND => {
                    let a = p.at as usize;
                    let r = s.st[a];
                    if r.up && r.role == C {
                        if (r.jr.len as usize) < MAXJ_CAP {
                            let mut r2 = r;
                            r2.jr.push(cmd_e(r.ep, p.cmd));
                            let r2 = self.commit(a, r2);
                            let mut nw = s.clone();
                            nw.st[a] = r2;
                            add.clear();
                            self.bcast(a, &r2, &mut add);
                            self.set_msgs(&mut nw, &add);
                            self.post(s, nw, &[a], true, vec![], out, info);
                        }
                    } else {
                        self.post(s, s.clone(), &[a], true, vec![], out, info);
                    }
                }
                A_CRASH => {
                    let t = p.t as usize;
                    let mut nw = s.clone();
                    let r = &mut nw.st[t];
                    r.up = false;
                    r.role = F;
                    r.ci = 0;
                    r.votes = 0;
                    r.ni = [0; N];
                    r.mi = [0; N];
                    r.ch = NOCH;
                    self.set_msgs(&mut nw, &[]);
                    self.post(s, nw, &[t], true, vec![], out, info);
                }
                A_RESTART => {
                    let t = p.t as usize;
                    let mut nw = s.clone();
                    nw.st[t].up = true;
                    self.set_msgs(&mut nw, &[]);
                    self.post(s, nw, &[t], true, vec![], out, info);
                }
                A_CUT | A_DROP | A_HEAL => {
                    let mut nw = s.clone();
                    if p.op == A_HEAL {
                        nw.down = 0;
                    } else {
                        nw.down |= p.links;
                        if p.op == A_CUT {
                            for x in 0..5u8 {
                                for y in 0..5u8 {
                                    if p.links & link(x, y) != 0 {
                                        nw.down |= link(y, x);
                                    }
                                }
                            }
                        }
                    }
                    self.post(s, nw, &[0], true, vec![], out, info);
                }
                _ => {}
            }
        }
    }

    fn initial(&self) -> State {
        let mut pend = NOACT;
        if let Some((t, a)) = self.steps.first() {
            if t.k == EvK::Start {
                let mut links = 0;
                for &(x, y) in &a.links {
                    if x != y {
                        links |= link(x, y);
                    }
                }
                pend = Act { op: a.op, t: a.t, at: a.at, cmd: a.cmd, links };
            }
        }
        State {
            st: [zero_mem(); N],
            msgs: vec![],
            down: 0,
            elec: vec![],
            comm: vec![],
            bad13: false,
            bad14b: false,
            bad14k: false,
            lost: 0,
            tmo: 0,
            stp: 1,
            pend,
            last_e: NONE,
            last_c: NONE,
            settle: 0,
        }
    }

    /// violation flags: (J1.1, J1.3, J1.4a, J1.4b)
    fn viol(&self, s: &State) -> [bool; 5] {
        let mut v = [false; 5];
        for a in &s.elec {
            for b in &s.elec {
                if a.0 == b.0 && a.1 != b.1 {
                    v[0] = true;
                }
            }
        }
        v[1] = s.bad13;
        for r in &s.elec {
            for c in &s.comm {
                if c.2 < r.0 && !(r.2.len >= c.0 && r.2.get(c.0 as usize) == c.1) {
                    v[2] = true;
                }
            }
        }
        v[3] = s.bad14b;
        v[4] = s.bad14k;
        v
    }
    /// false if the remaining Elected triggers cannot all fire: each needs an election, and an
    /// election needs a timeout still allowed or a current candidate. Such prefixes are not
    /// prefixes of any behaviour that takes every step, so the format does not explore them.
    fn can_complete(&self, s: &State) -> bool {
        let first = if s.pend.op != A_NONE { s.stp as usize + 1 } else { s.stp as usize };
        let need = self.steps.iter().skip(first.saturating_sub(1)).filter(|(t, _)| t.k == EvK::Elected).count();
        if need == 0 {
            return true;
        }
        let cands = s.st.iter().filter(|r| r.up && r.role == L).count();
        need <= (self.maxt.min(self.maxt_pre).saturating_sub(s.tmo)) as usize + cands
    }
    fn done(&self, s: &State) -> bool {
        s.stp > self.ns()
    }
}

thread_local! {
    static LABEL: std::cell::RefCell<String> = std::cell::RefCell::new(String::new());
}
fn set_label(on: bool, f: impl FnOnce() -> String) {
    if on {
        LABEL.with(|l| *l.borrow_mut() = f());
    }
}
fn push(out: &mut Vec<State>, info: &mut Option<Vec<(State, Vec<Ev>, String)>>, s: State, evs: &[Ev]) {
    if let Some(v) = info.as_mut() {
        v.push((s.clone(), evs.to_vec(), LABEL.with(|l| l.borrow().clone())));
    }
    out.push(s);
}

// ------------------------------------------------------------------ fingerprints
fn fp(s: &State) -> u64 {
    let mut h = DefaultHasher::new();
    s.hash(&mut h);
    let x = h.finish();
    // second, independent mixing to spread bits; never 0
    let mut z = x ^ 0x9E37_79B9_7F4A_7C15;
    z = (z ^ (z >> 30)).wrapping_mul(0xBF58_476D_1CE4_E5B9);
    z = (z ^ (z >> 27)).wrapping_mul(0x94D0_49BB_1331_11EB);
    z ^= z >> 31;
    if z == 0 { 1 } else { z }
}

struct Table {
    t: Vec<AtomicU64>,
    mask: usize,
    count: AtomicUsize,
}
impl Table {
    fn new(bits: u32) -> Table {
        let n = 1usize << bits;
        let mut t = Vec::with_capacity(n);
        for _ in 0..n {
            t.push(AtomicU64::new(0));
        }
        Table { t, mask: n - 1, count: AtomicUsize::new(0) }
    }
    /// true if newly inserted
    fn insert(&self, f: u64) -> bool {
        let mut i = (f as usize) & self.mask;
        loop {
            let cur = self.t[i].load(Ordering::Relaxed);
            if cur == f {
                return false;
            }
            if cur == 0 {
                match self.t[i].compare_exchange(0, f, Ordering::Relaxed, Ordering::Relaxed) {
                    Ok(_) => {
                        self.count.fetch_add(1, Ordering::Relaxed);
                        return true;
                    }
                    Err(v) => {
                        if v == f {
                            return false;
                        }
                    }
                }
            }
            i = (i + 1) & self.mask;
        }
    }
}

// ------------------------------------------------------------------ exploration
struct Item {
    state: State,
    prefix: Arc<Vec<State>>, // init .. parent of state
}
struct Shared {
    queue: Mutex<Vec<Item>>,
    active: AtomicUsize,
    stop: AtomicBool,
    table: Table,
    done_states: AtomicU64,
    fail: Mutex<Option<(Vec<State>, [bool; 5])>>,
    anyviol: Mutex<Vec<Option<(Vec<State>, bool)>>>, // per flag: first witness, and whether Done
    reason: Mutex<String>,
}

fn explore(model: Arc<Model>, threads: usize, bits: u32, limit: Duration) -> Arc<Shared> {
    let sh = Arc::new(Shared {
        queue: Mutex::new(vec![]),
        active: AtomicUsize::new(0),
        stop: AtomicBool::new(false),
        table: Table::new(bits),
        done_states: AtomicU64::new(0),
        fail: Mutex::new(None),
        anyviol: Mutex::new(vec![None, None, None, None, None]),
        reason: Mutex::new(String::new()),
    });
    let init = model.initial();
    sh.table.insert(fp(&init));
    sh.queue.lock().unwrap().push(Item { state: init, prefix: Arc::new(vec![]) });
    let t0 = Instant::now();
    let cap = (sh.table.mask + 1) / 10 * 8;
    let mut hs = vec![];
    for _ in 0..threads {
        let sh = sh.clone();
        let model = model.clone();
        hs.push(std::thread::spawn(move || worker(&model, &sh, threads, t0, limit, cap)));
    }
    // progress
    let shp = sh.clone();
    let prog = std::thread::spawn(move || {
        let mut last = 0;
        while !shp.stop.load(Ordering::Relaxed) {
            std::thread::sleep(Duration::from_millis(500));
            let el = t0.elapsed().as_secs();
            if el >= last + 30 {
                last = el;
                eprintln!("progress {}s distinct={} done_states={} queue={}", el, shp.table.count.load(Ordering::Relaxed),
                          shp.done_states.load(Ordering::Relaxed), shp.queue.lock().unwrap().len());
            }
        }
    });
    for h in hs {
        h.join().unwrap();
    }
    sh.stop.store(true, Ordering::Relaxed);
    prog.join().unwrap();
    sh
}

struct Frame {
    state: State,
    succs: Vec<State>,
    next: usize,
}

fn worker(model: &Model, sh: &Shared, threads: usize, t0: Instant, limit: Duration, cap: usize) {
    let mut buf: Vec<State> = Vec::new();
    let mut none: Option<Vec<(State, Vec<Ev>, String)>> = None;
    loop {
        if sh.stop.load(Ordering::Relaxed) {
            return;
        }
        let item = {
            let mut q = sh.queue.lock().unwrap();
            match q.pop() {
                Some(it) => {
                    sh.active.fetch_add(1, Ordering::SeqCst);
                    Some(it)
                }
                None => {
                    if sh.active.load(Ordering::SeqCst) == 0 {
                        return;
                    }
                    None
                }
            }
        };
        let item = match item {
            Some(it) => it,
            None => {
                std::thread::sleep(Duration::from_micros(200));
                continue;
            }
        };
        // DFS from item
        let mut frames: Vec<Frame> = Vec::new();
        let expand = |s: &State, buf: &mut Vec<State>, none: &mut Option<Vec<(State, Vec<Ev>, String)>>, frames: &Vec<Frame>, item: &Item| -> Vec<State> {
            buf.clear();
            model.succs(s, buf, none);
            let mut v = Vec::new();
            for x in buf.drain(..) {
                if model.prune && !model.can_complete(&x) {
                    continue;
                }
                if sh.table.insert(fp(&x)) {
                    let vi = model.viol(&x);
                    let any = vi.iter().any(|&b| b);
                    let dn = model.done(&x);
                    if dn {
                        sh.done_states.fetch_add(1, Ordering::Relaxed);
                    }
                    if any {
                        let mk = || {
                            let mut tr: Vec<State> = item.prefix.as_ref().clone();
                            for f in frames.iter() {
                                tr.push(f.state.clone());
                            }
                            tr.push(s.clone());
                            tr.push(x.clone());
                            tr
                        };
                        {
                            let mut a = sh.anyviol.lock().unwrap();
                            for k in 0..5 {
                                if vi[k] && (a[k].is_none() || (dn && !a[k].as_ref().unwrap().1)) {
                                    a[k] = Some((mk(), dn));
                                }
                            }
                        }
                        if dn && (0..5).any(|k| vi[k] && model.fail_on[k]) {
                            let mut f = sh.fail.lock().unwrap();
                            if f.is_none() {
                                *f = Some((mk(), vi));
                            }
                            sh.stop.store(true, Ordering::Relaxed);
                        }
                    }
                    v.push(x);
                }
            }
            v
        };
        let s0 = item.state.clone();
        let sc = expand(&s0, &mut buf, &mut none, &frames, &item);
        frames.push(Frame { state: s0, succs: sc, next: 0 });
        let mut steps: u64 = 0;
        while let Some(top) = frames.last_mut() {
            if sh.stop.load(Ordering::Relaxed) {
                break;
            }
            if top.next < top.succs.len() {
                let x = std::mem::replace(&mut top.succs[top.next], model.initial());
                top.next += 1;
                let sc = expand(&x, &mut buf, &mut none, &frames, &item);
                frames.push(Frame { state: x, succs: sc, next: 0 });
                steps += 1;
                if steps % 2048 == 0 {
                    if t0.elapsed() > limit {
                        *sh.reason.lock().unwrap() = format!("wall-clock limit {}s", limit.as_secs());
                        sh.stop.store(true, Ordering::Relaxed);
                        break;
                    }
                    if sh.table.count.load(Ordering::Relaxed) > cap {
                        *sh.reason.lock().unwrap() = "fingerprint table 80% full".to_string();
                        sh.stop.store(true, Ordering::Relaxed);
                        break;
                    }
                    // donate work if others are idle
                    let qlen = sh.queue.lock().unwrap().len();
                    if qlen < threads {
                        for k in 0..frames.len() {
                            let rem = frames[k].succs.len() - frames[k].next;
                            if rem >= 2 {
                                let give = rem / 2;
                                let mut pre: Vec<State> = item.prefix.as_ref().clone();
                                for f in frames.iter().take(k + 1) {
                                    pre.push(f.state.clone());
                                }
                                let pre = Arc::new(pre);
                                let fr = &mut frames[k];
                                let mut q = sh.queue.lock().unwrap();
                                for _ in 0..give {
                                    let x = fr.succs.pop().unwrap();
                                    q.push(Item { state: x, prefix: pre.clone() });
                                }
                                break;
                            }
                        }
                    }
                }
            } else {
                frames.pop();
            }
        }
        sh.active.fetch_sub(1, Ordering::SeqCst);
    }
}

// ------------------------------------------------------------------ rendering
fn mname(i: u8) -> String {
    match i {
        NONE => "none".into(),
        _ => format!("m{}", i + 1),
    }
}
fn mask_s(m: u8) -> String {
    (0..5).filter(|i| m >> i & 1 == 1).map(|i| mname(i)).collect::<Vec<_>>().join(",")
}
fn ent_s(model: &Model, e: u16) -> String {
    if e_isc(e) {
        format!("e{}:cfg{{{}}}", e_ep(e), mask_s(e_pay(e)))
    } else {
        format!("e{}:{}", e_ep(e), model.cmd_names.get(e_pay(e) as usize).cloned().unwrap_or("?".into()))
    }
}
fn jr_s(model: &Model, j: &Jr) -> String {
    format!("[{}]", (1..=j.len as usize).map(|k| ent_s(model, j.get(k))).collect::<Vec<_>>().join(" "))
}
fn status_s(s: u8) -> &'static str {
    match s {
        ST_OK => "ok",
        ST_TIMEOUT => "timeout",
        ST_NOTCOORD => "not coordinator",
        ST_BUSY => "busy",
        ST_INVALID => "invalid",
        _ => "?",
    }
}
fn ev_s(_model: &Model, e: &Ev) -> String {
    let m = mname(e.member);
    let op = |o: u8| if o == OP_ADD { "add" } else { "remove" };
    match e.k {
        EvK::Elected => format!("Elected({}, e{}, {{{}}})", m, e.epoch, mask_s(e.config)),
        EvK::Appended => format!("Appended({}, {}, e{}, {})", m, e.index, e.epoch, if e.kind == 1 { "config" } else { "command" }),
        EvK::Truncated => format!("Truncated({}, from {})", m, e.from),
        EvK::Committed => format!("Committed({}, {}, e{})", m, e.index, e.epoch),
        EvK::ConfigInEffect => format!("ConfigInEffect({}, {{{}}}, {})", m, mask_s(e.config), e.index),
        EvK::ChangeRequested => format!("ChangeRequested({}, {} {})", m, op(e.op), mname(e.target)),
        EvK::ChangeReplied => format!("ChangeReplied({}, {} {}, {})", m, op(e.op), mname(e.target), status_s(e.status)),
        EvK::Start => "start".into(),
    }
}
fn act_s(a: &Act, model: &Model) -> String {
    let links = || {
        let mut v = vec![];
        for x in 0..5u8 {
            for y in 0..5u8 {
                if a.links & link(x, y) != 0 {
                    v.push(format!("{}>{}", mname(x), mname(y)));
                }
            }
        }
        v.join(" ")
    };
    match a.op {
        A_ADD => format!("add {} at {}", mname(a.t), mname(a.at)),
        A_REMOVE => format!("remove {} at {}", mname(a.t), mname(a.at)),
        A_COMMAND => format!("command {} at {}", model.cmd_names[a.cmd as usize], mname(a.at)),
        A_CRASH => format!("crash {}", mname(a.t)),
        A_RESTART => format!("restart {}", mname(a.t)),
        A_CUT => format!("cut {}", links()),
        A_DROP => format!("drop {}", links()),
        A_HEAL => "heal".into(),
        _ => "none".into(),
    }
}
fn msg_s(model: &Model, m: &Msg) -> String {
    if m.ty == 0 {
        format!("ballot {}->{} e{} last=({},e{})", mname(m.src), mname(m.dst), m.ep, m.a, m.b)
    } else {
        format!("extend {}->{} e{} prev=({},e{}) {} ci={}", mname(m.src), mname(m.dst), m.ep, m.a, m.b, jr_s(model, &m.ents), m.ci)
    }
}

/// describe the transition a -> b (re-derived by regenerating a's successors)
fn describe(model: &Model, a: &State, b: &State) -> String {
    let mut out = vec![];
    let mut info = Some(vec![]);
    model.succs(a, &mut out, &mut info);
    let info = info.unwrap();
    let found = info.iter().find(|(s, _, _)| s == b);
    let evs = found.map(|(_, e, _)| e.clone());
    let mut parts: Vec<String> = vec![];
    if let Some((_, _, l)) = found {
        parts.push(l.clone());
    }
    // what changed
    let newm: Vec<&Msg> = b.msgs.iter().filter(|m| a.msgs.binary_search(m).is_err()).collect();
    let mut who = vec![];
    for i in 0..N {
        let (x, y) = (&a.st[i], &b.st[i]);
        if x != y {
            let mut notes = vec![];
            if x.ep != y.ep {
                notes.push(format!("epoch {}->{}", x.ep, y.ep));
            }
            if x.role != y.role {
                notes.push(["follower", "candidate", "coordinator"][y.role as usize].to_string());
            }
            if x.vf != y.vf && y.vf != NONE {
                notes.push(format!("votes for {}", mname(y.vf)));
            }
            if x.votes != y.votes && y.votes != 0 {
                notes.push(format!("grants {{{}}}", mask_s(y.votes)));
            }
            if x.mi != y.mi && y.role == C {
                notes.push(format!("matchIndex {:?}", y.mi));
            }
            if x.up != y.up {
                notes.push(if y.up { "restarted".into() } else { "crashed".into() });
            }
            if notes.is_empty() {
                notes.push("state".into());
            }
            who.push(format!("{}: {}", mname(i as u8), notes.join(", ")));
        }
    }
    parts.extend(who);
    if !newm.is_empty() {
        parts.push(format!("sends {}", newm.iter().map(|m| msg_s(model, m)).collect::<Vec<_>>().join("; ")));
    }
    if let Some(e) = evs {
        if !e.is_empty() {
            parts.push(format!("=> {}", e.iter().map(|x| ev_s(model, x)).collect::<Vec<_>>().join("; ")));
        }
    } else {
        parts.push("(transition not re-derived)".into());
    }
    if b.pend != a.pend && b.pend.op != A_NONE {
        parts.push(format!("[step {} fires: {}]", b.stp, act_s(&b.pend, model)));
    }
    if b.down != a.down {
        let mut v = vec![];
        for x in 0..5u8 {
            for y in 0..5u8 {
                if b.down & link(x, y) != 0 {
                    v.push(format!("{}>{}", mname(x), mname(y)));
                }
            }
        }
        parts.push(format!("down: {}", if v.is_empty() { "none".into() } else { v.join(" ") }));
    }
    parts.join(" | ")
}

fn count_events(model: &Model, tr: &[State]) -> usize {
    let mut n = 0;
    for w in tr.windows(2) {
        let mut out = vec![];
        let mut info = Some(vec![]);
        model.succs(&w[0], &mut out, &mut info);
        if let Some((_, e, _)) = info.unwrap().iter().find(|(s, _, _)| *s == w[1]) {
            n += e.len();
        }
    }
    n
}

fn print_trace(model: &Model, tr: &[State], tag: &str) {
    println!("{}_LEN {} transitions, {} contract events", tag, tr.len() - 1, count_events(model, tr));
    for (k, w) in tr.windows(2).enumerate() {
        println!("{} {:3}. {}", tag, k + 1, describe(model, &w[0], &w[1]));
    }
    let last = tr.last().unwrap();
    for i in 0..N {
        let r = &last.st[i];
        println!("{} final {}{} {} ep={} ci={} cfg={{{}}} {}", tag, mname(i as u8), if r.up { "" } else { "(down)" },
                 ["follower", "candidate", "coordinator"][r.role as usize], r.ep, r.ci, mask_s(model.cfg(r)), jr_s(model, &r.jr));
    }
    for e in &last.elec {
        println!("{} elected e{} {} with {}", tag, e.0, mname(e.1), jr_s(model, &e.2));
    }
    for c in &last.comm {
        println!("{} committed idx {} {} by coordinator of e{}", tag, c.0, ent_s(model, c.1), c.2);
    }
}

// ------------------------------------------------------------------ scenario input
fn parse_model(path: &str, gated: bool, maxe: u8, maxt: u8, maxj: u8, settle: u16) -> Model {
    let text = std::fs::read_to_string(path).expect("scenario file");
    let mut init = 0u8;
    let mut steps = vec![];
    let mut cmd_names = vec!["noop".to_string()];
    for line in text.lines() {
        let line = line.trim();
        if line.is_empty() {
            continue;
        }
        let (kw, rest) = line.split_once(' ').unwrap_or((line, ""));
        match kw {
            "init" => init = rest.trim().parse().unwrap(),
            "cmds" => {
                for c in rest.split_whitespace() {
                    cmd_names.push(c.to_string());
                }
            }
            "step" => {
                let (t, a) = rest.split_once('|').unwrap();
                let mut tw = t.split_whitespace();
                let k = match tw.next().unwrap() {
                    "start" => EvK::Start,
                    "Elected" => EvK::Elected,
                    "Appended" => EvK::Appended,
                    "Truncated" => EvK::Truncated,
                    "Committed" => EvK::Committed,
                    "ConfigInEffect" => EvK::ConfigInEffect,
                    "ChangeRequested" => EvK::ChangeRequested,
                    "ChangeReplied" => EvK::ChangeReplied,
                    x => panic!("unknown event {}", x),
                };
                let mut f = vec![];
                for kv in tw {
                    let (k2, v) = kv.split_once('=').unwrap();
                    let fl = match k2 {
                        "member" => Fld::Member,
                        "index" => Fld::Index,
                        "epoch" => Fld::Epoch,
                        "kind" => Fld::Kind,
                        "op" => Fld::Op,
                        "target" => Fld::Target,
                        "status" => Fld::Status,
                        "from_index" => Fld::From,
                        x => panic!("unsupported trigger field {}", x),
                    };
                    f.push((fl, v.parse().unwrap()));
                }
                let mut sp = ActSpec { op: 0, t: NONE, at: NONE, cmd: 0, links: vec![] };
                for kv in a.split_whitespace() {
                    let (k2, v) = kv.split_once('=').unwrap();
                    match k2 {
                        "op" => sp.op = v.parse().unwrap(),
                        "t" => sp.t = v.parse().unwrap(),
                        "at" => sp.at = v.parse().unwrap(),
                        "cmd" => sp.cmd = v.parse().unwrap(),
                        "links" => {
                            for p in v.split(',').filter(|x| !x.is_empty()) {
                                let (x, y) = p.split_once(':').unwrap();
                                sp.links.push((x.parse().unwrap(), y.parse().unwrap()));
                            }
                        }
                        _ => panic!("bad action field"),
                    }
                }
                steps.push((Trig { k, f }, sp));
            }
            _ => panic!("bad line {}", line),
        }
    }
    Model { init, gated, maxe, maxt, maxj, settle, steps, cmd_names, fail_on: [true, true, true, true, false], prune: true, maxlost: 255, maxt_pre: maxt }
}

fn main() {
    let a: Vec<String> = std::env::args().collect();
    let get = |k: &str, d: &str| -> String {
        a.iter().position(|x| x == k).map(|i| a[i + 1].clone()).unwrap_or(d.to_string())
    };
    let path = &a[1];
    let gated = a[2] == "GATED";
    let maxe: u8 = get("--maxe", "3").parse().unwrap();
    let maxt: u8 = get("--maxt", "3").parse().unwrap();
    let maxj: u8 = get("--maxj", "3").parse().unwrap();
    let settle: u16 = get("--settle", "4").parse().unwrap();
    let threads: usize = get("--threads", "48").parse().unwrap();
    let bits: u32 = get("--bits", "30").parse().unwrap();
    let limit: u64 = get("--limit", "600").parse().unwrap();
    assert!((maxj as usize) < MAXJ_CAP);
    let mut m0 = parse_model(path, gated, maxe, maxt, maxj, settle);
    // which flags make a FAIL: contract clauses by default; J1.4(b') is diagnostic unless named
    let fl = get("--fail", "11,13,14a,14b");
    let keys = ["11", "13", "14a", "14b", "14k"];
    for k in 0..5 {
        m0.fail_on[k] = fl.split(',').any(|x| x == keys[k]);
    }
    m0.prune = !a.iter().any(|x| x == "--noprune");
    m0.maxlost = get("--maxlost", "255").parse().unwrap();
    m0.maxt_pre = get("--maxtpre", &maxt.to_string()).parse().unwrap();
    let model = Arc::new(m0);
    let t0 = Instant::now();
    let sh = explore(model.clone(), threads, bits, Duration::from_secs(limit));
    let secs = t0.elapsed().as_secs_f64();
    let distinct = sh.table.count.load(Ordering::Relaxed);
    let done = sh.done_states.load(Ordering::Relaxed);
    let reason = sh.reason.lock().unwrap().clone();
    let fail = sh.fail.lock().unwrap().take();
    let names = ["J1.1", "J1.3", "J1.4(a)", "J1.4(b)", "J1.4(b')"];
    println!("STATS distinct={} done_states={} seconds={:.1} exhausted={} reason={}", distinct, done, secs,
             fail.is_none() && reason.is_empty(), if reason.is_empty() { "-" } else { &reason });
    if let Some((tr, v)) = fail {
        let cl: Vec<&str> = (0..5).filter(|&k| v[k] && model.fail_on[k]).map(|k| names[k]).collect();
        println!("RESULT FAIL {}", cl.join(","));
        print_trace(&model, &tr, "TRACE");
    } else if !reason.is_empty() {
        println!("RESULT UNEXPLAINED bound");
    } else if done == 0 {
        println!("RESULT UNEXPLAINED steps");
    } else {
        println!("RESULT PASS");
    }
    let anyv = sh.anyviol.lock().unwrap().clone();
    for k in 0..5 {
        if let Some((tr, dn)) = &anyv[k] {
            println!("NOTE witnessed {} in a behaviour that {} taken every step{}", names[k],
                     if *dn { "has" } else { "had not (yet)" }, if model.fail_on[k] { "" } else { " (not a FAIL clause in this run)" });
            print_trace(&model, tr, &format!("WIT{}", k));
        }
    }
}
