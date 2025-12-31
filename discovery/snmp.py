from typing import Optional, Dict
import asyncio

from pysnmp.carrier.asyncio.dispatch import AsyncioDispatcher
from pysnmp.carrier.asyncio.dgram import udp
from pysnmp.proto import api
from pyasn1.codec.ber import encoder, decoder
from pysnmp.proto.rfc1905 import ResponsePDU


SYS_NAME = "1.3.6.1.2.1.1.5.0"
SYS_DESCR = "1.3.6.1.2.1.1.1.0"


def snmp_fingerprint(
    ip: str,
    community: str = "public",
    timeout: int = 2,
) -> Optional[Dict]:

    # 🔥 بسیار مهم: ساخت event loop مخصوص این thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    result = {}

    try:
        pMod = api.PROTOCOL_MODULES[api.SNMP_VERSION_2C]

        reqPDU = pMod.GetRequestPDU()
        pMod.apiPDU.set_defaults(reqPDU)
        pMod.apiPDU.set_varbinds(
            reqPDU,
            [(SYS_NAME, pMod.Null("")), (SYS_DESCR, pMod.Null(""))],
        )

        reqMsg = pMod.Message()
        pMod.apiMessage.set_defaults(reqMsg)
        pMod.apiMessage.set_community(reqMsg, community)
        pMod.apiMessage.set_pdu(reqMsg, reqPDU)

        def cbRecvFun(
            transportDispatcher, transportDomain, transportAddress, wholeMsg
        ):
            nonlocal result

            while wholeMsg:
                rspMsg, wholeMsg = decoder.decode(
                    wholeMsg, asn1Spec=pMod.Message()
                )
                rspPDU: ResponsePDU = pMod.apiMessage.get_pdu(rspMsg)

                if (
                    pMod.apiPDU.get_request_id(reqPDU)
                    == pMod.apiPDU.get_request_id(rspPDU)
                ):
                    if pMod.apiPDU.get_error_status(rspPDU):
                        transportDispatcher.job_finished(1)
                        return wholeMsg

                    for oid, val in pMod.apiPDU.get_varbinds(rspPDU):
                        result[str(oid)] = str(val)

                    transportDispatcher.job_finished(1)

            return wholeMsg

        transportDispatcher = AsyncioDispatcher()
        transportDispatcher.register_recv_callback(cbRecvFun)

        transportDispatcher.register_transport(
            udp.DOMAIN_NAME,
            udp.UdpAsyncioTransport().open_client_mode(),
        )

        transportDispatcher.send_message(
            encoder.encode(reqMsg),
            udp.DOMAIN_NAME,
            (ip, 161),
        )

        transportDispatcher.job_started(1)
        transportDispatcher.run_dispatcher(timeout)
        transportDispatcher.close_dispatcher()

    finally:
        pending = asyncio.all_tasks(loop)
        for task in pending:
            task.cancel()

        if pending:
            loop.run_until_complete(
                asyncio.gather(*pending, return_exceptions=True)
                )

        loop.stop()
        loop.close()

    if not result:
        return None

    return {
        "ip": ip,
        "hostname": result.get(SYS_NAME),
        "description": result.get(SYS_DESCR),
    }

