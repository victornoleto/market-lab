"""Smoke tests for DOWNLOAD-DATA.md HTML parsers.

No network. Validates the exact structures described in the task: catalog
`content-row`, system `#infoStats`, normal trade rows and deposit rows.
"""
from __future__ import annotations

import sys

from . import catalog, parser, system_info


CATALOG_HTML = """
<div class="content-row has-actions">
  <div class="grid-table-cell display-flex flex-column gap-5">
    <a href="https://www.myfxbook.com/members/HappyForex/old-happy-forex-v241-real/1152318" class="bold break-word width-100-percentage">
      OLD Happy Forex v2.4.1 - REAL (FortFS- set 3)
    </a>
    <div><div class="system-info-mini-boxes real">Real</div><div class="system-info-mini-boxes">1:500</div><div class="system-info-mini-boxes mobile-hidden">MetaTrader 4</div></div>
  </div>
  <div class="grid-table-cell"><span class="green">+154.03%</span></div>
  <div class="grid-table-cell">23.70%</div>
</div>
"""

SYSTEM_HTML = """
<div class="portfolio-resolve-account-type"><span>Real (USD), <a class="underline" href="/reviews/brokers/x">Fort Financial Services</a>, Technical , Automated , 1:500 , MetaTrader 4</span></div>
<div class="tab-pane active" id="infoStats"><table><tbody>
<tr><td><span><b class="dotted">Gain :</b></span></td><td><span><b><span class="green">+154.03%</span></b></span></td></tr>
<tr><td><span class="dotted"> Abs. Gain: </span></td><td><span><span class="green">+117.81%</span></span></td></tr>
<tr><td>Drawdown:</td><td><span>23.70% </span></td></tr>
<tr><td>Balance:</td><td><span><span id="statsBalance">$3,415.33</span></span></td></tr>
</tbody></table></div>
"""

HISTORY_HTML = """
<table id="tradingHistoryTable"><tbody>
<tr class="commentRow" data-record="11558090443" data-accountoid="1152318">
<td></td><td class="brokerTime">05.31.2021 03:33</td><td style="display:none" class="userTime">05.30.2021 22:33</td>
<td class="brokerTime">06.01.2021 02:31</td><td style="display:none" class="userTime">05.31.2021 21:31</td>
<td class="symbol" accountOid="1152318" openTime="1622431980000" closeTime="1622514660000"><a class="symbolName">AUDUSD</a></td>
<td>Buy</td><td>0.01</td><td>0.77041</td><td>0.77451</td><td><span class="green">41.0</span></td><td class="green">4.10</td><td>22h 58m</td><td><span class="green">0.12%</span></td><td class="sparkline">-</td><td></td>
</tr>
<tr class="commentRow orange" data-record="787028189" data-accountoid="1152318">
<td></td><td class="brokerTime">01.05.2015 11:32</td><td style="display:none" class="userTime">01.05.2015 06:32</td>
<td class="brokerTime"></td><td style="display:none" class="userTime"></td>
<td class="symbol" accountOid="1152318" openTime="1420457520000" closeTime="1420457520000"></td>
<td>Deposit</td><td></td><td></td><td></td><td></td><td class="green">1,068.00</td><td></td><td></td><td class="sparkline"></td><td></td>
</tr>
</tbody></table>
"""


def main() -> int:
    entries = catalog.parse_catalog_html(CATALOG_HTML)
    assert len(entries) == 1
    assert entries[0].system_id == 1152318
    assert entries[0].account_type == "Real"
    assert entries[0].leverage == "1:500"
    assert entries[0].platform == "MetaTrader 4"
    assert entries[0].gain_pct == 154.03
    assert entries[0].drawdown_pct == 23.70

    info = system_info.parse_system_info_html(SYSTEM_HTML, system_id=1152318)
    assert info["stats"]["gain"] == "+154.03%"
    assert info["stats"]["absolute_gain"] == "+117.81%"
    assert info["account"]["account_type"] == "Real"
    assert info["account"]["leverage"] == "1:500"

    df = parser.parse_history_html(HISTORY_HTML)
    assert len(df) == 2
    trade = df[df["is_trade"]].iloc[0]
    assert trade["symbol"] == "AUDUSD"
    assert trade["action"] == "Buy"
    assert trade["lots"] == 0.01
    assert trade["pips"] == 41.0
    assert trade["profit"] == 4.10
    assert trade["pct"] == 0.0012
    cash = df[~df["is_trade"]].iloc[0]
    assert cash["action"] == "Deposit"
    assert cash["profit"] == 1068.00
    print("PASS — DOWNLOAD-DATA HTML parser smoke")
    return 0


if __name__ == "__main__":
    sys.exit(main())
