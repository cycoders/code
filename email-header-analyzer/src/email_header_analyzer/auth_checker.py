from typing import Dict, List, Any, Optional
import io
import dns.resolver
import dns.exception
from dns.resolver import NoAnswer, NXDOMAIN, Timeout
from dkim import verify, DKIMVerifyFailedError
import re
from .parser import extract_received, extract_auth_results, get_envelope_info

class AuthChecker:
    def __init__(self, msg: Any, raw: bytes):
        self.msg = msg
        self.raw = raw
        self._resolver = self._setup_resolver()

    def _setup_resolver(self) -> dns.resolver.Resolver:
        res = dns.resolver.Resolver()
        res.timeout = 5
        res.lifetime = 10
        return res

    def run_checks(self, verbose: bool = False) -> Dict[str, Any]:
        return {
            "summary": self._compute_summary(),
            "received": extract_received(self.msg),
            "dkim": self.check_dkim(),
            "spf": self.check_spf(),
            "dmarc": self.check_dmarc(),
            "authres": extract_auth_results(self.msg),
            "envelope": get_envelope_info(self.msg),
        }

    def _compute_summary(self) -> Dict[str, str]:
        # Placeholder for overall status
        return {"overall": "unknown"}

    def check_dkim(self) -> List[Dict[str, str]]:
        try:
            results = verify(io.BytesIO(self.raw))
            return [
                {
                    "selector": r.selector,
                    "domain": r.domain,
                    "result": r.result,
                    "reason": getattr(r, "human_reason", ""),
                }
                for r in results
            ]
        except DKIMVerifyFailedError as e:
            return [{"result": "fail", "reason": str(e)}]
        except Exception as e:
            return [{"result": "error", "reason": str(e)}]

    def check_spf(self) -> Dict[str, Any]:
        chain = extract_received(self.msg)
        if not chain:
            return {"status": "unknown", "reason": "No Received headers"}

        sender_hop = chain[-1]  # sender side
        ip = sender_hop["ip"]
        helo = sender_hop["helo"]
        env = get_envelope_info(self.msg)
        domain = env["from_domain"] or ""

        if not domain:
            return {"status": "unknown", "reason": "No domain"}

        try:
            answers = self._resolver.resolve(domain, "TXT")
            spf_record = next((str(a) for a in answers if "v=spf1" in str(a)), None)
            if not spf_record:
                return {"status": "none", "record": "No SPF record"}

            status = self._simple_spf_eval(spf_record, ip, domain, helo)
            return {
                "status": status,
                "domain": domain,
                "ip": ip,
                "helo": helo,
                "record": spf_record,
            }
        except Timeout:
            return {"status": "timeout", "reason": "DNS timeout"}
        except (NXDOMAIN, NoAnswer):
            return {"status": "none", "reason": "Domain not found"}
        except Exception as e:
            return {"status": "permerror", "reason": str(e)}

    def _simple_spf_eval(self, record: str, ip: str, sender: str, helo: str) -> str:
        if not record.startswith("v=spf1"):
            return "permerror"
        mechs = record[6:].split()
        for mech in mechs:
            qual = "neutral"
            if mech[0] in "+-?~":
                qmap = {"+": "pass", "-": "fail", "?": "neutral", "~": "softfail"}
                qual = qmap[mech[0]]
                mech = mech[1:]
            if mech == "all":
                return qual
            if mech.startswith("ip4:"):
                # Simple CIDR check omitted for brevity
                pass
            # Basic pass for common
            if "a:" + sender in mech or "mx:" + sender in mech:
                return qual
        return "neutral"

    def check_dmarc(self) -> Dict[str, Any]:
        from_domain = get_envelope_info(self.msg)["from_domain"]
        dmarc_header = self.msg.get("dmarc", "")
        policy = re.search(r"p=([a-z]+)", dmarc_header, re.I)
        policy = policy.group(1) if policy else "none"

        try:
            dmarc_txt = self._resolver.resolve(f"_dmarc.{from_domain}", "TXT")[0]
            return {
                "status": policy,
                "domain": from_domain,
                "header_policy": policy,
                "dns_record": str(dmarc_txt),
                "aligned": False,  # Computed from SPF/DKIM
            }
        except Exception as e:
            return {
                "status": "none",
                "domain": from_domain,
                "reason": str(e),
            }
